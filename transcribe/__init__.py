import azure.functions as func
import logging
import os
import requests
from azure.core.credentials import AzureKeyCredential

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient
import json
import time
from pathlib import Path


import datetime
current_date = datetime.date.today()
month = current_date.month
day = current_date.day # '%B' for full month name, '%d' for day of the month

if os.getenv('LOCAL_DEV') == "True":
    BLOB_ENDPOINT = os.getenv("BLOB_ENDPOINT")
    blob_credential = DefaultAzureCredential()  # Uses managed identity or local login
    blob_service_client = BlobServiceClient(account_url=BLOB_ENDPOINT, credential=blob_credential)
    SUBSCRIPTION_KEY = os.getenv("SPEECH_KEY")
    SERVICE_REGION = os.getenv("SPEECH_REGION")
    BLOB_ENDPOINT=os.getenv("BLOB_ENDPOINT")
    DESTINATION_CONTAINER_URL=os.getenv("DESTINATION_CONTAINER_URL")


app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


RECORDINGS_CONTAINER_URI = f"{BLOB_ENDPOINT}/audio-files"
SPEECH_OUTPUT_CONTAINER_URI = f"{BLOB_ENDPOINT}/speech-output"

logging.info(f"BLOB_ENDPOINT: {BLOB_ENDPOINT}")

def write_to_blob(data, filename):
    container_name = "speech-output"
    blob_name = filename

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(data, overwrite=True)


# @app.route(route="transcribe/", methods=["POST"])
def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Function to send a transcription request to Azure Cognitive Services Speech to Text API.
    """
    logging.info(f"Blob trigger function processed a request.{req}")

    credential = DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default").token
    
    url = f"https://{SERVICE_REGION}.api.cognitive.microsoft.com/speechtotext/v3.2/transcriptions"
    headers = {
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Content-Type": "application/json"
    }

    data = {
        "contentContainerUrl": RECORDINGS_CONTAINER_URI,
        "destinationContainerUrl": DESTINATION_CONTAINER_URL,
        "properties": {
            "diarizationEnabled": False,
            "wordLevelTimestampsEnabled": False,
            "displayFormWordLevelTimestampsEnabled": False,
            # "punctuationMode": "DictatedAndAutomatic",
            "profanityFilterMode": "Masked",
            "timeToLive": "P2D"
        },
        "locale": "en-US",
        "displayName": "Transcription using default model for en-US",
}


    logging.info(f"data: {data}")

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    time.sleep(1)
    logging.info("response: ")

    logging.info(response.status_code)
    logging.info(response.json())

    url = response.json().get("self")
    
    while True:
        time.sleep(3)
        response = requests.get(url, headers=headers)
        response_data = response.json()

        # Check the status of the transcription
        if response_data['status'] == 'Succeeded':
            print("Transcription is completed.")
            break
        elif response_data['status'] == 'Failed':
            print("Transcription failed.")
            break
        else:
            print("Transcription is still processing...")

    links = response.json().get("links")
    files = links.get("files")

    response = requests.get(files, headers=headers)
# print(response.text)

    for file in response.json()["values"]:
    #   print(file['kind'])
    #   print(file.get("links").get("contentUrl"))
        if file['kind'] == 'Transcription':
            response = requests.get(file.get("links").get("contentUrl"), headers=headers)
            source_file_name = Path(response.json().get("source").split('/')[-1])

            # print("TRANSCRIPTION REPSONSE TEXT")
            # print(response.text)
            write_to_blob(json.dumps(response.json()), f"{month}/{day}/transcription-{source_file_name}.json")
            write_to_blob(json.dumps(response.json()['combinedRecognizedPhrases'][0]['lexical']), f"{month}/{day}/transcription-{source_file_name}.txt")

    # logging.info("Polling response: ")
    # logging.info(response.text)

    # Return the status code and response text
    return func.HttpResponse(f"Transcription request sent with status code: {response.status_code}")