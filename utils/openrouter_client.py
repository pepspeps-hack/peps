# utils/openrouter_client.py

import os
import requests # Using requests library for HTTP calls

# !!! IMPORTANT SECURITY NOTE !!!
# The API key below is provided for this development session.
# In a production environment, or any shared/public code,
# API keys should NOT be hardcoded. They should be stored securely,
# typically using environment variables or a secure secrets management system.
# Example: OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
PROVIDED_API_KEY = "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"
DEFAULT_MODEL = "openrouter/cypher-alpha:free" # User specified model

API_BASE_URL = "https://openrouter.ai/api/v1"

class OpenRouterClient:
    def __init__(self, api_key=None, model_name=None):
        self.api_key = api_key or PROVIDED_API_KEY
        self.model_name = model_name or DEFAULT_MODEL

        if not self.api_key:
            # This condition might not be hit if PROVIDED_API_KEY is always set,
            # but good practice if it could come from os.environ.get() which might be None.
            raise ValueError("OpenRouter API key not found. Please ensure it's set.")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            # OpenRouter specific headers if needed, e.g., for site identification
            "HTTP-Referer": "http://localhost", # Optional: Replace with your app's URL
            "X-Title": "AI Control App", # Optional: Replace with your app's name
        }

    def send_chat_completion(self, messages: list, model_name: str = None, max_tokens: int = 150, temperature: float = 0.5):
        """
        Sends a request to the OpenRouter chat completions endpoint.

        Args:
            messages (list): A list of message objects, similar to OpenAI's API.
                             Each message is a dict with "role" and "content".
            model_name (str, optional): The name of the model to use. Defaults to client's default.
            max_tokens (int): The maximum number of tokens to generate.
            temperature (float): Controls randomness. Lower is more deterministic.

        Returns:
            dict: The JSON response from the API, or None if an error occurs.
        """
        payload = {
            "model": model_name or self.model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            # TODO: Add 'tools' parameter here if cypher-alpha supports OpenAI-compatible tool calling
            # "tools": [ ... list of tool definitions ... ],
            # "tool_choice": "auto",
        }

        print(f"Sending payload to OpenRouter: {payload}") # For debugging

        try:
            response = requests.post(
                f"{API_BASE_URL}/chat/completions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status() # Raises an HTTPError for bad responses (4XX or 5XX)
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error connecting to OpenRouter API: {e}")
            # In a real app, you might want to log this error more robustly
            # or implement retry logic here.
            return None
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None

if __name__ == '__main__':
    print("Attempting to initialize OpenRouterClient with provided key and model...")
    try:
        # Initialize with the hardcoded key and default model for this test
        client = OpenRouterClient()
        print(f"OpenRouterClient initialized. Using model: {client.model_name}")

        # Example: Test with a simple prompt
        # This will make a live API call if the sandbox has internet and the key is valid.
        # Be mindful of API usage limits with the 'free' model tier.
        messages_example = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello! Can you tell me a short joke?"}
        ]

        print(f"\nAttempting to send chat completion to model: {client.model_name}...")
        response = client.send_chat_completion(messages_example)

        if response:
            print("\nAPI Response:")
            # Prettily print the JSON response
            import json
            print(json.dumps(response, indent=2))

            # Try to extract and print the assistant's message content
            if response.get("choices") and response["choices"][0].get("message"):
                assistant_message = response["choices"][0]["message"].get("content")
                if assistant_message:
                    print(f"\nAssistant's message: {assistant_message}")
                # Later, we will check for "tool_calls" here
                # tool_calls = response["choices"][0]["message"].get("tool_calls")
                # if tool_calls:
                # print(f"\nTool calls requested: {tool_calls}")
            else:
                print("\nCould not extract assistant's message from the response.")
        else:
            print("\nFailed to get a response from the API.")

    except ValueError as ve:
        print(f"Initialization or API call failed: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred during example usage: {e}")
