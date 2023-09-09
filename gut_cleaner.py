#!/usr/bin/python

import re


gutenberg_text_ebook_title = "The hermit hunter of the wilds by Gordon Stables.txt"

# Input and output file names
input_file_name = "books/source/" + gutenberg_text_ebook_title  # Replace with your input file name
output_file_name = "books/lines/" + gutenberg_text_ebook_title  # Replace with your output file name

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
        unbroken_paragraph = re.sub(r"([^\.])\n", r"\1 ", line)
        # Filter out short lines
        sentences = unbroken_paragraph.split(".")
        for sentence in sentences:
            if len(sentence) > 12:
                output_file.write(sentence+".")


print("File processing complete. Output written to", output_file_name)


