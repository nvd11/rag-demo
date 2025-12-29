from abc import ABC, abstractmethod
from typing import Any

class BaseEmbedding(ABC):
    """
    Abstract base class for Embedding providers.
    """
    
    @abstractmethod
    def get_client(self) -> Any:
        """
        Returns the underlying embedding client (e.g., LangChain Embeddings object).
        """
        pass
