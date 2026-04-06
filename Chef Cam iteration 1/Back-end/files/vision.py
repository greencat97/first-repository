import base64
import os
from typing import Union

import httpx

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OPENAI_API_URL = "https://api.openai.com/v1/responses"

SYSTEM_PROMPT = (
    "You are a kitchen ingredient scanner. Carefully examine this image and "
    "identify every food ingredient visible. Return ONLY a comma-separated list "
    "of ingredients with no additional text, no numbering, no categories, and no "
    "explanations. Use simple common names for each ingredient, for example "
    "'tomato' not 'roma tomato', 'cheese' not 'shredded mozzarella cheese'."
)


# ---------------------------------------------------------------------------
# Public function
# ---------------------------------------------------------------------------

def detect_ingredients(image_data: Union[str, bytes]) -> list[str]:
    """
    Send an image to GPT-4o and return a clean list of detected ingredient names.

    Args:
        image_data: Either a base64-encoded string or raw bytes of the image.

    Returns:
        A list of lowercase ingredient strings e.g. ["tomato", "egg", "cheese"].

    Raises:
        ValueError: If the API key is missing or the response cannot be parsed.
        httpx.HTTPStatusError: If the API returns a non-2xx status.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is not set.")

    # Ensure we have a base64 string
    if isinstance(image_data, bytes):
        b64 = base64.b64encode(image_data).decode("utf-8")
    else:
        b64 = image_data

    payload = {
        "model": "gpt-4o",
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": SYSTEM_PROMPT,
                    },
                    {
                        "type": "input_image",
                        "image_url": f"data:image/jpeg;base64,{b64}",
                    },
                ],
            }
        ],
    }

    with httpx.Client(timeout=30.0) as client:
        response = client.post(
            OPENAI_API_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
        )
        response.raise_for_status()

    data = response.json()

    # Parse the response format shown in the project spec:
    # data["content"][0]["text"] -> "Mayonnaise, minced garlic, butter, ..."
    try:
        raw_text: str = data["content"][0]["text"]
    except (KeyError, IndexError) as e:
        raise ValueError(f"Unexpected response structure from GPT-4o: {data}") from e

    ingredients = _parse_ingredient_list(raw_text)
    return ingredients


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _parse_ingredient_list(raw_text: str) -> list[str]:
    """
    Convert a comma-separated string into a clean lowercase list.

    "Mayonnaise, minced garlic, Butter" -> ["mayonnaise", "minced garlic", "butter"]
    """
    items = raw_text.split(",")
    cleaned = []
    for item in items:
        item = item.strip().lower()
        if item:  # skip any empty strings from trailing commas
            cleaned.append(item)
    return cleaned
