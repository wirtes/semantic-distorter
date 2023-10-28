#!/usr/bin/python

import re


gutenberg_text_ebook_title = "Arthur Conan Doyle-The Adventures of Sherlock Holmes.txt"

# Input and output file names
input_file_name = "./books/source/" + gutenberg_text_ebook_title  # Replace with your input file name
output_file_name = "./books/lines/" + gutenberg_text_ebook_title  # Replace with your output file name

# Open the input file for reading
with open(input_file_name, "r") as input_file:
    # Read the lines from the input file
    lines = input_file.readlines()

# Open the output file for writing
with open(output_file_name, "w") as output_file:
    # Iterate over the lines and apply the regex replacement
    for line in lines:
        # Remove forced wrap found in Gutenberg ebooks
        # Search for every line break that isn't immediately preceded by a period
        #   and remove it.
        # unbroken_paragraph = re.sub(r"([^\.])\n", r"\1 ", line)
        # Filter out short lines
        sentences = line.split(". ")
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 12:
                # print(sentence)
                output_file.write(sentence+".\n")


print("File processing complete. Output written to", output_file_name)


