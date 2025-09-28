import os
from dotenv import load_dotenv
from google import genai

# Load API key from .env
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Generate a response
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents="Is it safe to go for a run tomorrow in Delhi if it's raining?",
)

print("Gemini says:", response.text)
