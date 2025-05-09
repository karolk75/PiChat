import openai
import logging
from typing import List, Dict, AsyncGenerator
from ..config import settings


logger = logging.getLogger(__name__)

class AzureOpenAIService:
    def __init__(self):
        """Initialize Azure OpenAI client"""
        self.client = openai.AsyncAzureOpenAI(
            api_key=settings.AZURE_OPENAI_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT,
        )

    async def generate_response(
        self,
        messages: List[Dict[str, str]]
    ) -> AsyncGenerator:
        """Generate a streaming response from Azure OpenAI"""
        try:
            # Ensure we have a system message
            if not any(msg.get("role") == "system" for msg in messages):
                messages.insert(
                    0,
                    {
                        "role": "system",
                        "content": "You are a helpful assistant named PiChat. You provide concise and accurate information.",
                    },
                )

            logger.info(f"messages: {messages}")

            # Create a streaming completion
            stream = await self.client.chat.completions.create(
                model=settings.AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=messages,
                stream=True,
                temperature=0.7,
                # max_tokens=4096,
            )

            # Return the stream directly
            async for chunk in stream:
                yield chunk

        except Exception as e:
            logger.error(f"Error generating OpenAI response: {str(e)}")
            raise
        
openai_service = AzureOpenAIService()

def get_openai_service():
    return openai_service
