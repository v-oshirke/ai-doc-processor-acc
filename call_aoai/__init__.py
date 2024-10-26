import azure.functions as func
import logging
import os
import jwt
import time
from azure.identity import ClientSecretCredential, DefaultAzureCredential
import base64
import requests
import json
import utils.prompts as prompts
from azure.keyvault.secrets import SecretClient
from utils.blob_functions import get_blob_content, write_to_blob

import datetime
current_date = datetime.date.today()
month = current_date.month
day = current_date.day

def get_prompts():
  system_prompt=prompts.adverse_events_prompt
  user_prompt="Read the following text and generate the table as previously instructed./n/nText: "
  # logging.info(system_prompt)
  return system_prompt, user_prompt


def main(myblob: func.InputStream):
  logging.info(f"Processing blob \n"
              f"Name: {myblob.name}\n"
              f"Blob Size: {myblob.length} bytes")

  if os.getenv('LOCAL_DEV') == "True":
    content = get_blob_content("silver", "result.json")
  else:
     content = myblob.read().decode('utf-8')
  logging.info(f"content {content}")

  logging.info('Python HTTP trigger function processed a request.')
  
  credential = DefaultAzureCredential()
  # Get token from the credential
  token = credential.get_token("https://cognitiveservices.azure.com/.default").token
  logging.info(f"Token: {token}")
  decoded_token = jwt.decode(token, options={"verify_signature": False})

  # Extract the object ID (oid) claim
  object_id = decoded_token.get('oid')
  logging.info(f"Object ID: {object_id}")
  system_prompt, user_prompt = get_prompts()
  headers = {
    "Content-Type": "application/json",  
    "Authorization": f"Bearer {token}"  
  }  
  
  # Payload for the request  
  payload = {
    "messages": [
      {
        "role": "system",
        "content": [
          {
            "type": "text",
            "text": f"{system_prompt}"
          }
        ],
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": user_prompt+content
          }
        ]
      }
    ],
    "temperature": 0.7,
    "top_p": 0.95,
    "max_tokens": 800
  }  
  ENDPOINT = "https://remmey-aoai.openai.azure.com/openai/deployments/gpt-4o/chat/completions?api-version=2024-02-15-preview"  
    
  # Send request  
  try:  
    response = requests.post(ENDPOINT, headers=headers, json=payload)  
    response.raise_for_status()
    # Handle the response as needed (e.g., print or process)  
    # Will raise an HTTPError if the HTTP request returned an unsuccessful status code  
  except requests.RequestException as e:  
    raise SystemExit(f"Failed to make the request. Error: {e}")  
  response_content = response.json().get('choices')[0].get('message').get('content')
  logging.info(f'LLM Response: {response_content}')
  json_bytes = response_content.encode('utf-8')
  # Write the response to a blob
  logging.info("Writing response to blob")
  sourcefile = os.path.splitext(os.path.basename(myblob.name))[0]
  logging.info(f"sourcefile: {sourcefile}")
  write_to_blob("gold", f"{sourcefile}-output.json", json_bytes)