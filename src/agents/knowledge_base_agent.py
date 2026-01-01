from typing import List, Dict, Any, Optional
from loguru import logger
from langchain.agents import create_agent
from langchain_core.messages import ToolMessage, AIMessage, HumanMessage, SystemMessage
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
        # We don't pass system_prompt here if we want to dynamicly inject it or modify it per request.
        # But create_agent expects it.
        # We can pass the base system prompt here.
        return create_agent(
            model=llm,
            tools=tools,
            system_prompt=self.system_prompt
        )

    async def ask(self, query: str, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Processes a user query and returns the answer along with sources.
        
        Args:
            query: The user's question.
            topic: (Optional) The topic context for this query. If provided, 
                   it instructs the agent to search within this topic.
        
        Returns:
            Dict containing:
            - 'answer': The final text answer from the LLM.
            - 'sources': A list of source strings extracted from tool outputs.
        """
        try:
            messages = []
            
            # If topic is provided, inject a system instruction override/supplement
            # Note: create_agent's system_prompt is fixed in the graph. 
            # We can append a SystemMessage (or HumanMessage with instruction) to the input messages.
            if topic:
                instruction = f"IMPORTANT: For this query, you MUST use the 'search_knowledge_base' tool with topic='{topic}'."
                # Appending as a high-priority instruction (SystemMessage usually goes first, but here we append to conversation)
                # Some models handle SystemMessage in history well.
                messages.append(SystemMessage(content=instruction))
            
            messages.append(HumanMessage(content=query))
            
            inputs = {"messages": messages}
            
            # Execute the graph
            result = await self.agent_graph.ainvoke(inputs)
            messages = result["messages"]
            
            # Extract final answer (last message)
            last_message = messages[-1]
            if isinstance(last_message, AIMessage):
                content = last_message.content
                # Gemini response content might be a list of dicts with 'text' field (multi-modal response)
                # We check if it's a list and contains dicts.
                if isinstance(content, list) and len(content) > 0 and isinstance(content[0], dict):
                     # Join all text parts if there are multiple parts.
                     # We explicitly check isinstance(item, dict) to satisfy static type checkers and ensure safety.
                     answer_text = "".join([
                         item.get("text", "") 
                         for item in content 
                         if isinstance(item, dict) and "text" in item
                     ])
                else:
                     # Standard string content
                     answer_text = str(content)
            else:
                answer_text = str(last_message)
            
            # Extract sources from ToolMessages manually to ensure they are presented
            sources = []
            for msg in messages:
                if isinstance(msg, ToolMessage) and msg.name == "search_knowledge_base":
                    tool_output = str(msg.content)
                    # Retrieve Source lines and content
                    current_source = None
                    current_content = []
                    
                    lines = tool_output.split('\n')
                    for line in lines:
                        stripped_line = line.strip()
                        if stripped_line.startswith("[Source"):
                            # If we were already processing a source, save it
                            if current_source:
                                # Show truncated content preview (50 chars) for user readability
                                full_content = ' '.join(current_content)
                                preview = full_content[:50].replace('\n', ' ') + "..." if len(full_content) > 50 else full_content
                                sources.append(f"{current_source}\nContent: {preview}")
                            
                            # Start new source
                            current_source = stripped_line
                            if current_source.endswith(":"):
                                current_source = current_source[:-1]
                            current_content = []
                        elif current_source is not None:
                            # Append content lines to current source if not empty
                            if stripped_line:
                                current_content.append(stripped_line)
                    
                    # Append the last source
                    if current_source:
                         sources.append(f"{current_source}\nContent: {' '.join(current_content)[:200]}...")
                            
            # Format the final response
            final_response = {
                "answer": answer_text,
                "sources": sources
            }
            
            return final_response
            
        except Exception as e:
            logger.error(f"Error in KnowledgeBaseAgent: {e}")
            return {
                "answer": f"An error occurred: {str(e)}",
                "sources": []
            }
