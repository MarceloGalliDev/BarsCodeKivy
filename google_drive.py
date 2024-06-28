# pylint: disable=all
# flake8: noqa

import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account


SERVICE_ACCOUNT_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive']

creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=creds)


def generate_download_link(file_id):
    return f"https://drive.google.com/uc?export=download&id={file_id}"

# 1p4kfRhOmv_w5D-HQ0jmWurb9jauyKXx2

def list_files_and_generate_links():
    folder_id = '1p4kfRhOmv_w5D-HQ0jmWurb9jauyKXx2'
    query = f"'{folder_id}' in parents and mimeType='image/png'"
    
    results = service.files().list(
        q=query,
        pageSize=1000,
        fields="nextPageToken,files(id, name)").execute()
    items = results.get('files', [])
    
    if not items:
        print('No files found.')
    
    data = []
    
    for item in items:
        file_name = item['name']
        download_link = generate_download_link(item['id'])
        data.append([file_name, download_link])
        print(f"File: {file_name}, Download Link: {download_link}")

    df = pd.DataFrame(data, columns=['File Name', 'Download Link'])
    
    output_excel_path = 'download_links.xlsx'
    df.to_excel(output_excel_path, index=False)
    print(f"Links de download salvos em {output_excel_path}")

list_files_and_generate_links()