from .base import BaseLangGraphAgent
from .tools import FAQ_TOOL, ORDER_STATUS_TOOL

class LangGraphSupportAgent(BaseLangGraphAgent):
    def __init__(self, agent_name: str):
        instructions = """
        You are a customer support specialist.  Your role is to help customers with:
        1. General FAQ questions (warranty, returns, shipping)
        2. Order status inquiries

        Use the available tools to provide accurate information.  Be helpful, professional, and empathetic.  
        If you can not help with something, politely explain your limitations and suggest contacting getneral support.
        """
        
        super().__init__(
            agent_name=agent_name,
            instructions=instructions,
            tools=[FAQ_TOOL, ORDER_STATUS_TOOL]
        )
        