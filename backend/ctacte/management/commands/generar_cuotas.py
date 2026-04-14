from django.core.management.base import BaseCommand
from ctacte.services import generar_cuotas_mes, MESES_CICLO


class Command(BaseCommand):

    help = "Genera las cuotas del mes actual (o del mes/año indicado) para todos los alumnos activos"

    def add_arguments(self, parser):
        # CORRECCIÓN: permite generar cuotas de meses anteriores o futuros
        # para correcciones manuales. Uso: py manage.py generar_cuotas --mes 3 --anio 2025
        parser.add_argument(
            '--mes',
            type=int,
            help='Número de mes a generar (3-12). Por defecto: mes actual.',
        )
        parser.add_argument(
            '--anio',
            type=int,
            help='Año a generar. Por defecto: año actual.',
        )

    def handle(self, *args, **options):

        mes  = options.get('mes')
        anio = options.get('anio')

        if mes and mes not in MESES_CICLO:
            self.stdout.write(
                self.style.ERROR(f"El mes {mes} está fuera del ciclo académico (marzo=3 a diciembre=12).")
            )
            return

        resultado = generar_cuotas_mes(anio=anio, mes=mes)

        if "motivo" in resultado:
            self.stdout.write(self.style.WARNING(resultado["motivo"]))
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Cuotas generadas: {resultado['generadas']}")
            )