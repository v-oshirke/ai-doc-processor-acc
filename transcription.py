import azure.functions as func
import logging
import os
import requests
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

credential = DefaultAzureCredential()  # Uses managed identity or local login
blob_service_client = BlobServiceClient(account_url="https://functionapp912.blob.core.windows.net/", credential=credential)



app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# key = 
# region=
# endpoint = 



import os

SUBSCRIPTION_KEY = os.getenv("SPEECH_KEY")
SERVICE_REGION = os.getenv("SPEECH_REGION")
NAME = "Simple transcription"
DESCRIPTION = "Simple transcription description"
LOCALE = "en-US"
# RECORDINGS_BLOB_URI = "<Your SAS Uri to the recording>"
RECORDINGS_CONTAINER_URI = os.getenv("CONTAINER_URL")

import requests
import json
    
@app.route(route="transcribe/", methods=["GET"])
def post_transcription_request(req: func.HttpRequest) -> func.HttpResponse:
    """
    Function to send a transcription request to Azure Cognitive Services Speech to Text API.
    

    """
    
    
    url = f"https://{SERVICE_REGION}.api.cognitive.microsoft.com/speechtotext/v3.2/transcriptions"
    headers = {
        "Ocp-Apim-Subscription-Key": SUBSCRIPTION_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "contentContainerUrl": RECORDINGS_CONTAINER_URI,
        "locale": LOCALE,
        "displayName": "transcription-job",
        "model": None,
        "properties": {}
    }

    # Make the POST request
    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Return the status code and response text
    return response.status_code, response.text

