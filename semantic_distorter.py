#!/usr/bin/python

import requests
import json
import random
import sqlite3
import base64
from mastodon import Mastodon
from pprint import pprint

def get_config(working_directory):
    try:
        with open(working_directory + '/config/config.json', 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print("Config file not found.")
    except json.JSONDecodeError as e:
        print(f"JSON decoding error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


def pick_language(languages_dict):
    return random.choice(list(languages_dict.keys()))


def translate(text_to_translate, source_language, target_language, endpoint_url):
    # Define the endpoint URL
    # endpoint_url = "http://bee-pi.local:5000/translate"  # Replace with your actual endpoint URL
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


def get_a_line(working_directory):
    # Define the SQLite database file name
    db_filename = working_directory + "/database/book_lines.db"
    # Create a connection to the database
    conn = sqlite3.connect(db_filename)
    # Create a cursor object to interact with the database
    cursor = conn.cursor()
    # Select a random row from the "lines" table and retrieve the "line" field
    cursor.execute("SELECT line, author, title FROM lines ORDER BY RANDOM() LIMIT 1")
    random_line = cursor.fetchone()
    # pprint(random_line)
    # Close the database connection
    conn.close()
    return random_line


def save_image_from_json(response, image_save_path):
    try:
        data = response.json()
        image_data = data.get("images")
        if image_data:
            # Just grab the first image. Maybe someday we'll do something with the others.
            image_bytes = base64.b64decode(image_data[0])
            with open(image_save_path, 'wb') as image_file:
                image_file.write(image_bytes)
            print(f"Image saved to {image_save_path}")
        else:
            print("No 'images' element found in the JSON data.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")


def generate_image_from_prompt(text_prompt, api_url, api_key):
    payload = json.dumps({
        "prompt": text_prompt,
        "steps": 100
    })
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + api_key
        }
    response = requests.request("POST", api_url, headers=headers, data=payload)
    return response


def post_to_mastodon(message_obj, config, translation_path, author, title, number_of_translations, working_directory, hash_tags):
    # Initialize the Mastodon API client
    mastodon = Mastodon(
        access_token = config["api_key"],
        api_base_url = config["base_url"]
    )
    message_text = message_obj["final"] + "\n" + hash_tags
    # Setup the media object and alt-text
    # Alt text is a good place to also place additional information such as the number of translations
    # and the translation path.
    alt_text = "A random sentence from '" + title + "' by " + author + " translated " + str(number_of_translations) + " times."
    alt_text += "\n\nOriginal text:\n" + message_obj["original"]
    alt_text += "\n\nTranslation Path:\n" + message_obj["translation_path"]
    alt_text += "\n\nThe final text which was used to generate image:\n" + message_obj["final"]
    media = mastodon.media_post(working_directory + '/images/autogen/image.png', description=alt_text)
    # Post a status update to the Mastodon account
    initial_status_id = mastodon.status_post(status=message_text, visibility="public", media_ids=media)
    print(message_text)
    # reply_text = ("Original Text:\n\n" + message_obj["original"] + "\n\nis a line from the book '"
    #               + title + "' by " + author + " was translated " + translation_path + "\n\n#SemanticDistorter")
    # Commeting out the reply to
    # Post a reply to the original status
    #initial_status_id = mastodon.status_post(status=reply_text, in_reply_to_id=initial_status_id, visibility="unlisted")
    # print(reply_text)
    return


def post_reply_to_mastodon(message_obj, config, translation_path, number_of_translations, working_directory, hash_tags, message_id):
    # Initialize the Mastodon API client
    mastodon = Mastodon(
        access_token = config["api_key"],
        api_base_url = config["base_url"]
    )
    message_text = message_obj["final"] + "\n" + hash_tags
    # Setup the media object and alt-text
    # Alt text is a good place to also place additional information such as the number of translations
    # and the translation path.
    alt_text = "Translated " + str(number_of_translations) + " times."
    alt_text += "\n\nOriginal text:\n" + message_obj["original"]
    alt_text += "\n\nTranslation Path:\n" + message_obj["translation_path"]
    alt_text += "\n\nThe final text used to generate image:\n" + message_obj["final"]
    media = mastodon.media_post(working_directory + '/images/autogen/reply_image.png', description=alt_text)
    # Post a status update to the Mastodon account
    initial_status_id = mastodon.status_post(status=message_text, visibility="unlisted", media_ids=media, in_reply_to_id=message_id)
    print(message_text)
    # reply_text = ("Original Text:\n\n" + message_obj["original"] + "\n\nis a line from the book '"
    #               + title + "' by " + author + " was translated " + translation_path + "\n\n#SemanticDistorter")
    # Commeting out the reply to
    # Post a reply to the original status
    #initial_status_id = mastodon.status_post(status=reply_text, in_reply_to_id=initial_status_id, visibility="unlisted")
    # print(reply_text)
    return