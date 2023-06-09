import os
import json
from azure.storage.blob import (
    BlobServiceClient
)

connect_str = os.environ['AzureWebJobsStorage']


def get_blob_client(container_name, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    return blob_client


def write_append_blob(container_name, blob_name, write_row_data):
    append_blob_client = get_blob_client(container_name, blob_name)
    if not append_blob_client.exists():
        append_blob_client.create_append_blob(write_row_data)
    append_blob_client.append_block(write_row_data + '\n')


def upload_json_blob(json_dic, container_name, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    upload_data = json.dumps(json_dic).encode()
    # 空白、改行なしのjsonファイルが書き込まれる
    blob_client.upload_blob(data=upload_data, overwrite=True)
