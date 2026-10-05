from typing import Any
from langchain_core.messages import HumanMessage, SystemMessage
from .client import langgraph_client
from .support import LangGraphSupportAgent
from .sales import LangGraphSalesAgent

class LangGraphCoordinator:
    """
    AI-powered Coordinator Agent that uses LLM to analyze queries and route them 
    to the appropriate specialist agent.
    """

    def __init__(self, agents: list[Any]):
        self.agents = {}
        for agent in agents:
            if isinstance(agent, LangGraphSupportAgent):
                self.agents["support"] = agent
            elif isinstance(agent, LangGraphSalesAgent):
                self.agents["sales"] = agent

        self.model = None
        self.instructions = """ You are an intelligent customer service coordinator.  your primary role is to:
        
        1. ANALYZE each customer query to understand their intent
        2. DECIDE which specialist agent should handle the query.
        3. RESPOND with ONLY the routing decision

        Available specialist:
        - "support" - Handles FAQ questions (warranty, returns, shipping) and order status inquiries.
        - "sales" - Handles questions about promotions, discounts, deals, and special offers.
        - "general" - For any other questions that don't fit the above categories.

        IMPORTANT: You must respond with EXACTLY ONE WORD - either "support", "sales", or "general".
        Do not include any other text, explanation, or punctuation.  Just the single word.
        """

    async def initialize(self):
        """Initialize the coordinator model for LangGraph routing."""
        self.model = langgraph_client.get_model()
        print("   -> Coordinator Agent initialized (LangGraph)")

    async def _get_routing_decision(self, question: str) -> str:
        """ Use AI to determine which agent should handle the query"""
        if self.model is None:
            await self.initialize()

        response = await self.model.ainvoke(
            [
                SystemMessage(content=self.instructions),
                HumanMessage(
                    content=(
                        "Analyze this customer query and decide which specialist should handle it.\n\n"
                        f'Customer Query: "{question}"\n\n'
                        'Respond with ONLY one word: "support", "sales", or "general".'
                    )
                ),
            ]
        )

        decision = langgraph_client.extract_message_text(response).lower()
        if "support" in decision:
            return "support"
        if "sales" in decision:
            return "sales"
        if "general" in decision:
            return "general"
        return decision


    async def _handle_general_query(self, question: str) -> str:
        """Handle general queries that don't fit specialist agents."""

        if self.model is None:
            await self.initialize()

        response = await self.model.ainvoke(
            [
                SystemMessage(
                    content=(
                        "You are a helpful general customer service assistant."
                        "Provide clear and accurate responses."
                    )
                ),
                HumanMessage(
                    content=(
                        f"A customer asked: {question}.\n\n"
                        "Provide a helpful response.  If specific information is unavailable, "
                        "suggest alternatives like contacting support or visiting the website."
                    )
                ),
            ]
        )
        content = langgraph_client.extract_message_text(response).strip()
        return content or "I apologize, but I'm unable to assist with that question."


    async def route_query(self, question: str) -> str:
        """Main routing method -- uses AI to decide routing, then forwards to appropriate agent."""

        if self.model is None:
            await self.initialize()

        print(f"   [Coordinator] Analyzing query: {question}")
        routing_decision = await self._get_routing_decision(question)
        print(f"   [Coordinator] Routing decision: {routing_decision.upper()}")

        if routing_decision == "support":
            support_agent = self.agents.get("support")
            if support_agent:
                print(f"   [Coordinator] Forwarding query to support agent...")
                response = await support_agent.handle_query(question)
                if response:
                    return f"[Routed via Coordinator -> Support Agent]\n{response}"
                print(f"   [Coordinator] Support Agent failed, falling back to general...")

        elif routing_decision == "sales":
            sales_agent = self.agents.get("sales")
            if sales_agent:
                print(f"   [Coordinator] Forwarding query to Sales Agent...")

                response = await sales_agent.handle_query(question)
                if response:
                    return f"[Routed via Coordinator -> Sales Agent]\n{response}"
                print(f"   [Coordinator] Sales Agent failed, falling back to general...")


        print(f"   [Coordinator] Falling back to general query...")
        response = await self._handle_general_query(question)
        return f"[Routed via Coordinator -> General Assistant]\n{response}"
            