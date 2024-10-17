import os
import json
import requests
import datetime
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from pathlib import Path

BLOB_ENDPOINT = "https://functionapp1016.blob.core.windows.net/"
credential = DefaultAzureCredential()  # Uses managed identity or local login
blob_service_client = BlobServiceClient(account_url=BLOB_ENDPOINT, credential=credential)

current_date = datetime.date.today()
month = current_date.month
day = current_date.day # '%B' for full month name, '%d' for day of the month

print(month, day)

def write_to_blob(data, filename):
    container_name = "speech-output"
    blob_name = filename

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(data, overwrite=True)

transcription_endpoint = 'https://eastus.api.cognitive.microsoft.com/speechtotext/v3.2/transcriptions/81889019-5cc8-4c33-8bf2-4081faa1aeb1'

# Define the API endpoint URL

# Set up the headers with your subscription key
headers = {
    "Ocp-Apim-Subscription-Key": "706e7524522a4b78a377c59e8d2c56d0"
}

# Send the GET request
response = requests.get(transcription_endpoint, headers=headers)
print(response.json())
links = response.json().get("links")
files = links.get("files")

# print("files: ", files)

response = requests.get(files, headers=headers)
# print(response.text)

for file in response.json()["values"]:
#   print(file['kind'])
#   print(file.get("links").get("contentUrl"))
  if file['kind'] == 'Transcription':
    response = requests.get(file.get("links").get("contentUrl"), headers=headers)
    source_file_name = Path(response.json().get("source").split('/')[-1])

    print("TRANSCRIPTION REPSONSE TEXT")
    print(response.json()['combinedRecognizedPhrases'][0]['lexical'])
    write_to_blob(json.dumps(response.json()), f"{month}/{day}/transcription-{source_file_name}.json")
    write_to_blob(json.dumps(response.json()['combinedRecognizedPhrases'][0]['lexical']), f"{month}/{day}/transcription-{source_file_name}.txt")