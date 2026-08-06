import os

from dotenv import load_dotenv

load_dotenv()

class Settings:
    def __init__(self) -> None:
        self.openai_api_key= os.getenv("OPENAI_API_KEY")
        self.openai_model= os.getenv("OPENAI_MODEL", "gpt-5-nano")

        if not self.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is missing. Please set it in your environment variables or in a .env file."
            )

settings= Settings()