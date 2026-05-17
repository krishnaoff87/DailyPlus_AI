"""Final test of Gemini API key with available models."""

from google import genai
from config.settings import settings


def test_gemini_final():
    """Test the Gemini API key with an available model."""
    try:
        # Create client
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        print("Testing Gemini API key with available model...")
        print(f"API Key format: {settings.GEMINI_API_KEY[:10]}...\n")

        # Use gemini-2.5-flash which is available
        model_name = "gemini-2.5-flash"

        print(f"Testing with model: {model_name}")
        response = client.models.generate_content(
            model=model_name, contents='Say "API key working"'
        )

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
    test_gemini_final()

# Made with Bob
