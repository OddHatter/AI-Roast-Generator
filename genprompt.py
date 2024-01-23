import os
from dotenv import load_dotenv
from elevenlabs import set_api_key
import google.generativeai as genai

# Get .env variables
load_dotenv()
genapi_key = os.environ.get('genapi_key')
elevenlabs_key = os.environ.get('elevenlabs_key')
genai.configure(api_key=genapi_key)
set_api_key(elevenlabs_key)

# Set text prompt for gemini-pro-vision
text_prompt = 'You are Sir David Attenborough.Do not introduce yourself. Narrate the picture as if it is part of comedic roast. Do not use more than 60 words. Do not use the phrase "natural habitat". Be as mean as possible and be funny. Be concise but creative. Make sure to make fun of something specific to the picture.'

# Analyze image and generate prompt
def generate_prompt(img):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([text_prompt, img], stream=True)
    return response


