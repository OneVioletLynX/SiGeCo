import os
import pymysql

# 🔧 CONFIGURACIÓN — ajustá estos valores:
DB_NAME = "sigecodb"
DB_USER = "root"
DB_PASS = "1234"
DB_HOST = "localhost"
DB_PORT = 3306
OUTPUT_FILE = "backup.sql"

# 📦 Conexión
conn = pymysql.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASS,
    database=DB_NAME,
    port=DB_PORT,
    charset="utf8mb4"
)

cursor = conn.cursor()

# 📜 Obtiene todas las tablas
cursor.execute("SHOW TABLES;")
tables = [row[0] for row in cursor.fetchall()]

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(f"-- Backup completo de la base `{DB_NAME}`\n\n")
    f.write("SET FOREIGN_KEY_CHECKS = 0;\n\n")

    for table in tables:
        print(f"Exportando tabla: {table}...")
        f.write(f"-- Tabla `{table}`\n\n")

        # 🔹 Estructura
        cursor.execute(f"SHOW CREATE TABLE {table}")
        create_stmt = cursor.fetchone()[1]
        f.write(f"{create_stmt};\n\n")

        # 🔹 Datos
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        if not rows:
            continue

        columns = [desc[0] for desc in cursor.description]
        for row in rows:
            values = []
            for val in row:
                if val is None:
                    values.append("NULL")
                elif isinstance(val, (int, float)):
                    values.append(str(val))
                else:
                    values.append("'" + str(val).replace("'", "''") + "'")
            insert_stmt = f"INSERT INTO `{table}` ({', '.join(columns)}) VALUES ({', '.join(values)});\n"
            f.write(insert_stmt)
        f.write("\n\n")
    f.write("SET FOREIGN_KEY_CHECKS = 1;\n")

conn.close()
print(f"✅ Backup completo generado: {OUTPUT_FILE}")
