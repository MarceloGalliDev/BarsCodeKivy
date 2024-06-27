# pylint: disable=all
# flake8: noqa

import re
import boto3
import pandas as pd
from botocore.exceptions import NoCredentialsError


def generate_presigned_url(bucket_name, object_name, expiration=345600):
    s3_client = boto3.client('s3')
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name,
                'ResponseContentDisposition': 'attachment'
            },
            ExpiresIn=expiration)
    except NoCredentialsError:
        print("Credentials not available")
        return None

    return response


def list_files_and_generate_links(bucket_name):
    s3_client = boto3.client('s3')
    result = s3_client.list_objects_v2(Bucket=bucket_name)

    files_data = []
    if 'Contents' in result:
        for obj in result['Contents']:
            file_name = obj['Key']
            if file_name.endswith('.png'):  # Filtrar apenas arquivos PNG
                code_match = re.search(r'convite-(\d+)\.png', file_name)
                if code_match:
                    code = code_match.group(1)
                    url = generate_presigned_url(bucket_name, file_name)
                    files_data.append([file_name, url, code])

    return files_data


def main():
    bucket_name = 'dusnei-convite'
    files_data = list_files_and_generate_links(bucket_name)

    if files_data:
        df = pd.DataFrame(files_data, columns=['File Name', 'Download Link', 'Code'])
        output_excel_path = 'download_links.xlsx'
        df.to_excel(output_excel_path, index=False)
        print(f"Links de download salvos em {output_excel_path}")
    else:
        print("No PNG files found in the bucket.")


if __name__ == "__main__":
    main()
