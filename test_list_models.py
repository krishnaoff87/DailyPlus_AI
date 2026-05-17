"""List available Gemini models."""

from google import genai
from config.settings import settings


def list_available_models():
    """List all available Gemini models."""
    try:
        # Create client
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        print("Fetching available Gemini models...\n")

        # List models
        models = client.models.list()

        print("Available models:")
        for model in models:
            print(f"  - {model.name}")
            if hasattr(model, "supported_generation_methods"):
                print(f"    Methods: {model.supported_generation_methods}")

        return True

    except Exception as e:
        print(f"[FAILED] Could not list models: {type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    list_available_models()

# Made with Bob
