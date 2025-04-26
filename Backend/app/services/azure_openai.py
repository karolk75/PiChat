# import openai
# import logging
# from typing import List, Dict, Any, AsyncGenerator
# from ..config import settings

# # Configure OpenAI with Azure credentials
# client = openai.AsyncAzureOpenAI(
#     api_key=settings.AZURE_OPENAI_KEY,
#     api_version="2023-07-01-preview",
#     azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
# )

# logger = logging.getLogger(__name__)

# async def generate_response(messages: List[Dict[str, str]], model: str = "gpt-3.5-turbo") -> AsyncGenerator:
#     """Generate a streaming response from Azure OpenAI"""
#     try:
#         # Determine which deployment to use based on model
#         deployment_id = settings.AZURE_OPENAI_DEPLOYMENT_GPT4 if model == "gpt-4" else settings.AZURE_OPENAI_DEPLOYMENT_GPT35
        
#         # Check if we have necessary credentials
#         if not settings.AZURE_OPENAI_KEY or not settings.AZURE_OPENAI_ENDPOINT or not deployment_id:
#             logger.error("Missing Azure OpenAI credentials or deployment ID")
#             raise ValueError("Azure OpenAI is not properly configured")
        
#         # Ensure we have a system message
#         if not any(msg.get("role") == "system" for msg in messages):
#             messages.insert(0, {
#                 "role": "system", 
#                 "content": "You are a helpful assistant named PiChat. You provide concise and accurate information."
#             })
        
#         # Create a streaming completion
#         stream = await client.chat.completions.create(
#             model=deployment_id,
#             messages=messages,
#             stream=True,
#             temperature=0.7,
#             max_tokens=2000
#         )
        
#         # Return the stream directly
#         async for chunk in stream:
#             yield chunk
    
#     except Exception as e:
#         logger.error(f"Error generating OpenAI response: {str(e)}")
#         raise 