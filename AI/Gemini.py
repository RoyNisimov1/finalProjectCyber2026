import os
from dotenv import load_dotenv
from google import genai

class GideonGeminiBackEnd:
    def __init__(self):
        # Load your .env file
        load_dotenv()

        # The client automatically picks up GOOGLE_API_KEY from the environment
        self.client = genai.Client()

    def prompt(self, prompt):
        HEADER = "Do not use markdown. Answer the prompt below\nPrompt\""
        prompt = HEADER + prompt + "\"\nYour Answer:"

        # Generate content
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        return response.text
