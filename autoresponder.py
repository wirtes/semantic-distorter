#!/usr/bin/python

from mastodon import Mastodon
import semantic_distorter
from pprint import pprint
import json
import time
from bs4 import BeautifulSoup
import sys
import random
from datetime import datetime


# Setup Global Variables
config = semantic_distorter.get_config("/home/pi/botcode")
time_to_sleep = config["poll_interval"]

# Set up your Mastodon client with your instance URL and access token
mastodon = Mastodon(
    access_token = config["api_key"],  
    api_base_url = config["base_url"],
)

# Define your Mastodon username (without the "@" symbol)
my_username = config["mastodon_user_name"]

def read_state():
    # Open the text file in read mode (change the filename to your file)
    file_path = config["working_directory"] + "/state"
    try:
        with open(file_path, "r") as file:
            line = file.readline()
            if line:
                print("Read line from file:", line)
                id = int(line)
            else:
                print("File is empty or no more lines to read.")
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    return id


def write_state(last_mention_id):
    # The file path (change it to the desired file)
    file_path = config["working_directory"] + "/state"
    # Open the file in write mode (overwriting any existing content)
    with open(file_path, "w") as file:
        file.write(str(last_mention_id))
    return


def prepare_reply_text(content, acct):
    reply_content = "@" + acct + " Reply to: " + content
    return reply_content


def post_reply(content, message_id):
    # Initialize the Mastodon API client
    mastodon = Mastodon(
        access_token=config["api_key"],
        api_base_url=config["base_url"]
    )
    if len(content) > 499:
        content = content[:499]
    initial_status_id = mastodon.status_post(status=content, in_reply_to_id=message_id, visibility="public")
    # print(initial_status_id)
    return initial_status_id


def create_and_post_reply(mention_text, message_id, acct):
    # Load up the configuration & secrets
    # config = semantic_distorter.get_config(working_directory)
    # Initialize the Message Object
    message_obj = {}
    # Get a line to translate from the database
    original_text_to_translate = mention_text
    # author = line_from_book[1]
    # title = line_from_book[2]
    # Push the original line into the message object
    message_obj["original"] = original_text_to_translate
    print ("Original: " + original_text_to_translate)
    # Pick a number of times to translate the statement
    cycles = random.randint(config["min_translations"], config["max_translations"])
    text_to_translate = original_text_to_translate
    translate_from_language = "en"
    current_cycle = 1
    translation_path = "English > "
    while current_cycle < cycles:
        translate_to_language = semantic_distorter.pick_language(config["languages"])
        # Just skip if we selected the same language to translate
        if translate_to_language != translate_from_language:
            translated_text = semantic_distorter.translate(text_to_translate, translate_from_language, translate_to_language, config["translation_endpoint_url"])
            print("Translated from " + config["languages"][translate_from_language] + " to " + config["languages"][translate_to_language] + ": ", translated_text)
            message_obj[config["languages"][translate_to_language]] = translated_text
            translation_path += config["languages"][translate_to_language] + " > "
            translate_from_language = translate_to_language
            text_to_translate = translated_text
            current_cycle += 1

    # Translate back to English
    translated_text = semantic_distorter.translate(translated_text, translate_from_language, "en", config["translation_endpoint_url"])
    message_obj["final"] = "@" + acct + " : " + translated_text
    translation_path += "English"
    message_obj["translation_path"] = translation_path
    print("Final: ", translated_text)
    # Create an image from the translated_text
    text_prompt = config["sd_reply_image_prompt"] + translated_text
    response = semantic_distorter.generate_image_from_prompt(text_prompt, config["wizmodel_api_url"], config["wizmodel_api_key"])
    # Save the image to disk
    semantic_distorter.save_image_from_json(response, config["working_directory"] + '/images/autogen/reply_image.png')
    pprint(message_obj)
    semantic_distorter.post_reply_to_mastodon(message_obj, config, translation_path, current_cycle, config["working_directory"], config["hash_tags"], message_id)


def respond_to_mentions(last_mention_id):
    while True:
        # Let's sleep first to see if that calms down the OS after a reboot
        time.sleep(config["poll_interval"])
        mention_ids = []
        # Get the latest state

        print("last_mention_id: " + str(last_mention_id))
        # Fetch mentions in your timeline
        mentions = mastodon.notifications(since_id=last_mention_id)
        # pprint(mentions)
        print("Fetched Notifications")
        print("Number of mentions: " + str(len(mentions)))
        # Get the current date and time
        current_datetime = datetime.now()
        # Format the current date and time as a string
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
        # Print the formatted date and time
        print("Current Date and Time:", formatted_datetime)
        highest_mention_id = 0

        if len(mentions) > 0:
            for mention in mentions:
                # Mentions should be descending ID order, but this will find the higest in any order
                if mention.id > highest_mention_id:
                    highest_mention_id = mention.id
                print("Notification ID: " + str(mention["id"]))
                print("Mention Type: " + mention.type)
                # This executes if there are notifications of type "mention"
                # This is where we reply
                if mention.type == "mention":
                    mention_ids.append(mention.id)
                    print(mention.account.acct)
                    soup = BeautifulSoup(mention["status"]["content"], 'html.parser')
                    print(soup.get_text())
                    # reply_text = "Replying to: " + soup.get_text()
                    # reply_text = prepare_reply_text(soup.get_text(), mention.account.acct)

                    # pprint(mention)
                    # reply_id = post_reply(reply_text, mention.status.id)
                    create_and_post_reply(soup.get_text().replace("@semantic_distorter", ""), mention.status.id, mention.account.acct)
                    print("Replied to post id " + str(mention.status.id))


            # Check if there were any "mention" type notifications:
            if len(mention_ids) > 0:
                mention_ids.sort()
                # pprint(mention_ids)
                last_mention_id = mention_ids[-1]
            else:
                last_mention_id =  highest_mention_id
            print("Last Mention Id: " + str(last_mention_id))
            write_state(last_mention_id)
        print("\n\n=====\n\n")


if __name__ == "__main__":
    respond_to_mentions(read_state())
