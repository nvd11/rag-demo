from src.configs.config import yaml_configs
from src.embeddings.embedding_factory import EmbeddingFactory
from loguru import logger

class EmbeddingService:
    def __init__(self, provider: str | None = None, model: str | None = None):
        """
        Initialize EmbeddingService.
        
        Args:
            provider: The embedding provider to use (e.g., "google"). 
                      If None, reads from config or defaults to "google".
            model: The model name to use. 
                   If None, reads from config or defaults to "models/text-embedding-004".
        """
        embedding_config = yaml_configs.get("embedding", {})
        
        # Priority: Constructor Args -> Config File -> Defaults
        self.provider = provider or embedding_config.get("provider", "google")
        self.model = model or embedding_config.get("model", "models/text-embedding-004")
        
        logger.info(f"Initializing EmbeddingService with provider: {self.provider}, model: {self.model}")
        
        embedding_provider = EmbeddingFactory.get_embedding_provider(self.provider, self.model)
        self.embeddings = embedding_provider.get_client()

    def generate_embeddings(self, text_chunks: list[str]) -> list[list[float]]:
        """
        Generates embeddings for a list of text chunks.
        
        Args:
            text_chunks: List of text strings to embed.
            
        Returns:
            List of embedding vectors (list of floats).
        """
        if not text_chunks:
            logger.warning("Empty text_chunks provided to generate_embeddings")
            return []
            
        try:
            embeddings = self.embeddings.embed_documents(text_chunks)
            logger.info(f"Generated embeddings for {len(text_chunks)} chunks.")
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
