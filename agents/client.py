import os
from typing import Any
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from azure.identity import DefaultAzureCredential

load_dotenv()

class LangGraphClient:
    """
    Shared model factory for LangGraph agents.
    """

    def __init__(self):
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-5-mini")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self._azure_credential = DefaultAzureCredential()

        if not self._has_configured_model():
            raise ValueError(
                "Model configuration not found.  Configure either:\n"
                "1) OPENAI_API_KEY (and optionally OPENAI_MODEL), or\n"
                "2) AZURE_OPENAI_ENDPOINT + AZURE_OPENAI_DEPLOYMENT + AZURE_OPENAI_API_KEY."
            )

    def _has_configured_model(self) -> bool:
        has_azure = bool(self.azure_openai_endpoint and self.azure_openai_deployment)
        has_openai = bool(self.openai_api_key)
        return has_azure or has_openai

    def get_model(self):
        """Create and return the configured LangChain chat model."""

        endpoint = (self.azure_openai_endpoint or "").strip()
        deployment = (self.azure_openai_deployment or "").strip()
        api_key = (self.azure_openai_api_key or "").strip()
        openai_key = (self.openai_api_key or "").strip()

        # Azure OpenAI
        if endpoint and deployment and api_key:
            endpoint = endpoint.rstrip("/")

            print("   -> Using Azure OpenAI")
            print(f"   -> Endpoint: {endpoint}")
            print(f"   -> Deployment: {deployment}")

            return ChatOpenAI(
                model=deployment,
                base_url=endpoint,
                api_key="unused",
                default_headers={
                    "api-key": api_key
                },
            )

        # Standard OpenAI
        if openai_key:
            print("   -> Using OpenAI")

            return ChatOpenAI(
                model=self.openai_model,
                api_key=openai_key,
            )

        raise ValueError(
            "Unable to configure a model client. "
            "Set OPENAI_API_KEY or provide Azure OpenAI credentials."
        )
    @staticmethod
    def extract_message_text(message: Any) -> str:
        """Extract and return the text content from a LangChain model response."""
        if message is None:
            return ""
        
        if isinstance(message, BaseMessage):
            content = message.content
        elif isinstance(message, dict):
            content = message.get("content", "")
        else:
            content = str(message)

        if isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                else:
                    text_parts.append(str(item))
            return "\n".join(part for part in text_parts if part).strip()

        return str(content).strip()


langgraph_client = LangGraphClient()