import os
from typing import Any
from pydantic import SecretStr
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from loguru import logger
from .base_embedding import BaseEmbedding

class GoogleEmbedding(BaseEmbedding):
    def __init__(self, model: str):
        self.model = model
        
    def get_client(self) -> Any:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            logger.error("GOOGLE_API_KEY not found in environment variables.")
            raise ValueError("GOOGLE_API_KEY is required for Google embeddings")
        
        return GoogleGenerativeAIEmbeddings(
            model=self.model,
            google_api_key=SecretStr(api_key)
        )
