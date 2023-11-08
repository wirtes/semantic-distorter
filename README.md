# Semantic Distorter
This is a Mastodon bot that plays a game of "telephone" by translating a string through many languages to generate something of obfuscated meaning. The resulting string along with additional text specifying that the output should be in the style of a Victoian oil painting is used as the prompt to a Stable Diffusion API to generate an image. The resulting string and image are then posted to Mastodon. The output looks something like this:

This code needs a lot of refactoring at the moment.

<img width="592" alt="Screenshot 2023-11-04 at 7 34 32 PM" src="https://github.com/wirtes/semantic-fuzz-box/assets/11652957/23c1acf5-90bf-4ace-983e-ba5590fde1c2">

The original string, the translation path, and the final text are included as alt text on the image in the Mastodon post.

<img width="587" alt="Screenshot 2023-11-04 at 7 35 29 PM" src="https://github.com/wirtes/semantic-fuzz-box/assets/11652957/29e03791-652d-439e-b91c-9f99a4a72335">


