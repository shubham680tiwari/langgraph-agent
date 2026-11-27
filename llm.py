import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

def get_llm(temperature: float = 0):
    """Returns the Gemini chat model used by entire project"""

    if not os.getenv('GOOGLE_API_KEY'):
        raise RuntimeError('Google API Key is missing')
    return ChatGoogleGenerativeAI(
        model=os.getenv('GEMINI_MODEL', 'gemini-3.5-flash'),
        temperature = temperature,
        timeout=30.0,
        max_retries=2
    )

def text_of(message) -> str:
    """Return the plain text of the message"""
    content = message.content

    if isinstance(content, str):
        return content
    return ''.join(
        block.get('text', '') for block in content if isinstance(block, dict)
    )