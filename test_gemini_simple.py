"""Simple test of Gemini API key using available libraries."""

from google import genai
from config.settings import settings


def test_gemini_simple():
    """Test the Gemini API key with google.genai library."""
    try:
        # Create client
        client = genai.Client(api_key=settings.GEMINI_API_KEY)

        print("Testing Gemini API key...")
        print(f"API Key format: {settings.GEMINI_API_KEY[:10]}...")

        # Try to generate content with a simple prompt
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp", contents='Say "API key working"'
        )

        print(f"\n[SUCCESS] API Response: {response.text}")
        print("[SUCCESS] Gemini API key valid and responding correctly")
        return True

    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)

        # Try alternative model names
        alternative_models = ["gemini-2.5-flash", "gemini-2.5-flash", "gemini-pro"]

        for model in alternative_models:
            try:
                print(f"\nTrying alternative model: {model}")
                response = client.models.generate_content(
                    model=model, contents='Say "API key working"'
                )
                print(f"\n[SUCCESS] API Response: {response.text}")
                print("[SUCCESS] Gemini API key valid and responding correctly")
                print(f"[SUCCESS] Working model: {model}")
                return True
            except Exception as alt_e:
                print(f"  Model {model} failed: {type(alt_e).__name__}")
                continue

        # All attempts failed
        if (
            "API_KEY_INVALID" in error_msg
            or "401" in error_msg
            or "authentication" in error_msg.lower()
        ):
            print("\n[FAILED] API key invalid or expired")
            print(f"Error: {error_type}: {error_msg}")
        else:
            print(f"\n[FAILED] API test failed: {error_type}: {error_msg}")

        return False


if __name__ == "__main__":
    test_gemini_simple()

# Made with Bob
