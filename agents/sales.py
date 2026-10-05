from .base import BaseLangGraphAgent
from .tools import PROMOTIONS_TOOL

class LangGraphSalesAgent(BaseLangGraphAgent):
    def __init__(self, agent_name: str):
        instructions = """
        You are a sales specialist focused on promotions and discounts.
        Help customers find the best deals and understand our current offers. 
        Use the available tools to provide accurate promotion information.
        Be enthusiastic and helful while staying accurate about what's available.
        """

        super().__init__(
            agent_name=agent_name, 
            instructions=instructions, 
            tools=[PROMOTIONS_TOOL]
        )
