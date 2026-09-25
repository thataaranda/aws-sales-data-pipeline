import csv
import io
from collections import defaultdict
from decimal import Decimal, InvalidOperation

import boto3


BUCKET = "ventas-portfolio-thalita-483729"
PREFIJO_ENTRADA = "tienda/ventas/"
ARCHIVO_SALIDA = "procesado/resumen_por_categoria.csv"

s3 = boto3.client("s3")


def obtener_archivos_csv():
    archivos = []
    paginador = s3.get_paginator("list_objects_v2")

    for pagina in paginador.paginate(Bucket=BUCKET, Prefix=PREFIJO_ENTRADA):
        for objeto in pagina.get("Contents", []):
            if objeto["Key"].lower().endswith(".csv") and objeto["Size"] > 0:
                archivos.append(objeto["Key"])

    if not archivos:
        raise ValueError(
            f"No encontré archivos CSV en s3://{BUCKET}/{PREFIJO_ENTRADA}"
        )

    return archivos


def procesar_ventas():
    resumen = defaultdict(
        lambda: {"cantidad_ventas": 0, "unidades": 0, "monto_total": Decimal("0")}
    )
    filas_procesadas = 0

    for nombre_archivo in obtener_archivos_csv():
        respuesta = s3.get_object(Bucket=BUCKET, Key=nombre_archivo)
        contenido = respuesta["Body"].read().decode("utf-8-sig")
        lector = csv.reader(io.StringIO(contenido))

        for numero_fila, columnas in enumerate(lector, start=1):
            if not columnas or all(not valor.strip() for valor in columnas):
                continue

            # DMS exportó el CSV sin encabezados, en este orden:
            # id_venta, fecha, categoria, producto, cantidad, precio_unitario
            if len(columnas) != 6:
                raise ValueError(
                    f"{nombre_archivo}, fila {numero_fila}: "
                    f"esperaba 6 columnas y encontré {len(columnas)}"
                )

            id_venta, fecha, categoria, producto, cantidad, precio_unitario = [
                valor.strip() for valor in columnas
            ]

            try:
                unidades = int(cantidad)
                precio = Decimal(precio_unitario)
            except (ValueError, InvalidOperation) as error:
                raise ValueError(
                    f"{nombre_archivo}, fila {numero_fila}: "
                    "cantidad o precio no válido"
                ) from error

            if not categoria:
                raise ValueError(
                    f"{nombre_archivo}, fila {numero_fila}: categoría vacía"
                )

            resumen[categoria]["cantidad_ventas"] += 1
            resumen[categoria]["unidades"] += unidades
            resumen[categoria]["monto_total"] += unidades * precio
            filas_procesadas += 1

    salida = io.StringIO()
    escritor = csv.writer(salida)
    escritor.writerow(
        ["categoria", "cantidad_ventas", "unidades", "monto_total"]
    )

    for categoria in sorted(resumen):
        datos = resumen[categoria]
        escritor.writerow(
            [
                categoria,
                datos["cantidad_ventas"],
                datos["unidades"],
                str(datos["monto_total"]),
            ]
        )

    s3.put_object(
        Bucket=BUCKET,
        Key=ARCHIVO_SALIDA,
        Body=salida.getvalue().encode("utf-8"),
        ContentType="text/csv",
    )

    print(f"Archivos de entrada: s3://{BUCKET}/{PREFIJO_ENTRADA}")
    print(f"Filas procesadas: {filas_procesadas}")
    print(f"Categorías encontradas: {len(resumen)}")
    print(f"Resultado: s3://{BUCKET}/{ARCHIVO_SALIDA}")


if __name__ == "__main__":
    procesar_ventas()