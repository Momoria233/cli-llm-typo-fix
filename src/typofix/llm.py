import openai
from typing import List, Optional
from .prompts import GLOBAL_SYSTEM_PROMPT, DEFAULT_SYSTEM_PROMPT, SUGGEST_SYSTEM_PROMPT, REWRITE_SYSTEM_PROMPT
from .config import get_api_key, get_model, get_base_url

def fix_text(text: str, mode: str = "fix") -> str:
    """
    Fix, suggest, or rewrite text using LLM.
    Args:
        text: The input text to process.
        mode: One of "fix", "suggest", "rewrite".
    """
    api_key = get_api_key()
    if not api_key:
        return "[CONFIG_NEEDED] API key not configured. Run `typofix setup` to initialize configuration."

    model = get_model()
    base_url = get_base_url()
    
    # Select prompt based on mode
    if mode == "suggest":
        specific_prompt = SUGGEST_SYSTEM_PROMPT
    elif mode == "rewrite":
        specific_prompt = REWRITE_SYSTEM_PROMPT
    else:
        specific_prompt = DEFAULT_SYSTEM_PROMPT
        
    # Combine with GLOBAL_SYSTEM_PROMPT
    system_prompt = f"{GLOBAL_SYSTEM_PROMPT}\n\n{specific_prompt}"

    try:
        client = openai.OpenAI(api_key=api_key, base_url=base_url)
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

def list_models(api_key: Optional[str] = None, base_url: Optional[str] = None) -> List[str]:
    """
    List available models from OpenAI API.
    Args:
        api_key: Optional API key. If None, retrieves from config.
        base_url: Optional base URL. If None, retrieves from config.
    Returns:
        List of model IDs.
    Raises:
        Exception: If API call fails.
    """
    if not api_key:
        api_key = get_api_key()
    
    if not api_key:
        raise ValueError("API key not configured.")

    if not base_url:
        base_url = get_base_url()
        
    client = openai.OpenAI(api_key=api_key, base_url=base_url)
    models = client.models.list()
    # Sort models by id
    return sorted([m.id for m in models.data])
