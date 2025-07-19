import requests
import json
from typing import Generator
from utils.config import GEMMA_SERVICE_URL


def ask_gemma(prompt: str, streaming: bool = False) -> str | Generator[str, None, None]:
    """
    Simple function to ask Gemma 12b a question and get a response.
    
    Args:
        prompt: The input text prompt/question
        streaming: Whether to use streaming response (default: False)
        
    Returns:
        If streaming=False: The complete generated text response
        If streaming=True: A generator that yields text chunks as they're generated
    """
    if GEMMA_SERVICE_URL is None:
        raise ValueError("GEMMA_SERVICE_URL not configured")
    
    api_endpoint = f"{GEMMA_SERVICE_URL.rstrip('/')}/api/generate"
    
    payload = {
        "model": "gemma3:12b",
        "prompt": prompt,
        "stream": streaming
    }
    
    try:
        response = requests.post(
            api_endpoint,
            json=payload,
            headers={"Content-Type": "application/json"},
            stream=streaming,
            timeout=120
        )
        response.raise_for_status()
        
        if streaming:
            # Return a generator for streaming responses
            def stream_generator():
                for line in response.iter_lines():
                    if line:
                        try:
                            chunk = json.loads(line.decode('utf-8'))
                            if 'response' in chunk:
                                yield chunk['response']
                        except json.JSONDecodeError:
                            continue
            
            return stream_generator()
        else:
            # For non-streaming, collect all response chunks
            full_response = ""
            for line in response.text.strip().split('\n'):
                if line.strip():
                    try:
                        chunk = json.loads(line)
                        if 'response' in chunk:
                            full_response += chunk['response']
                    except json.JSONDecodeError:
                        continue
            return full_response
                
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error calling Gemma service: {str(e)}")
