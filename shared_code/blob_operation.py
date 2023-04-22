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


def upload_json_blob(json_dic, container_name, blob_name):
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    upload_data = json.dumps(json_dic).encode()
    # 空白、改行なしのjsonファイルが書き込まれる
    blob_client.upload_blob(data=upload_data, overwrite=True)
