# utils/openrouter_client.py

import os
import requests # Using requests library for HTTP calls

# It's good practice to get API keys from environment variables
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
API_BASE_URL = "https://openrouter.ai/api/v1"

class OpenRouterClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or OPENROUTER_API_KEY
        if not self.api_key:
            raise ValueError("OpenRouter API key not found. Please set the OPENROUTER_API_KEY environment variable.")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def send_chat_completion(self, model_name: str, messages: list, max_tokens: int = 100, temperature: float = 0.7):
        """
        Sends a request to the OpenRouter chat completions endpoint.

        Args:
            model_name (str): The name of the model to use (e.g., "openai/gpt-3.5-turbo").
            messages (list): A list of message objects, similar to OpenAI's API.
                             Each message is a dict with "role" and "content".
            max_tokens (int): The maximum number of tokens to generate.
            temperature (float): Controls randomness. Lower is more deterministic.

        Returns:
            dict: The JSON response from the API, or None if an error occurs.
        """
        payload = {
            "model": model_name,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            # Add other parameters like 'tools' for tool_calling later
        }

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
    # Example usage (requires OPENROUTER_API_KEY to be set in environment)
    # This part will not run in the sandbox due to lack of API key and internet access for requests
    print("Attempting to initialize OpenRouterClient...")
    try:
        client = OpenRouterClient()
        print("OpenRouterClient initialized (API key found).")

        # This is a placeholder for a real call, which would require network access
        # and a valid API key.
        # For now, we'll just simulate what a call might look like.
        if os.environ.get("OPENROUTER_API_KEY"):
            print("Simulating a call to OpenRouter (actual call would require network)...")
            # messages_example = [
            #     {"role": "user", "content": "Hello, who are you?"}
            # ]
            # response = client.send_chat_completion("openai/gpt-3.5-turbo", messages_example)
            # if response:
            #     print("API Response:", response)
            # else:
            #     print("Failed to get response from API.")
        else:
            print("OPENROUTER_API_KEY not set. Skipping example API call.")

    except ValueError as ve:
        print(f"Initialization failed: {ve}")
    except Exception as e:
        print(f"An unexpected error occurred during example usage: {e}")
