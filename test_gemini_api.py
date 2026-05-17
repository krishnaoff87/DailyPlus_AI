"""Test script to verify Google Gemini API key functionality."""

from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings


def test_gemini_api():
    """Test the Google Gemini API key with a simple prompt."""
    # List of models to try in order of preference
    models_to_try = ["gemini-2.5-flash", "gemini-2.5-flash", "gemini-pro"]

    for model_name in models_to_try:
        try:
            print(f"Testing Google Gemini API with model: {model_name}...")

            # Initialize the LLM
            llm = ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=settings.GEMINI_API_KEY,
                temperature=0.7,
                convert_system_message_to_human=True,
            )

            # Make a test call
            response = llm.invoke("Say 'API key working'")

            # Print success message (using ASCII characters for Windows compatibility)
            print(f"[SUCCESS] API Response: {response.content}")
            print(
                f"\n[SUCCESS] Google Gemini API key valid and responding correctly with model: {model_name}"
            )
            return True

        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)

            # Check for authentication errors
            if (
                "authentication" in error_msg.lower()
                or "api key" in error_msg.lower()
                or "401" in error_msg
            ):
                print("[FAILED] API key invalid or expired")
                print(f"Error details: {error_type}: {error_msg}")
                return False
            else:
                print(f"[WARNING] Model {model_name} failed: {error_type}: {error_msg}")
                print("Trying next model...")
                continue

    # If all models failed
    print("[FAILED] All models failed. API key test unsuccessful.")
    return False


if __name__ == "__main__":
    test_gemini_api()

# Made with Bob
