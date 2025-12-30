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
    async def search_datasheet(query: str) -> str:
        """
        Search for information in the VisionFive 2 Datasheet/Knowledge Base.
        Use this tool when you need technical details, specifications, or descriptions 
        about the VisionFive 2 hardware.
        
        Args:
            query: The search query (e.g., "CPU frequency", "Memory interface").
        """
        # Call the service
        return await retrieval_service.search_knowledge_base(query)

    return search_datasheet
