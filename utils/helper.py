import requests
import json
import uuid
from datetime import datetime
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
            # For non-streaming, try different response formats
            try:
                # First, try to parse as a single JSON object
                return response.json().get('response', '')
            except json.JSONDecodeError:
                # If that fails, try parsing as streaming format
                full_response = ""
                for line in response.text.strip().split('\n'):
                    if line.strip():
                        try:
                            chunk = json.loads(line)
                            if 'response' in chunk:
                                full_response += chunk['response']
                        except json.JSONDecodeError:
                            continue
                
                if full_response:
                    return full_response
                else:
                    # If all else fails, return the raw text
                    return response.text.strip()
                
    except requests.exceptions.RequestException as e:
        raise Exception(f"Error calling Gemma service: {str(e)}")


def generate_sample_query() -> str:
    """
    Generate a sample scientific query using the deployed Gemma 3 12B model.
    
    Returns:
        str: Generated query text
    """
    if GEMMA_SERVICE_URL is None:
        raise ValueError("GEMMA_SERVICE_URL not configured")
    
    # Get the query generation prompt
    from prompts import AgentPrompts
    prompt = AgentPrompts.QUERY_GENERATION_AGENT
    
    try:
        # Call Gemma 3 12B for query generation
        response = ask_gemma(prompt, streaming=False)
        
        # Debug: Log the response for troubleshooting
        print(f"DEBUG: Raw response from Gemma: {repr(response)}")
        
        # Check if response is empty
        if not response or not response.strip():
            raise Exception("Empty response from Gemma service")
        
        # Extract the generated query from the response
        generated_query = extract_query_from_response(response)
        
        return generated_query
        
    except Exception as e:
        raise Exception(f"Error generating sample query: {str(e)}")


def extract_query_from_response(response: str) -> str:
    """
    Extract the generated query from the Gemma response.
    Handles various response formats including JSON and markdown.
    
    Args:
        response: Raw response from Gemma service
        
    Returns:
        str: Extracted query text
    """
    # Try to parse as JSON first
    try:
        # Remove markdown code blocks if present
        cleaned_response = response.strip()
        if cleaned_response.startswith('```json'):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith('```'):
            cleaned_response = cleaned_response[:-3]
        
        query_data = json.loads(cleaned_response.strip())
        
        # If it's a JSON object with generated_query field
        if isinstance(query_data, dict) and 'generated_query' in query_data:
            return query_data['generated_query']
        
        # If it's a JSON object with 'query' field
        if isinstance(query_data, dict) and 'query' in query_data:
            return query_data['query']
            
    except json.JSONDecodeError:
        pass
    
    # If JSON parsing fails, try to extract the query using regex
    import re
    
    # Look for patterns like "generated_query": "..." or "query": "..."
    patterns = [
        r'"generated_query":\s*"([^"]+)"',
        r'"query":\s*"([^"]+)"',
        r'query":\s*"([^"]+)"',
        r'query:\s*"([^"]+)"'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, response, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
    
    # If no structured format found, return the response as-is
    # Remove markdown formatting if present
    cleaned = response.strip()
    if cleaned.startswith('```'):
        lines = cleaned.split('\n')
        if len(lines) > 1:
            # Skip the first line (```json or similar) and last line (```)
            return '\n'.join(lines[1:-1]).strip()
    
    return cleaned
