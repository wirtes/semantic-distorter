#!/usr/bin/python

import requests
import json
import random
import sqlite3
import base64
from mastodon import Mastodon
from pprint import pprint

# Setup Global Variables we can't store in config (like the location of config)
working_directory = "/home/pi/botcode"


def get_config():
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
    print("Working directory value " + working_directory)
    return random.choice(list(languages_dict.keys()))


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


def post_to_mastodon(message_obj, config, translation_path, author, title, number_of_translations):
    # Initialize the Mastodon API client
    mastodon = Mastodon(
        access_token = config["api_key"],
        api_base_url = config["base_url"]
    )
    message_text = message_obj["final"] + "\n#SemanticDistorter #NondeterministicPoetry"
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
    reply_text = ("Original Text:\n\n" + message_obj["original"] + "\n\nis a line from the book '"
                  + title + "' by " + author + " was translated " + translation_path + "\n\n#SemanticDistorter")
    # Commeting out the reply to
    # Post a reply to the original status
    #initial_status_id = mastodon.status_post(status=reply_text, in_reply_to_id=initial_status_id, visibility="unlisted")
    # print(reply_text)
    return


if __name__ == '__main__':
    # Load up the configuration & secrets
    config = get_config()
    # Initialize the Message Object
    message_obj = {}
    # Get a line to translate from the database
    line_from_book = get_a_line()
    original_text_to_translate = line_from_book[0]
    author = line_from_book[1]
    title = line_from_book[2]
    # Push the original line into the message object
    message_obj["original"] = original_text_to_translate
    print ("Original: " + original_text_to_translate)
    # Pick a number of times to translate the statement
    cycles = random.randint(5, 8)
    text_to_translate = original_text_to_translate
    translate_from_language = "en"
    current_cycle = 1
    translation_path = "English > "
    while current_cycle < cycles:
        translate_to_language = pick_language(config["languages"])
        # Just skip if we selected the same language to translate
        if translate_to_language != translate_from_language:
            translated_text = translate(text_to_translate, translate_from_language, translate_to_language)
            print("Translated from " + config["languages"][translate_from_language] + " to " + config["languages"][translate_to_language] + ": ", translated_text)
            message_obj[config["languages"][translate_to_language]] = translated_text
            translation_path += config["languages"][translate_to_language] + " > "
            translate_from_language = translate_to_language
            text_to_translate = translated_text
            current_cycle += 1

    # Translate back to English
    translated_text = translate(translated_text, translate_from_language, "en")
    message_obj["final"] = translated_text
    translation_path += "English"
    message_obj["translation_path"] = translation_path
    print("Final: ", translated_text)
    # Create an image from the translated_text
    text_prompt = config["sd_image_prompt"] + translated_text
    response = generate_image_from_prompt(text_prompt, config["wizmodel_api_url"], config["wizmodel_api_key"])
    # Save the image to disk
    save_image_from_json(response, working_directory + '/images/autogen/image.png')
    pprint(message_obj)
    post_to_mastodon(message_obj, config, translation_path, author, title, current_cycle)





