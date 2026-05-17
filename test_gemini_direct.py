"""Direct test of Gemini API key using google-generativeai library."""

import google.generativeai as genai
from config.settings import settings


def test_gemini_direct():
    """Test the Gemini API key directly with google-generativeai."""
    try:
        # Configure the API key
        genai.configure(api_key=settings.GEMINI_API_KEY)

        # List available models
        print("Fetching available models...")
        models = genai.list_models()

        available_models = []
        for model in models:
            if "generateContent" in model.supported_generation_methods:
                available_models.append(model.name)
                print(f"  - {model.name}")

        if not available_models:
            print("[FAILED] No models available for content generation")
            return False

        # Try to use the first available model
        model_name = available_models[0].replace("models/", "")
        print(f"\nTesting with model: {model_name}")

        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'API key working'")

        print(f"\n[SUCCESS] API Response: {response.text}")
        print("[SUCCESS] Gemini API key valid and responding correctly")
        print(f"[SUCCESS] Working model: {model_name}")
        return True

    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)

        if (
            "API_KEY_INVALID" in error_msg
            or "401" in error_msg
            or "authentication" in error_msg.lower()
        ):
            print("[FAILED] API key invalid or expired")
            print(f"Error: {error_type}: {error_msg}")
        else:
            print(f"[FAILED] API test failed: {error_type}: {error_msg}")

        return False


if __name__ == "__main__":
    test_gemini_direct()

# Made with Bob
