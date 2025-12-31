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
        
        system_prompt_general = (
            "You are a helpful assistant. "
            "You have access to a knowledge base. "
            "When asked about technical details, use the 'search_knowledge_base' tool. "
            "If the user specifies a topic (e.g. 'VisionFive 2'), pass it to the tool."
        )
        
        agent_general = KnowledgeBaseAgent(session, system_prompt=system_prompt_general)
        
        queries = [
            "VisionFive 2 的 CPU 主频是多少？", # Should find it (topic='VisionFive 2' or inferred or global search)
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

        # Scenario 2: Specialized Assistant (Topic Enforced via Prompt)
        print("\n" + "="*50)
        print("🤖 Agent Demo: VisionFive 2 Specialist")
        print("="*50 + "\n")
        
        # Note: We enforce the topic by passing it to the ask method, which injects a system instruction
        system_prompt_specialized = (
            "You are a specialist for VisionFive 2 hardware. "
            "Do not answer questions unrelated to VisionFive 2."
        )
        
        agent_specialized = KnowledgeBaseAgent(session, system_prompt=system_prompt_specialized)
        
        queries_special = [
            "昉·星光 2 是什么公司的产品？", # Context implies VisionFive 2 due to specialist persona
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
