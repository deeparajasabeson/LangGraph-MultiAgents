from langchain.agents import create_agent
from .client import langgraph_client

class BaseLangGraphAgent:
    """
    Base class for specialist agents.
    """
    def __init__(self, agent_name: str, instructions: str, tools: list | None = None):
        self.agent_name = agent_name
        self.instructions = instructions
        self.tools = tools or []
        self.graph = None   # parameter for graph setting

    async def initialize(self):
        model = langgraph_client.get_model()

        self.graph = create_agent(
            model=model,
            tools=self.tools,
            system_prompt=self.instructions
        )

        print(f"-> {self.agent_name} initialized.")


    async def handle_query(self, question: str) -> str | None:
        if self.graph is None:
            await self.initialize()

        result = await self.graph.ainvoke(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            }
        )

        messages = result.get("messages", [])
        return langgraph_client.extract_message_text(messages[-1])
