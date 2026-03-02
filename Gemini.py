import os
from dotenv import load_dotenv
from google import genai

# Load your .env file
load_dotenv(dotenv_path=".env")

# The client automatically picks up GOOGLE_API_KEY from the environment
client = genai.Client()

# Generate content
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Explain how APIs work in simple terms.",
)

print(response.text)