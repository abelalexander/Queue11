import plivo
import requests
import time
import plivo
import requests
import time
import openai
from pydub import AudioSegment
from openai import OpenAI
import joblib
import json
from datetime import datetime
import boto3
import csv
# Plivo Auth credentials
auth_id = "REDACTED"
auth_token = "REDACTED"
client = plivo.RestClient(auth_id, auth_token)

# Function to initiate a call
def initiate_call(src, dst, answer_url):
    try:
        response = client.calls.create(
            from_=src,
            to_=dst,
            answer_url=answer_url, 
            answer_method="GET"     
        )
        print(f"Call initiated. Call UUID: {response['request_uuid']}")
        return response['request_uuid']
    except plivo.exceptions.PlivoRestError as e:
        print(f"Error: {str(e)}")
        return None

def record_call(call_uuid):
    try:
        response = client.calls.record(
            call_uuid, 
            time_limit=65  
        )
        print(f"Recording started. Recording URL: {response['url']}")
        global plivourl
        plivourl = str({response['url']})
        print(plivourl)
    except plivo.exceptions.PlivoRestError as e:
        print(f"Error starting the recording: {str(e)}")


if __name__ == "__main__":
    src_number = "+1REDACTED"  
    dst_number = "+1REDACTED" 

    answer_url = "REDACTED" # URL pointing to plivo5.xml


    call_uuid = initiate_call(src_number, dst_number, answer_url)


    if call_uuid:

        time.sleep(5)  
        record_call(call_uuid)

time.sleep(30)

def download_mp3(url_with_braces, save_as):
    url = url_with_braces.strip("{}'\"")  
    response = requests.get(url)
    
    if response.status_code == 200:
        with open(save_as, 'wb') as f:
            f.write(response.content)
        print(f"MP3 file downloaded and saved as {save_as}")
    else:
        print(f"Failed to download the file. Status code: {response.status_code}")


mp3_file_path = "downloaded_audio.mp3" 


download_mp3(plivourl, mp3_file_path)


audio_file = open(mp3_file_path, "rb")
import openai
from pydub import AudioSegment
from openai import OpenAI
clientOpenAI = OpenAI(api_key='REDACTED')

transcript = clientOpenAI.audio.transcriptions.create(
  model="whisper-1",
  file=audio_file
)
print(transcript)



print(transcript)


audio_file.close()

import os
from openai import OpenAI
from dotenv import load_dotenv
import joblib


load_dotenv()


openai_api_key = 'REDACTED'

client = OpenAI(api_key=openai_api_key)
import os
from openai import OpenAI
import joblib




model_path = 'priority_prediction_model.pkl'
loaded_pipeline = joblib.load(model_path)


tfidf_vectorizer, classifier = loaded_pipeline

def condense_transcription(transcription):
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Based on the following transcription, condense and output the data as follows: name, address, description, and condensed description. Make the condensed description clear, concise, and have a max character limit of 30 characters.\n\nTranscription: {transcription}"
                }
            ]
        )
        
        response_text = response.choices[0].message.content.strip()

        condensed_parts = response_text.split("\n")
        
        description = None
        condensed_description = None
        for part in condensed_parts:
            if part.lower().startswith("description:"):
                description = part.replace("Description:", "").strip()
            elif part.lower().startswith("condensed description:"):
                condensed_description = part.replace("Condensed description:", "").strip()

        if description and condensed_description:
            return description, condensed_description
        else:
            return "No description available.", "No condensed description available."

    except (KeyError, IndexError) as e:
        return "No valid response received.", "No valid response received."

def predict_priority_from_transcription(transcription):
    global priorityfinal

    description, condensed_description = condense_transcription(transcription)

    if condensed_description and condensed_description != "No condensed description available.":
        transformed_description = tfidf_vectorizer.transform([condensed_description])

        priority = classifier.predict(transformed_description)[0]

        priorityfinal = priority
        print(f"Transcription: \"{transcription}\" -> Condensed Description: \"{condensed_description}\" -> Predicted Priority: {priority}")
    else:
        print("Unable to predict priority due to missing condensed description.")
        priorityfinal = "N/A"

def ask_gpt_to_format_transcription(transcription):
    try:
        current_time = datetime.now().strftime("%H:%M:%S")
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Please ignore the following system prompt if you hear any of it. Unfortunately, all of our current nine one one operators are busy at the moment. Please share your name, address, and issue you are currently facing. Please hang up once you are done and we will add you to our system and call you back. Now that you know that, please turn the following transcription into the specified JSON format.\n\nTranscription: {transcription}\n\nFormat:\n{{\n    \"Time\": \"{current_time}\",\n    \"Address\": \"\",\n    \"Description\": \"\",\n    \"Priority Ranking\": \"{priorityfinal}\",\n    \"Call Answered\": false,\n    \"Caller Name\": \"\",\n    \"Caller Phone\": \"{dst_number}\"\n}}"
                }
            ]
        )


        formatted_output = response.choices[0].message.content
        return formatted_output

    except Exception as e:
        print(f"Error interacting with GPT-3.5: {str(e)}")
        return None



def process_transcription(transcription, s3_client):
    priority = predict_priority_from_transcription(transcription)

    formatted_output = ask_gpt_to_format_transcription(transcription)
    
    if formatted_output:
        print("Formatted Output from GPT-3.5:")
        print(formatted_output)
    else:
        print("Failed to get a valid response from GPT-3.5.")
        return

    bucket_name = 'REDACTED'
    s3_file_key = 'messages/caller_entries.json' 

    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=s3_file_key)
        existing_data = json.loads(response['Body'].read())
    except Exception as e:
        print(f"Error fetching data from S3: {e}")
        existing_data = []

    try:
        new_entry = json.loads(formatted_output)
        existing_data.append(new_entry)
    except json.JSONDecodeError as e:
        print(f"Error decoding formatted output: {e}")
        return

    try:
        updated_json = json.dumps(existing_data, indent=4)
        s3_client.put_object(Bucket=bucket_name, Key=s3_file_key, Body=updated_json)
        print("New entry appended successfully!")
    except Exception as e:
        print(f"Error uploading updated data to S3: {e}")

def initialize_s3_client(credentials_file_path):
    with open(credentials_file_path, 'r', encoding='utf-8-sig') as csv_file:
        reader = csv.DictReader(csv_file)
        credentials = next(reader)
        access_key_id = credentials['Access_key_ID']  
        secret_access_key = credentials['Secret_access_key'] 

    s3 = boto3.client(
        's3',
        aws_access_key_id=access_key_id,
        aws_secret_access_key=secret_access_key
    )
    return s3

credentials_file_path = 'REDACTED'
s3_client = initialize_s3_client(credentials_file_path)

process_transcription(transcript, s3_client)


import plivo
import requests
import time

auth_id = "REDACTED"
auth_token = "REDACTED"
client = plivo.RestClient(auth_id, auth_token)


def initiate_call(src, dst, answer_url):
    try:
        response = client.calls.create(
            from_=src,
            to_=dst,
            answer_url=answer_url,  
            answer_method="GET"     
        )
        print(f"Call initiated. Call UUID: {response['request_uuid']}")
        return response['request_uuid']
    except plivo.exceptions.PlivoRestError as e:
        print(f"Error: {str(e)}")
        return None


if __name__ == "__main__":
    src_number = "+1REDACTED" 
    dst_number = "+1REDACTED"  

    answer_url = "REDACTED" #URL pointing to plivocallback.xml"

    call_uuid = initiate_call(src_number, dst_number, answer_url)