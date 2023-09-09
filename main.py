#!/usr/bin/python

import requests
import json
import random
import re
from pprint import pprint


def pick_language():
    languages = ["en", "es", "ru", "it", "eo", "ko", "de", "ar", "az", "he", "hi", "ga", "th"]
    return random.choice(languages)


def translate(text_to_translate, source_language, target_language):
    # Define the endpoint URL
    endpoint_url = "http://bee-pi.local:5000/translate"  # Replace with your actual endpoint URL
    # Define the JSON payload
    payload = {
            "q": text_to_translate,
            "source": source_language,
            "target": target_language,
            "format": "text",
            "api_key": ""
        }
    # Convert the payload to JSON format
    json_payload = json.dumps(payload)
    # Set the headers for the request (specify JSON content type)
    headers = { "Content-Type": "application/json" }
    try:
        # Send the POST request with the JSON payload
        response = requests.post(endpoint_url, data=json_payload, headers=headers)

    except Exception as e:
        print(f"An error occurred: {str(e)}")

    translated_object = json.loads(response.text)
    return translated_object["translatedText"]


if __name__ == '__main__':
    original_text_to_translate = "“Dost thou well, O poplar-tree log, to boast thus of thy beauty and stateliness?"

    # Pick a number of times to translate the statement
    cycles = random.randint(5, 10)
    text_to_translate = original_text_to_translate
    translate_from_language = "en"
    current_cycle = 0
    while current_cycle < cycles:
        translate_to_language = pick_language()
        # Just skip if we selected the same language to translate
        if translate_to_language != translate_from_language:
            translated_text = translate(text_to_translate, translate_from_language, translate_to_language)
            print("Translated from " + translate_from_language + " to " + translate_to_language + ": ", translated_text)
            translate_from_language = translate_to_language
        current_cycle += 1

    # Translate back to English
    translated_text = translate(translated_text, translate_from_language, "en")
    print("Final: ", translated_text)




