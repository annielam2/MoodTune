## MoodTune
Welcome to MoodTune! A simple web app that recommends music based on your mood.
MoodTune takes a short text description of how you’re feeling and uses an AI emotion model to detect your mood.
It then maps that mood to a Last.fm music tag and displays a playlist of recommended songs.
You can also select optional genres to influence the playlist (such as indie, pop, electronic, etc.), and you can regenerate the playlist to get a new set of tracks.
Each result includes a link that allows you to open the song on Spotify via a search page.
--- 
### Important Info
MoodTune does not create a playlist in your Spotify library.
Instead, it provides recommended songs and links you to them.
This web app relies on two external APIs:
Hugging Face Inference API (for emotion detection)
Last.fm API (for music recommendations)
Because MoodTune communicates with external services, your results depend on API response times. Most requests return quickly, but occasional delays may occur.
Album artwork is intentionally replaced with a clean placeholder for consistency because Last.fm does not always provide reliable images.
The form expects the user to enter a natural language description of how they feel (for example: “I’m tired but hopeful” or “Feeling stressed after my exam”).
Genre selection is optional.
--- 
### Getting API Keys
MoodTune requires two API keys: a Hugging Face Inference API token and a Last.fm API key.
#### 1. Create the secrets file
Create a hidden file in your project directory named: projectsecrets.py
Inside it, add the following:

APP_SECRET_KEY = "your_flask_secret_here"

LASTFM_API_KEY = "your_lastfm_key_here"

HF_TOKEN = "your_huggingface_token_here"

This file should NOT be shared publicly or pushed to GitHub.
#### 2. Getting a Last.fm API Key
* Go to: https://www.last.fm/api/account/create
* Log in or create a free Last.fm account
* Create an API application
* Copy the generated API key into projectsecrets.py
* The Last.fm API is used to fetch playlists based on mood tags such as “happy”, “sad”, “chill”, or “energetic”.

#### 3. Getting a Hugging Face API Token
* Go to: https://huggingface.co/settings/tokens
* Create a new token with “read” permissions
* Copy the token into projectsecrets.py
* This token allows MoodTune to call an emotion classification model that interprets the user’s text.