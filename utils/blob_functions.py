import os
import logging
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

BLOB_ENDPOINT=os.getenv("BLOB_ENDPOINT")
if BLOB_ENDPOINT == None:
    BLOB_ENDPOINT="https://functionapp912b6f8.blob.core.windows.net"
    
blob_credential = DefaultAzureCredential()  # Uses managed identity or local login
blob_service_client = BlobServiceClient(account_url=BLOB_ENDPOINT, credential=blob_credential)

# DESTINATION_CONTAINER_URL=os.getenv("DESTINATION_CONTAINER_URL")

# RECORDINGS_CONTAINER_URI = f"{BLOB_ENDPOINT}/audio-files"
# SPEECH_OUTPUT_CONTAINER_URI = f"{BLOB_ENDPOINT}/speech-output"


logging.info(f"BLOB_ENDPOINT: {BLOB_ENDPOINT}")

def write_to_blob(container_name, blob_path, data):

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)
    blob_client.upload_blob(data, overwrite=True)

def get_blob_content(container_name, blob_path):

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_path)

    # Download the blob content
    blob_content = blob_client.download_blob().readall()
    return blob_content

def list_blobs(container_name):
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs()
    return blob_list

def delete_all_blobs_in_container(container_name):
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        blob_client = container_client.get_blob_client(blob.name)
        blob_client.delete_blob()