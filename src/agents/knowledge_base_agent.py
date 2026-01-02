import asyncio
import sys
import os
import re
from typing import Optional, Dict, Any, List
from loguru import logger
from langchain.agents import create_agent
from langchain_core.messages import BaseMessage, ToolMessage, AIMessage, HumanMessage, SystemMessage
from sqlalchemy.ext.asyncio import AsyncSession

from src.tools.knowledge_base_tool import create_retrieval_tool
from src.llm.gemini_chat_model import get_gemini_llm

class KnowledgeBaseAgent:
    """
    A generic agent for querying a knowledge base.
    It encapsulates the LangChain agent graph and handles response formatting including source citation.
    """

    DEFAULT_SYSTEM_PROMPT = (
        "You are a helpful assistant. "
        "You have access to a knowledge base. "
        "When asked about technical details, use the 'search_knowledge_base' tool. "
        "If the user specifies a topic in the question, pass it to the tool."
    )
    
    def __init__(self, session: AsyncSession, system_prompt: str = DEFAULT_SYSTEM_PROMPT):
        self.session = session
        self.system_prompt = system_prompt
        self.agent_graph = self._build_agent()
        
    def _build_agent(self):
        # 1. Create Tools
        self.retrieval_tool = create_retrieval_tool(self.session)
        tools = [self.retrieval_tool]
        
        # 2. Setup LLM
        llm = get_gemini_llm()
        
        # 3. Create Graph
        return create_agent(
            model=llm,
            tools=tools,
            system_prompt=self.system_prompt
        )

    async def ask(self, query: str, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Processes a user query and returns the answer along with sources.
        """
        try:
            inputs = self._prepare_inputs(query, topic)
            result = await self.agent_graph.ainvoke(inputs)
            messages = result["messages"]
            
            return {
                "answer": self._extract_answer(messages),
                "sources": self._extract_sources(messages)
            }
            
        except Exception as e:
            logger.error(f"Error in KnowledgeBaseAgent: {e}")
            return { "answer": f"An error occurred: {str(e)}", "sources": [] }

    def _prepare_inputs(self, query: str, topic: Optional[str]) -> Dict[str, List[BaseMessage]]:
        """Prepares the input messages for the agent."""
        messages: List[BaseMessage] = []
        if topic:
            instruction = f"IMPORTANT: For this query, you MUST use the 'search_knowledge_base' tool with topic='{topic}'."
            messages.append(SystemMessage(content=instruction))
        
        messages.append(HumanMessage(content=query))
        return {"messages": messages}

    def _extract_answer(self, messages: List[BaseMessage]) -> str:
        """Extracts the final answer from the agent's messages."""
        last_message = messages[-1]
        if isinstance(last_message, AIMessage):
            content = last_message.content
            if isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict):
                # Handle structured content (e.g. from some models)
                return "".join([item.get("text", "") for item in content if isinstance(item, dict) and "text" in item])
            return str(content)
        return str(last_message)

    def _extract_sources(self, messages: List[BaseMessage]) -> List[str]:
        """Extracts and formats sources from ToolMessages."""
        sources = []
        for msg in messages:
            if isinstance(msg, ToolMessage) and msg.name == "search_knowledge_base":
                tool_output = str(msg.content)
                sources.extend(self._parse_tool_output(tool_output))
        return sources

    def _parse_tool_output(self, tool_output: str) -> List[str]:
        """Parses the raw string output from the retrieval tool."""
        sources = []
        current_source_header = None
        current_content = []
        
        lines = tool_output.split('\n')
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith("[Source"):
                if current_source_header:
                    self._append_source(sources, current_source_header, current_content)
                
                current_source_header = self._parse_source_header(stripped_line)
                current_content = []
                
            elif current_source_header is not None:
                if stripped_line:
                    current_content.append(stripped_line)
        
        if current_source_header:
             self._append_source(sources, current_source_header, current_content)
             
        return sources

    def _parse_source_header(self, header_line: str) -> str:
        """Parses a single source header line to extract and format metadata."""
        source_id = header_line.split(']')[0] + ']'
        score_match = re.search(r"\(Score: ([\d\.]+)\)", header_line)
        score_str = f"(Score: {score_match.group(1)})" if score_match else ""
        
        meta_parts = []
        
        # Match Page: N or page=N
        page_match = re.search(r"(?:Page: |page=)(\d+)", header_line)
        if page_match:
            meta_parts.append(f"Page: {page_match.group(1)}")

        title_match = re.search(r"title=([^,)]+)", header_line)
        if title_match:
            meta_parts.append(f"Title: {title_match.group(1)}")
            
        source_match = re.search(r"source=([^,)]+)", header_line)
        if source_match:
            file_path = source_match.group(1)
            file_name = os.path.basename(file_path)
            meta_parts.append(f"File: {file_name}")

        meta_str = ", ".join(meta_parts)
        return f"{source_id} ({meta_str}) {score_str}"

    def _append_source(self, sources: List[str], header: str, content: List[str]):
        """Formats and appends a source entry to the list."""
        full_content = ' '.join(content)
        # Create a short preview of the content
        preview = full_content[:200].replace('\n', ' ') + "..." if len(full_content) > 200 else full_content
        sources.append(f"{header}\nContent: {preview}")
