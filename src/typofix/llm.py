import openai
from .prompts import DEFAULT_SYSTEM_PROMPT, SUGGEST_SYSTEM_PROMPT, REWRITE_SYSTEM_PROMPT
from .config import get_api_key, get_model

def fix_text(text: str, mode: str = "fix", test: bool = False) -> str:
    """
    Fix, suggest, or rewrite text using LLM.
    Args:
        text: The input text to process.
        mode: One of "fix", "suggest", "rewrite".
        test: If True, returns a stub response without calling the API.
    """
    if test:
        # Stub logic for testing
        if mode == "suggest":
            return "Suggestion: This is a test suggestion."
        elif mode == "rewrite":
            return "1. This is a test rewrite option 1.\n2. This is a test rewrite option 2."
        else:
            # For fix mode in test, return the original text prefixed with [Fixed] to simulate a fix, 
            # or just a dummy fixed string. The user complained "Where is my hello world?", 
            # implying they expect the stub to reflect the input or be more realistic.
            # Let's return the input text itself or a slight modification to show it "worked".
            return f"{text}"

    api_key = get_api_key()
    if not api_key:
        return "[CONFIG_NEEDED] API key not configured. Run `typofix config --api-key YOUR_KEY` to set it."

    model = get_model()
    
    # Select prompt based on mode
    if mode == "suggest":
        system_prompt = SUGGEST_SYSTEM_PROMPT
    elif mode == "rewrite":
        system_prompt = REWRITE_SYSTEM_PROMPT
    else:
        system_prompt = DEFAULT_SYSTEM_PROMPT

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.7 if mode != "fix" else 0.3, # Lower temperature for fix mode
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Error calling LLM: {str(e)}"
