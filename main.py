#!/usr/bin/python

import requests
import json
import random
import sqlite3
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


def get_a_line():
    # Define the SQLite database file name
    db_filename = "database/book_lines.db"

    # Create a connection to the database
    conn = sqlite3.connect(db_filename)

    # Create a cursor object to interact with the database
    cursor = conn.cursor()

    # Select a random row from the "lines" table and retrieve the "line" field
    cursor.execute("SELECT line FROM lines ORDER BY RANDOM() LIMIT 1")
    random_line = cursor.fetchone()

    # Check if a random row was found
    # if random_line:
    #     # Print the "line" field from the random row
    #     print("Random Line:", random_line[0])
    # else:
    #     print("No rows found in the 'lines' table.")

    # Close the database connection
    conn.close()

    return random_line[0]


if __name__ == '__main__':
    original_text_to_translate = get_a_line()
    print ("Original: " + original_text_to_translate)
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
            text_to_translate = translated_text
        current_cycle += 1

    # Translate back to English
    translated_text = translate(translated_text, translate_from_language, "en")
    print("Final: ", translated_text)




