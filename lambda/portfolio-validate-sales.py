import os
import boto3

s3 = boto3.client("s3")


def lambda_handler(event, context):
    bucket = os.environ["BUCKET"]
    prefix = os.environ["RAW_PREFIX"]

    response = s3.list_objects_v2(
        Bucket=bucket,
        Prefix=prefix
    )

    csv_files = [
        item for item in response.get("Contents", [])
        if item["Key"].lower().endswith(".csv")
        and item["Size"] > 0
    ]

    if not csv_files:
        raise ValueError(
            f"No hay CSV con datos en s3://{bucket}/{prefix}"
        )

    return {
        "bucket": bucket,
        "archivos_encontrados": len(csv_files)
    }
