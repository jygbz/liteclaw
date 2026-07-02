import os
import asyncio
os.chdir(os.path.dirname(os.path.abspath(__file__)))

from liteclaw.core.agent import create_agent_app
from liteclaw.core.config import DB_PATH
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from langchain_core.messages import HumanMessage

async def test_liteclaw():
    print("🔧 Initializing LiteClaw...")
    
    async with AsyncSqliteSaver.from_conn_string(DB_PATH) as memory:
        app = create_agent_app(provider_name='deepseek', model_name='deepseek-v4-flash', checkpointer=memory)
        config = {"configurable": {"thread_id": "test_user"}}
        
        print("✅ Agent app created")
        print("🔍 Testing with: '你好'")
        
        inputs = {"messages": [HumanMessage(content="你好")]}
        
        async for event in app.astream(inputs, config=config, stream_mode="updates"):
            for node_name, node_data in event.items():
                if node_name == "agent":
                    last_msg = node_data["messages"][-1]
                    if hasattr(last_msg, "tool_calls") and last_msg.tool_calls:
                        for tc in last_msg.tool_calls:
                            print(f"  ● Tool Call: {tc['name']}")
                    elif last_msg.content:
                        print(f"\n🤖 Response: {last_msg.content}")
        
        print("\n✅ LiteClaw test completed successfully!")

if __name__ == "__main__":
    asyncio.run(test_liteclaw())