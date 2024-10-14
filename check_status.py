import os
import json
import requests
import datetime
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
from pathlib import Path

BLOB_ENDPOINT = "https://functionapp912.blob.core.windows.net/"
credential = DefaultAzureCredential()  # Uses managed identity or local login
blob_service_client = BlobServiceClient(account_url=BLOB_ENDPOINT, credential=credential)

current_date = datetime.date.today()
month_day = current_date.strftime("%B %d")  # '%B' for full month name, '%d' for day of the month

print(month_day)

def write_to_blob(data, filename):
    container_name = "speech-output"
    blob_name = filename

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(data, overwrite=True)

transcription_endpoint = 'https://eastus.api.cognitive.microsoft.com/speechtotext/v3.2/transcriptions/c8b7dfbb-9387-403f-93a2-ce4060d336eb'

# Define the API endpoint URL

# Set up the headers with your subscription key
headers = {
    "Ocp-Apim-Subscription-Key": "706e7524522a4b78a377c59e8d2c56d0"
}

# Send the GET request
response = requests.get(transcription_endpoint, headers=headers)
links = response.json().get("links")
files = links.get("files")

print("files: ", files)

response = requests.get(files, headers=headers)
print(response.text)

for file in response.json()["values"]:
  print(file['kind'])
  print(file.get("links").get("contentUrl"))
  if file['kind'] == 'Transcription':
    response = requests.get(file.get("links").get("contentUrl"), headers=headers)
    source_file_name = Path(response.json().get("source").split('/')[-1])

    print("TRANSCRIPTION REPSONSE TEXT")
    print(response.text)
    write_to_blob(json.dumps(response.json()), f"{month_day}/transcription-{source_file_name}.json")
# Print the status code and response content
# print("Status Code:", response.status_code)
# print("Response Body:", response.text)

