from src.embeddings.google_embedding import GoogleEmbedding
from src.embeddings.base_embedding import BaseEmbedding
from loguru import logger

class EmbeddingFactory:
    """
    Factory class to create Embedding instances based on provider name.
    """
    
    @staticmethod
    def get_embedding_provider(provider: str, model: str) -> BaseEmbedding:
        if provider == "google":
            return GoogleEmbedding(model)
        # Add other providers here:
        # elif provider == "openai":
        #     return OpenAIEmbedding(model)
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")
