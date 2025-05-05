import time
import random

def get_response(prompt, model_params=None):
    """Generate a response from the LLM based on the input prompt."""

    return {
        "status": "completed",
        "max_output_tokens": None,
        "model": "model name",
        "output": [
            {
            "type": "message",
            "content": [
                {
                "type": "output_text",
                "text": "response text",
                }
            ]
            }
        ],
    }
