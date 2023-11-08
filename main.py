#!/usr/bin/python

import random
from pprint import pprint
import semantic_distorter

# Setup Global Variables we can't store in config (like the location of config)
working_directory = "/home/pi/botcode"


if __name__ == '__main__':
    # Load up the configuration & secrets
    config = semantic_distorter.get_config(working_directory)
    # Initialize the Message Object
    message_obj = {}
    # Get a line to translate from the database
    line_from_book = semantic_distorter.get_a_line(working_directory)
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
    message_obj["final"] = translated_text
    translation_path += "English"
    message_obj["translation_path"] = translation_path
    print("Final: ", translated_text)
    # Create an image from the translated_text
    text_prompt = config["sd_image_prompt"] + translated_text
    response = semantic_distorter.generate_image_from_prompt(text_prompt, config["wizmodel_api_url"], config["wizmodel_api_key"])
    # Save the image to disk
    semantic_distorter.save_image_from_json(response, config["working_directory"] + '/images/autogen/image.png')
    pprint(message_obj)
    semantic_distorter.post_to_mastodon(message_obj, config, translation_path, author, title, current_cycle, working_directory, config["hash_tags"])





