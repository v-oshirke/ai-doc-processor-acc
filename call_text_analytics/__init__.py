import azure.functions as func
import logging
import os
import requests
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential

from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient

import datetime

# Get the current local date
current_date = datetime.date.today()

# Access the month and day as integers
current_month = current_date.month
current_day = current_date.day

BLOB_ENDPOINT = os.getenv("BLOB_ENDPOINT")
credential = DefaultAzureCredential()  # Uses managed identity or local login
blob_service_client = BlobServiceClient(account_url=BLOB_ENDPOINT, credential=credential)

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

key = os.getenv("LANGUAGE_KEY")
lang_endpoint = os.getenv("LANGUAGE_ENDPOINT")

credential = AzureKeyCredential(key)
client = TextAnalyticsClient(endpoint=lang_endpoint, credential=credential)

def get_blob_content(url):
    container_name = "speech-output"
    blob_name = "transcription-sample.mp4.txt"

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Download the blob content
    blob_content = blob_client.download_blob().readall().decode('utf-8')
    return blob_content

def write_to_blob(data, filename):
    container_name = "text-analytics-results"

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
    blob_client.upload_blob(data, overwrite=True)

# def main(myBlob: func.InputStream, name: str) -> func.HttpResponse:
def main(req: func.HttpRequest) -> func.HttpResponse:
    # logging.info(f"Python blob trigger function processed blob \n"
    #             f"Name: {name}\n"
    #             f"Blob Size: {myBlob.length} bytes")
    # blob_content = myBlob.read()

    # Assuming the blob content is a string, decode if necessary
    # If the blob is binary data, you might handle it differently
    # content = blob_content.decode('utf-8')
    # logging.info(f"Blob content: {text_content}")
    blob_url = f"{BLOB_ENDPOINT}/speech-output/{current_month}/{current_day}/transcription-sample.mp4.txt"
    logging.info("blob_url: %s", blob_url)
    content = get_blob_content(blob_url)
    logging.info("content: %s", content)
    documents = [
        content,
        """
        Patient needs to take 50 mg of ibuprofen.
        """
    ]

    poller = client.begin_analyze_healthcare_entities(documents)
    logging.info("poller: %s", poller)
    result = poller.result()

    logging.info("result: %s", result)
    docs = [doc for doc in result if not doc.is_error]
    logging.info("docs: %s", docs)

    entity_list = []
    for idx, doc in enumerate(docs):
        for entity in doc.entities:
            logging.info("Entity: {}".format(entity.text))
            entity_list.append(entity.text)
            logging.info("...Normalized Text: {}".format(entity.normalized_text))
            logging.info("...Category: {}".format(entity.category))
            logging.info("...Subcategory: {}".format(entity.subcategory))
            logging.info("...Offset: {}".format(entity.offset))
            logging.info("...Confidence score: {}".format(entity.confidence_score))
        for relation in doc.entity_relations:
            logging.info("Relation of type: {} has the following roles".format(relation.relation_type))
            for role in relation.roles:
                logging.info("...Role '{}' with entity '{}'".format(role.name, role.entity.text))
        logging.info("------------------------------------------")

    write_to_blob(str(entity_list), "{current_month}/{current_day}/health_entities.txt")
    return