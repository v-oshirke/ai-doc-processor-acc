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

key = os.getenv("LANGUAGE_KEY")
endpoint = os.getenv("LANGUAGE_ENDPOINT")

credential = AzureKeyCredential(key)
client = TextAnalyticsClient(endpoint=endpoint, credential=credential)

def get_blob_content(url):
    # connection_string = "BlobEndpoint=https://functionapp912.blob.core.windows.net/;QueueEndpoint=https://functionapp912.queue.core.windows.net/;FileEndpoint=https://functionapp912.file.core.windows.net/;TableEndpoint=https://functionapp912.table.core.windows.net/;SharedAccessSignature=sv=2022-11-02&ss=bfqt&srt=co&sp=rwdlacupiyx&se=2024-10-01T06:46:08Z&st=2024-09-30T22:46:08Z&spr=https&sig=QLdmo38QkPDh%2B1tVlkR5p33%2FuZu%2FVuRGPaSqzquKT64%3D"
    container_name = "text-files"
    blob_name = "health_sample.txt"

    # Create a BlobServiceClient to interact with Blob storage
    # blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

    # Download the blob content
    blob_content = blob_client.download_blob().readall().decode('utf-8')
    return blob_content

def write_to_blob(data):
    container_name = "text-analytics-results"
    blob_name = "result.json"

    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    blob_client.upload_blob(data, overwrite=True)

@app.route(route="textanalytics/", methods=["GET"])
def health_example(req: func.HttpRequest) -> func.HttpResponse:
    content = get_blob_content("https://functionapp912.blob.core.windows.net/text-files/health_sample.txt")
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

    docs = [doc for doc in result if not doc.is_error]

    for idx, doc in enumerate(docs):
        for entity in doc.entities:
            logging.info("Entity: {}".format(entity.text))
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

import openai
import os

def call_openai(analysis_result):
    # Set up Azure OpenAI credentials
    openai.api_type = "azure"
    openai.api_base = os.getenv("OPENAI_API_BASE")  # e.g., "https://your-resource-name.openai.azure.com/"
    openai.api_version = os.getenv("OPENAI_API_VERSION")  # e.g., "2023-05-15"
    openai.api_key = os.getenv("OPENAI_API_KEY")

    # Replace 'your-deployment-name' with your actual deployment name
    deployment_id = "your-deployment-name"

    # Prepare the prompt using the analysis result
    prompt = generate_prompt(analysis_result)  # Define this function to create a prompt based on analysis_result

    try:
        # Call the Azure OpenAI Completion API
        response = openai.Completion.create(
            deployment_id=deployment_id,
            prompt=prompt,
            max_tokens=100,
            temperature=0.7,
            n=1,
            stop=None
        )

        # Extract the generated text from the response
        generated_text = response.choices[0].text.strip()
        return generated_text

    except openai.error.OpenAIError as e:
        # Handle exceptions from the OpenAI API
        logging.error(f"An error occurred while calling Azure OpenAI: {e}")
        return None

def generate_prompt(analysis_result):
    # Example: Create a summary prompt using the extracted entities
    entities = []
    for doc in analysis_result:
        for entity in doc.get('entities', []):
            entities.append(entity['text'])

    # Create a prompt for the OpenAI model
    prompt = (
        "Based on the following medical entities extracted from patient records:\n"
        f"{', '.join(entities)}\n"
        "Please create a table that can be sent to a front end dashboard"
    )
    return prompt


@app.route(route="process/", methods=["POST"])
def process_text(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get the analysis result from the request or previous processing step
        analysis_result = req.get_json()
        
        # Call Azure OpenAI with the analysis result
        final_response = call_openai(analysis_result)
        
        if final_response:
            return func.HttpResponse(final_response, status_code=200)
        else:
            return func.HttpResponse("Failed to get a response from Azure OpenAI.", status_code=500)
    
    except Exception as e:
        logging.error(f"An error occurred in the processing function: {e}")
        return func.HttpResponse(f"An error occurred: {str(e)}", status_code=500)
