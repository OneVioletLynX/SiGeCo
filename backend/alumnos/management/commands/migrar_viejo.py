"""
Migra los datos del sistema viejo (Excel exportado de SQL Server) al esquema
nuevo de SiGeCo. Ver conversación con el usuario para el detalle de cada
decision (fusion de DNI duplicados, mapeo ciudad->Localidad, que conceptos de
CTACTE se migran, etc.) - este comando implementa esas decisiones tal como
fueron acordadas.

Uso:
    python manage.py migrar_viejo --excel "C:\\ruta\\base_de_datos.xlsx"
    python manage.py migrar_viejo --excel "..." --dry-run
"""
import re
import unicodedata
import datetime

import pandas as pd
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from alumnos.models import Alumno
from carreras.models import Carrera, CarreraCursada, Estado
from ctacte.models import MesPago, MetodoPago, Cuota, EstadoCuota, Pago, PagoDetalle
from valores.models import Concepto, Valor
from geografia.models import Localidad


# ---------------------------------------------------------------------------
# Mapeo ciudad (texto libre del Excel) -> id_loc de geografia_localidad.
# Construido a partir de las 73 ciudades unicas del Excel: se normaliza
# (mayusculas, sin tildes, abreviaturas expandidas) y se busca la localidad
# correcta. Los casos ambiguos (localidades con el mismo nombre en mas de una
# provincia) fueron fijados a Cordoba a pedido del usuario.
# ---------------------------------------------------------------------------
CIUDAD_ID_LOC = {
    "AMSTRONG": 11696, "ARMSTRONG": 11696, "BALLESTEROS": 4616,
    "BEL VILLE": 4618, "BELL VILE": 4618, "BELL VILLE": 4618, "BELLVILLE": 4618,
    "BOUQUET": 11714, "BOUQUET SANTA FE": 12099, "CAMILO ALDAO": 3607,
    "CANADA DE GOMEZ": 12069, "CARLOS PELLEGRINI SANTA FE": 12546,
    "CHANAR LADEADO": 11739, "CORRAL DE BUSTOS": 3613, "CORREA": 12064,
    "CRUZ ALTA": 3614, "EL FORTIN": 4268, "GENERA ROCA": 3616,
    "GENERAL BALDISERA": 3615, "GENERAL BALDISSERA": 3615, "GENERAL ROCA": 3616,
    "GODEKEN": 11737, "GUATIMOZIN": 3617, "HERNANDO": 4469, "INRIVILLE": 3618,
    "ISLA VERDE": 3619, "JUSTINIANO POSSE": 4626, "KEONES": 3620,
    "LAS ROSAS": 11693, "LEONES": 3620, "LOS SURGENTES": 3621,
    "MAARCOS JUAREZ": 3622, "MARCOS JUAEREZ": 3622, "MARCOS JUANEZ": 3622,
    "MARCOS JUAREZ": 3622, "MJUAREZ": 3622, "MONTE BUEY": 3623,
    "MONTE LENA": 4628, "MONTE MAIZ": 4629, "MORRISON": 4630,
    "NOETIGER": 4631, "NOETINGER": 4631, "ORDONES": 4632, "ORDONEZ": 4632,
    "SAIRA": 3624, "SAN MARCOS": 4637, "SAN MARCOS SUD": 4637,
    "TORTUGAS": 11713, "TORTUGAS SANTA FE": 11713, "VIAMONTE": 4639,
    "VILLA MARIA": 3491, "VILLADA": 11736,
}

_ABBR = {
    r"\bGRAL\.?\b": "GENERAL", r"\bSTA\.?\b": "SANTA", r"\bSTO\.?\b": "SANTO",
    r"\bCDA\.?\b": "CANADA", r"\bC\.\s*ALDAO\b": "CAMILO ALDAO",
    r"\bC\.\s*ALTA\b": "CRUZ ALTA",
    r"\bC\.\s*DE BUSTOS\b": "CORRAL DE BUSTOS", r"\bCORRA DE BUSTOS\b": "CORRAL DE BUSTOS",
    r"\bMS[\.\-]?\s*JZ\.?A?\d*[\-\d]*\b": "MARCOS JUAREZ",
    r"\bMZ\.?\s*JZ\.?\b": "MARCOS JUAREZ",
}


def normalize_ciudad(s):
    s = str(s).replace("�", "")
    nfkd = unicodedata.normalize("NFKD", s)
    s = "".join(c for c in nfkd if not unicodedata.combining(c)).upper().strip()
    for pat, repl in _ABBR.items():
        s = re.sub(pat, repl, s)
    s = re.sub(r"[.\-]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def resolver_localidad(ciudad_raw):
    if ciudad_raw is None or (isinstance(ciudad_raw, float) and pd.isna(ciudad_raw)):
        return None
    return CIUDAD_ID_LOC.get(normalize_ciudad(ciudad_raw))


# ---------------------------------------------------------------------------
# Correcciones manuales de nombre/apellido (casos de apellido compuesto que
# la heuristica simple -primera palabra = apellido- separaria mal). Provistas
# por el usuario tras revisar el listado de casos con 3+ palabras.
# ---------------------------------------------------------------------------
NOMBRE_CORRECCIONES = {
    4: ("Amarilla Ramirez", "Eliana"), 58: ("Ciccarelli Grabemvarter", "Cristian"),
    64: ("Celis Giletta", "Luisina"), 75: ("Celis", "Maria Agustina"),
    78: ("Cagliero", "Maria Celeste"), 89: ("Distel Rodriguez", "Leonardo"),
    90: ("De Arma", "Jimena"), 93: ("De Giorgi", "Nicolas"),
    96: ("Di Napoli", "Leandro"), 99: ("Di Pietro", "Micaela Fernanda"),
    101: ("Del Bosco", "Deysi"), 104: ("De La Mata", "Francisco"),
    112: ("Escobedo", "Maria Alejandra"), 141: ("Garmendia", "Maria Antonella"),
    146: ("Garmendia", "Maria Andreina"), 165: ("Lerda", "Maria Emilia"),
    224: ("Pazos Sverko", "Marcos Rodolfo"), 228: ("Peralta", "Maria Celeste"),
    287: ("Saco Robul", "Gabriel Matias"), 330: ("Celis Sanzotti", "Maria Jose"),
    351: ("Soria Oviedo", "Genesis"), 410: ("Maero", "Torres Cecilia"),
    422: ("De Ricco", "Agustin"), 428: ("Ruveda Ferreyra", "Virginia"),
    468: ("Farias Lopez", "Facundo"), 486: ("Rosso Lloret", "Jose Francisco"),
    559: ("Rosso Lloret", "Jose Francisco"), 480: ("Perazzo Lingua", "Mauro Javier"),
    507: ("Vilchez Bazan", "Flaviana"), 518: ("De Arma", "Helen"),
    547: ("Collura Verdenelli", "Melquiades"), 555: ("Flores Torrez", "Maria Antonella"),
    583: ("Della Libera", "Ramiro"), 599: ("Longo Garrido", "Alesandro"),
    605: ("Barbon Perez", "Rocio"), 632: ("Martinez Aguilar", "Carolina Claudia"),
    635: ("Martinez Posco", "Maria Belen"), 669: ("Bosio Capra", "Agustin"),
    721: ("Della Ceca", "Sofia"), 723: ("Tovar Telmo", "Adriano"),
    752: ("Cornaglia", "Maria Monserrat"), 762: ("Loste Tolomei", "Maria Del Rosario"),
    779: ("Cardozo Rodriguez", "Mariana"), 782: ("De Los Santos", "Micaela"),
    784: ("Fernandez Barda", "Maria Victoria"), 791: ("Olea Figueroa", "Irina"),
    802: ("Villa", "Maria De Los Angeles"), 832: ("Moraes Pires", "Eliana"),
    839: ("Porporato Fratoni", "Facundo"), 856: ("Cavallero", "Juan Pablo"),
    882: ("Di Marco", "Josefina"), 904: ("Roche Gutierrez", "Rocio"),
    906: ("Molinengo Cuello", "Joaquin"), 918: ("Del Arco", "Gabriel"),
    921: ("Bustos Osuna", "Paola"), 932: ("Rodriguez Busquets", "Matias Jose"),
    943: ("Krawinkel Tinari", "Katherina"), 950: ("Barrios Gatti", "Camila"),
    960: ("Gala Taborda", "Tomas"), 1985: ("Luna Ruiz", "Miyen Uriel"),
    2001: ("Silva Saldanez", "Oriana"), 2012: ("Marveggio Carmona", "Sofia Nyra"),
    2035: ("De La Mata", "Ignacio"), 2052: ("Santa Cruz", "Ariana"),
    2054: ("Cordoba Movio", "Candela Maria"), 2072: ("Menghi Baleani", "Dolores"),
    2073: ("Menghi Baleani", "Dolores"), 2075: ("Pessuto Aguero", "Victoria"),
    2095: ("Ramirez Dana", "Agustina"), 2101: ("Murua Jercovich", "Mariana"),
    2122: ("Rodriguez Brouwer", "Eugenia"), 2125: ("Rosso Cavallazzi", "Maria Emilia"),
    2133: ("Espindola", "Maria"), 2140: ("Mare Godino", "Camila"),
    2148: ("D Andrea", "Romina Sol"), 2157: ("Murua Diaz", "Daniel Ignacio"),
    2159: ("Gorosito Panero", "Abril Delfina"), 2163: ("Martinez Dupuy", "Avril"),
    2180: ("Lujan Berto", "Valentin"), 2207: ("Barreto Dassie", "David"),
    2257: ("Peretti Fucili", "Pedro"), 2264: ("Molina Romero", "Ileana"),
    2266: ("Lezcano Bolcato", "Catalina"), 2276: ("Tulian Centeno", "Lucas Alejandro"),
    2288: ("Aguilar Tarantola", "Paula"), 2292: ("Cepeda Lancioni", "Camila"),
    2302: ("Dellia Santina", "Carolina"), 2308: ("Gonzalez Neira", "Fausto"),
    2311: ("Varas Moyano", "Aitana"), 2317: ("Roche Gutierrez", "Agustina"),
    2321: ("Gutierrez Pratti", "Daviana"), 2338: ("Trejo Pucciarelli", "Gabriel"),
    2340: ("Molina Di Natale", "Trinidad Esther"), 2365: ("Perez Butler", "Alvaro"),
    2422: ("Van Den Brager", "Helga"), 2427: ("Ardid Rubbino", "Paula"),
    2430: ("Della Maggiora", "Martin"), 2446: ("Boscolo Valinotti", "Malena"),
}


# DNIs que coinciden entre dos filas con nombres totalmente distintos (no son
# la misma persona reinscripta, sino un DNI mal tipeado): no se fusionan.
DNI_NO_FUSIONAR = {37172312}


def split_nombre(id_alumno, nombre_raw):
    if id_alumno in NOMBRE_CORRECCIONES:
        return NOMBRE_CORRECCIONES[id_alumno]
    n = str(nombre_raw).strip()
    if "," in n:
        ap, nom = n.split(",", 1)
        return ap.strip().title(), nom.strip().title()
    partes = n.split()
    apellido = partes[0].title()
    nombre = " ".join(partes[1:]).title() if len(partes) > 1 else ""
    return apellido, nombre


def clean_dni(raw):
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None
    digits = re.sub(r"\D", "", str(raw))
    return int(digits) if digits else None


def parse_direccion(raw):
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None, None
    raw = str(raw).strip()
    if not raw:
        return None, None
    m = re.match(r"^(.*?)\s*(\d+)\s*$", raw)
    if m:
        calle = m.group(1).strip().rstrip(",").strip()
        return (calle or None), int(m.group(2))
    return raw, None


def parse_telefono(raw):
    if raw is None or (isinstance(raw, float) and pd.isna(raw)):
        return None, None
    digits = re.sub(r"\D", "", str(raw))
    if not digits:
        return None, None
    if len(digits) <= 7:
        return None, int(digits)
    if len(digits) >= 11:
        return None, None  # dato sucio (ej. telefono pegado a otro campo), no confiar
    return int(digits[:-6]), int(digits[-6:])


class Command(BaseCommand):
    help = "Migra alumnos, cursadas, cuotas, pagos y valores desde el Excel del sistema viejo"

    def add_arguments(self, parser):
        parser.add_argument("--excel", required=True, help="Ruta al archivo base_de_datos.xlsx")
        parser.add_argument("--dry-run", action="store_true", help="No escribe en la base, solo reporta")

    def handle(self, *args, **options):
        excel_path = options["excel"]
        dry_run = options["dry_run"]

        try:
            xls = pd.ExcelFile(excel_path)
        except Exception as exc:
            raise CommandError(f"No pude abrir el Excel: {exc}")

        al = xls.parse("ALUMNO")
        ct = xls.parse("CTACTE")
        va = xls.parse("VALOR")

        # Al crear CarreraCursada existe una signal (carreras/signals.py)
        # pensada para altas manuales que genera una cuota fantasma de
        # "Enero, importe=0, Pendiente". Para una migracion masiva de datos
        # historicos esto genera filas de mas y puede tapar una cuota real
        # de enero con esa version vacia (get_or_create no pisa lo existente).
        # Se desconecta durante la migracion y se reconecta al finalizar.
        from django.db.models.signals import post_save
        from carreras.models import CarreraCursada
        from carreras.signals import generar_cuota_inscripcion
        post_save.disconnect(generar_cuota_inscripcion, sender=CarreraCursada)
        try:
            with transaction.atomic():
                self._migrar_alumnos(al, ct, dry_run)
                self._migrar_ctacte(al, ct, dry_run)
                self._migrar_valores(va, dry_run)
                if dry_run:
                    self.stdout.write(self.style.WARNING("dry-run: haciendo rollback de todo"))
                    transaction.set_rollback(True)
        finally:
            post_save.connect(generar_cuota_inscripcion, sender=CarreraCursada)

    # ------------------------------------------------------------------
    def _migrar_alumnos(self, al, ct, dry_run):
        estado_por_id = {e.id_estado: e for e in Estado.objects.all()}
        mes_min_por_alumno = (
            ct.groupby("ID_ALUMNO")["ANO"].min().to_dict()
        )

        # agrupar por DNI (no nulo) para fusionar duplicados
        grupos = {}
        sin_dni = []
        dni_conflictivo_visto = set()
        for _, row in al.iterrows():
            dni = clean_dni(row["DNI"])
            if dni in DNI_NO_FUSIONAR:
                # nombres totalmente distintos con el mismo DNI: no es la misma
                # persona. Se tratan como alumnos separados; solo el primero
                # conserva el DNI (no puede haber dos con el mismo, es unico).
                if dni in dni_conflictivo_visto:
                    row = row.copy()
                    row["DNI"] = None
                else:
                    dni_conflictivo_visto.add(dni)
                sin_dni.append(row)
            elif dni is None:
                sin_dni.append(row)
            else:
                grupos.setdefault(dni, []).append(row)

        self.old_id_to_alumno = {}
        self.old_id_to_carrera = {}
        creados = 0
        legajos_usados = set()
        legajos_repetidos = []
        emails_usados = set()
        emails_repetidos = []

        def crear_alumno_y_cursadas(filas):
            nonlocal creados
            # primaria = preferir una fila con correccion manual de nombre ya
            # revisada por el usuario; si no hay, la de mas campos completos
            # (empate -> mayor ID_ALUMNO)
            def score(r):
                tiene_correccion = int(r["ID_ALUMNO"]) in NOMBRE_CORRECCIONES
                campos = [r["CIUDAD"], r["DIRECCION"], r["TELEFONO"], r["MAIL"], r["NOTAS"]]
                completitud = sum(0 if pd.isna(c) else 1 for c in campos)
                return (tiene_correccion, completitud, r["ID_ALUMNO"])

            primaria = max(filas, key=score)
            apellido, nombre = split_nombre(int(primaria["ID_ALUMNO"]), primaria["NOMBRE"])
            direccion, numero = parse_direccion(primaria["DIRECCION"])
            prefijo, telefono = parse_telefono(primaria["TELEFONO"])
            id_loc = resolver_localidad(primaria["CIUDAD"])
            dni = clean_dni(primaria["DNI"])
            email = None if pd.isna(primaria["MAIL"]) else str(primaria["MAIL"]).strip().lower()
            if email is not None:
                if email in emails_usados:
                    emails_repetidos.append((int(primaria["ID_ALUMNO"]), email))
                    email = None
                else:
                    emails_usados.add(email)

            legajo = str(primaria["LEGAJO"])
            if legajo in legajos_usados:
                legajos_repetidos.append((int(primaria["ID_ALUMNO"]), legajo))
                legajo = f"{legajo}-DUP{int(primaria['ID_ALUMNO'])}"
            legajos_usados.add(legajo)

            alumno = Alumno(
                legajo=legajo,
                nombre=nombre or "",
                apellido=apellido or "",
                fecha_nacimiento=None,
                dni=dni,
                ciudad_id=id_loc,
                direccion=direccion,
                numero=numero,
                prefijo=prefijo,
                telefono=telefono,
                email=email,
            )
            if not dry_run:
                alumno.save()
            creados += 1

            for r in filas:
                old_id = int(r["ID_ALUMNO"])
                self.old_id_to_alumno[old_id] = alumno
                self.old_id_to_carrera[old_id] = int(r["ID_CARRERA"])

                anio_ingreso = mes_min_por_alumno.get(old_id)
                if anio_ingreso is None or pd.isna(anio_ingreso):
                    anio_ingreso = pd.Timestamp(r["INSCRIPCION"]).year
                anio_ingreso = int(anio_ingreso)

                if not dry_run:
                    CarreraCursada.objects.get_or_create(
                        alumno=alumno,
                        carrera_id=int(r["ID_CARRERA"]),
                        defaults={
                            "id_estado": estado_por_id[int(r["ID_ESTADO"])],
                            "anio_ingreso": anio_ingreso,
                        },
                    )

        for filas in grupos.values():
            crear_alumno_y_cursadas(filas)
        for row in sin_dni:
            crear_alumno_y_cursadas([row])

        self.stdout.write(self.style.SUCCESS(
            f"Alumnos creados: {creados} (de {len(al)} filas originales, "
            f"{sum(1 for f in grupos.values() if len(f) > 1)} grupos de DNI duplicado fusionados)"
        ))
        if legajos_repetidos:
            self.stdout.write(self.style.WARNING(
                f"Legajos repetidos en el Excel (no relacionado a DNI duplicado), "
                f"se les agrego un sufijo para poder migrarlos: {legajos_repetidos}"
            ))
        if emails_repetidos:
            self.stdout.write(self.style.WARNING(
                f"Emails repetidos entre alumnos distintos (probablemente un mail "
                f"familiar compartido), se dejo en null en el segundo alumno: {emails_repetidos}"
            ))

    # ------------------------------------------------------------------
    def _migrar_ctacte(self, al, ct, dry_run):
        # MesPago id=13 representa "Inscripcion" (sin mes real, MES=0 en el
        # Excel). No se uso id=0 porque Django rechaza 0 como valor de
        # cualquier campo que apunte a un AutoField.
        MES_INSCRIPCION = 13
        mes_obj = {m.id_mes: m for m in MesPago.objects.all()}

        def mes_fk(mes):
            return mes_obj[MES_INSCRIPCION if mes == 0 else mes]

        estado_cuota = {e.descripcion: e for e in EstadoCuota.objects.all()}
        concepto_obj = {c.id_concepto: c for c in Concepto.objects.all()}
        metodo_no_esp = MetodoPago.objects.get(descripcion="No especificado")
        hoy = datetime.date.today()

        cargos = ct[ct["ID_CONCEPTO"].isin([1, 4])]
        pagos_rows = ct[ct["ID_CONCEPTO"] == 5]

        pagado_set = set(
            zip(pagos_rows["ID_ALUMNO"], pagos_rows["ANO"], pagos_rows["MES"])
        )
        importe_cargo = {
            (int(r["ID_ALUMNO"]), int(r["ANO"]), int(r["MES"])): float(r["DEBE"])
            for _, r in cargos.iterrows()
        }

        cuotas_creadas = 0
        cuotas_omitidas = 0
        vistos = set()
        for _, r in cargos.iterrows():
            old_id = int(r["ID_ALUMNO"])
            alumno = self.old_id_to_alumno.get(old_id)
            if alumno is None:
                continue
            carrera_id = self.old_id_to_carrera[old_id]
            mes = int(r["MES"])
            anio = int(r["ANO"])
            key = (alumno.pk if not dry_run else old_id, carrera_id, mes, anio)
            if key in vistos:
                cuotas_omitidas += 1
                continue
            vistos.add(key)

            pagada = (old_id, anio, mes) in pagado_set
            due = datetime.date(anio, mes if mes >= 1 else 1, 1)
            if pagada:
                estado = estado_cuota["Pagada"]
            elif due < hoy:
                estado = estado_cuota["Vencida"]
            else:
                estado = estado_cuota["Pendiente"]

            if not dry_run:
                Cuota.objects.get_or_create(
                    alumno=alumno,
                    carrera_id=carrera_id,
                    mes=mes_fk(mes),
                    anio=anio,
                    defaults={"estado": estado, "importe": r["DEBE"]},
                )
            cuotas_creadas += 1

        pagos_creados = 0
        for _, r in pagos_rows.iterrows():
            old_id = int(r["ID_ALUMNO"])
            alumno = self.old_id_to_alumno.get(old_id)
            if alumno is None:
                continue
            carrera_id = self.old_id_to_carrera[old_id]
            mes = int(r["MES"])
            anio = int(r["ANO"])
            concepto_id = 4 if mes == 0 else 1
            importe_detalle = importe_cargo.get((old_id, anio, mes), float(r["HABER"]))

            if not dry_run:
                # importe_total = precio real de la cuota (sin el recargo del
                # concepto 2, que se descarta); el HABER original del Excel
                # puede incluir ese recargo pero no se cuenta.
                pago = Pago.objects.create(
                    id_alumno=alumno,
                    fecha_pago=pd.to_datetime(r["FECHA"]),
                    importe_total=importe_detalle,
                    id_metodo_pago=metodo_no_esp,
                )
                PagoDetalle.objects.get_or_create(
                    pago=pago,
                    carrera_id=carrera_id,
                    mes=mes_fk(mes),
                    anio_pago=anio,
                    defaults={
                        "id_concepto": concepto_obj[concepto_id],
                        "importe": importe_detalle,
                    },
                )
            pagos_creados += 1

        self.stdout.write(self.style.SUCCESS(
            f"Cuotas creadas: {cuotas_creadas} (omitidas por duplicado: {cuotas_omitidas}) | "
            f"Pagos creados: {pagos_creados}"
        ))

    # ------------------------------------------------------------------
    def _migrar_valores(self, va, dry_run):
        creados = 0
        for _, r in va.iterrows():
            fecha_fin = None if pd.isna(r["HASTA"]) else pd.to_datetime(r["HASTA"]).date()
            if not dry_run:
                Valor.objects.create(
                    id_carrera_id=int(r["ID_CARRERA"]),
                    id_concepto_id=int(r["ID_CONCEPTO"]),
                    fecha_inicio=pd.to_datetime(r["DESDE"]).date(),
                    fecha_fin=fecha_fin,
                    importe=r["IMPORTE"],
                )
            creados += 1
        self.stdout.write(self.style.SUCCESS(f"Valores creados: {creados}"))
