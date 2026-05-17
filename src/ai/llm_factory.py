from config.settings import settings


def get_llm(temperature: float = 0.7, timeout: int = 60, max_retries: int = 2):
    """
    Get the best available LLM instance.

    Priority: NVIDIA NIM > Google Gemini.
    NVIDIA NIM is preferred because the Gemini free-tier has strict rate limits.

    Returns:
        A LangChain chat model instance.
    """
    # Prefer NVIDIA NIM if key is available
    if settings.NVIDIA_API_KEY:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model="meta/llama-3.3-70b-instruct",
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=settings.NVIDIA_API_KEY,
            temperature=temperature,
            timeout=timeout,
            max_retries=max_retries,
        )

    # Fallback to Google Gemini
    if settings.GEMINI_API_KEY:
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=temperature,
            convert_system_message_to_human=True,
            timeout=timeout,
            max_retries=max_retries,
        )

    raise ValueError(
        "No AI API key configured. Set NVIDIA_API_KEY or GEMINI_API_KEY in config/.env"
    )
