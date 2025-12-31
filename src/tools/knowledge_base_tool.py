from langchain_core.tools import tool
from src.services.retrieval_service import RetrievalService
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

# We need a way to inject the session or service into the tool.
# Since @tool functions are stateless, we usually bind them or use a class-based tool.
# Here we define a function that returns the configured tool.

def create_retrieval_tool(session: AsyncSession):
    """
    Creates a LangChain tool bound to the retrieval service.
    """
    retrieval_service = RetrievalService(session)

    @tool
    async def search_knowledge_base(query: str, topic: Optional[str] = None) -> str:
        """
        Search for information in the Knowledge Base.
        
        Args:
            query: The search query (e.g., "CPU frequency", "Memory interface").
            topic: (Optional) specific topic to search within (e.g., "VisionFive 2"). 
                   If not provided, searches all documents.
        """
        # Call the service
        return await retrieval_service.search_knowledge_base(query, topic=topic)

    return search_knowledge_base
