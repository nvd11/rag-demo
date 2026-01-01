import asyncio
import sys
import os
from loguru import logger
from src.configs.db import get_async_engine
from src.agents.knowledge_base_agent import KnowledgeBaseAgent
from sqlalchemy.ext.asyncio import async_sessionmaker

async def run_agent_demo():
    # 1. Setup Database Session
    engine = get_async_engine()
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with async_session() as session:
        # 2. Initialize Agent
        # Scenario 1: General Assistant (Topic Optional)
        print("\n" + "="*50)
        print("🤖 Agent Demo: General Assistant")
        print("="*50 + "\n")
        
        # We rely on the default system prompt in KnowledgeBaseAgent.
        # SCENARIO 1: We DO NOT pass a topic to `ask()`.
        # The agent must rely on the LLM to detect the topic from the user's query 
        # (e.g., "topic:开发板 ...") and pass it to the tool.
        agent_general = KnowledgeBaseAgent(session)
        
        queries = [
            "topic:开发板 ,VisionFive 2 的 CPU 主频是多少？", # Explicit topic instruction in query
            "叶丽法的胸围是多少？"             # Should be filtered out
        ]
        
        for q in queries:
            print(f"\n❓ Question: {q}")
            result = await agent_general.ask(q)
            print(f"💡 Answer: {result['answer']}")
            if result['sources']:
                print(f"📚 Sources: {len(result['sources'])} found")
                for s in result['sources']:
                    print(f"   - {s}")

        # Scenario 2: Specialized Assistant (Topic Enforced via Code)
        print("\n" + "="*50)
        print("🤖 Agent Demo: VisionFive 2 Specialist")
        print("="*50 + "\n")
        
        # We use the SAME default agent configuration (KnowledgeBaseAgent).
        # SCENARIO 2: We EXPLICITLY pass `topic="开发板"` to `ask()`.
        # This injects a system instruction forcing the LLM to use this topic for tool calls.
        agent_specialized = KnowledgeBaseAgent(session)
        
        queries_special = [
            "昉·星光 2 是什么公司的产品？", # Context implies VisionFive 2 due to injected topic
            "Linux Kernel 的编译步骤？" # If we had Linux topic, it might search there, but we force '开发板'
        ]
        
        for q in queries_special:
            print(f"\n❓ Question: {q}")
            # Enforce topic '开发板' via the ask method
            result = await agent_specialized.ask(q, topic="开发板")
            print(f"💡 Answer: {result['answer']}")
            if result['sources']:
                print(f"📚 Sources: {len(result['sources'])} found")
                for s in result['sources']:
                    print(f"   - {s}")


if __name__ == "__main__":
    try:
        asyncio.run(run_agent_demo())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.exception("Fatal error in agent demo")
