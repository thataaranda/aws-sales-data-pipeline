# Pipeline de ventas con AWS

Proyecto de portafolio realizado por Thalita Aranda. Construí un flujo de datos que toma ventas ficticias de una base de datos PostgreSQL, las exporta a Amazon S3, comprueba que el archivo exista y genera un resumen de ventas por categoría.

## ¿Qué hace el proyecto?

1. Registré seis ventas ficticias en una base de datos PostgreSQL alojada en Amazon RDS.
2. Utilicé AWS Database Migration Service (DMS) para realizar una carga completa de la tabla de ventas hacia un archivo CSV en Amazon S3.
3. Creé una función de AWS Lambda que comprueba si el archivo CSV de origen existe en S3.
4. Creé un trabajo de AWS Glue que lee el CSV, agrupa las ventas por categoría y guarda un nuevo CSV con la cantidad de ventas, las unidades vendidas y el monto total.
5. Utilicé AWS Step Functions para ejecutar primero la validación con Lambda y después el trabajo de Glue.
6. Configuré permisos con AWS IAM y la conectividad necesaria mediante Amazon VPC y grupos de seguridad.

## Servicios utilizados

- **Amazon RDS:** alojamiento de PostgreSQL.
- **AWS DMS:** exportación inicial de la tabla desde PostgreSQL hacia S3.
- **Amazon S3:** almacenamiento del archivo de ventas y del resumen generado.
- **AWS Lambda:** comprobación de la existencia del archivo de entrada.
- **AWS Glue:** transformación y agrupación de las ventas.
- **AWS Step Functions:** coordinación de Lambda y Glue.
- **AWS IAM:** permisos de los servicios.
- **Amazon VPC:** conectividad de red entre los recursos que la necesitan.

## Resultado obtenido

El archivo de salida 'resumen_por_categoria.csv' contiene:

| Categoría | Cantidad de ventas | Unidades | Monto total |
| --- | ---: | ---: | ---: |
| Accesorios | 1 | 3 | 9000 |
| Pokemon | 3 | 7 | 39000 |
| Videojuegos | 2 | 2 | 43000 |

La ejecución de Step Functions finalizó correctamente. Los datos son ficticios y se utilizaron únicamente para demostrar el funcionamiento del proyecto.

## Alcance

DMS realizó una carga completa inicial. El flujo de Step Functions se ejecuta manualmente sobre el archivo que ya está en S3; no hay una actualización continua de la base de datos.
