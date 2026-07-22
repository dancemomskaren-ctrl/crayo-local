import os
import time
from typing import Optional
from openai import OpenAI, APIError, APIConnectionError, RateLimitError
from schema import CampaignConfig, GeneratedScript, Transcript

SYSTEM_PROMPT = """You are a viral short-form video editor for CSGORoll streams.
CSGORoll is a Counter-Strike gambling platform with games like Case Battles, Crash, Dice, Plinko, Roulette, and skin unboxings.

Given a transcript of a CSGORoll stream, find the {max_clips} most CLIPWORTHY gambling moments.

For each clip provide:
- title: catchy name
- start: start time in SECONDS from beginning of stream
- duration: clip length in seconds (aim for {target_duration}s)
- hook: TikTok-style caption hook at TOP (4 WORDS MAX, organic sounding, like "Bro got triggered" or "This man went INSANE" or "Wait for it")
- text_overlay: 2-3 WORDS MAX, HUGE and dramatic (like "HUGE WIN" "RIP SKINS" "UNREAL" "GREEN!" "CRASH!")
- outro_text: 2-3 words at end (like "SUBSCRIBE" "NEXT" "MORE WINS")

CRITICAL: Do NOT use single quotes, percent signs, backslashes, or colons in any text fields. Only use letters, numbers, spaces, and basic punctuation.

Output JSON matching the GeneratedScript schema with these exact keys: clips, caption, hashtags.

CSGORoll HIGHLIGHT MOMENTS (prioritize these):
- Case Battle wins (opening cases, winning opponents skins)
- Crash hits (green on crash, big multipliers)
- Roulette wins (green hits, streaks)
- Rare skin unboxings (knife, gloves, covert)
- High value trades and gambles
- Rage moments (yelling, quitting after losses)
- Near misses and bad beats
- Streaks (winning or losing)

CAPTION/HOOK RULES (CRITICAL):
- MAX 4 WORDS per hook/caption
- NEVER exceed 4 words
- Examples: "Bro got triggered" "This man INSANE" "No way" "Wait for it"

TEXT STYLE:
- 2-3 words MAX, all caps, dramatic
- Examples: "HUGE WIN" "RIP" "INSANE" "NO WAY" "GREEN" "5000 SKIN" "CRASHED"

CAPTION STYLE:
- 4 words max, gambling energy
- Example: "He hit green" or "No way he won"

HASHTAGS:
- Include: #csgoroll #casebattle #crash #gambling #skins #bigwin #csgo #cs2
- 5-8 hashtags max"""

# Global client instance (singleton pattern)
_client: Optional[OpenAI] = None

# Retry configuration for API calls
MAX_API_RETRIES = 3
API_RETRY_DELAY = 1  # seconds between retries


def get_client() -> OpenAI:
    """
    Get or create the OpenAI client singleton.

    Returns:
        Configured OpenAI client instance

    Raises:
        RuntimeError: If DEEPSEEK_API_KEY environment variable is not set
    """
    global _client
    if _client is None:
        key = os.environ.get("DEEPSEEK_API_KEY")
        if not key:
            raise RuntimeError(
                "Set DEEPSEEK_API_KEY env var first: export DEEPSEEK_API_KEY=your-key"
            )
        # Create client with timeout and retry configuration
        _client = OpenAI(
            base_url="https://api.deepseek.com",
            api_key=key,
            timeout=60.0,  # 60 second timeout for long transcripts
            max_retries=0,  # We handle retries ourselves for better control
        )
    return _client


def generate_script(transcript: Transcript, config: CampaignConfig) -> GeneratedScript:
    """
    Generate a clipping script from transcript using DeepSeek AI.

    Args:
        transcript: Video transcript with word-level timestamps
        config: Campaign configuration with streamer info and preferences

    Returns:
        GeneratedScript with clips, caption, and hashtags

    Raises:
        RuntimeError: If API returns no valid content
        RateLimitError: If rate limited by API (after retries)
        APIConnectionError: If cannot connect to API
    """
    client = get_client()

    # Prepare the prompt with config values
    system_content = SYSTEM_PROMPT.format(
        max_clips=config.max_clips,
        target_duration=config.target_duration,
    )

    # Include timestamp information in the prompt for better clip selection
    timestamp_info = ""
    if transcript.words:
        # Add word-level timestamps to help AI select precise moments
        # Send ALL words for full context (DeepSeek handles long context well)
        timestamp_info = "\n\nWord timestamps (word: start-end seconds):\n"
        for word in transcript.words:
            timestamp_info += f'"{word.text}": {word.start:.1f}-{word.end:.1f}\n'

    user_content = (
        f"Streamer: {config.streamer_name}\n"
        f"Platform: CSGORoll\n"
        f"Tone: {config.tone}\n\n"
        f"Transcript:\n{transcript.text}"
        f"{timestamp_info}"
    )

    # Retry logic for transient errors
    last_error = None
    for attempt in range(MAX_API_RETRIES):
        try:
            resp = client.chat.completions.create(
                model="deepseek-chat",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": user_content},
                ],
            )

            # Validate response
            if not resp.choices:
                raise RuntimeError("DeepSeek returned no choices")

            content = resp.choices[0].message.content
            if not content:
                raise RuntimeError("DeepSeek returned empty content")

            # Parse and validate JSON response
            return GeneratedScript.model_validate_json(content)

        except RateLimitError as e:
            last_error = e
            if attempt < MAX_API_RETRIES - 1:
                delay = API_RETRY_DELAY * (2**attempt)  # Exponential backoff
                print(
                    f"Warning: Rate limited, retrying in {delay}s (attempt {attempt + 1}/{MAX_API_RETRIES})..."
                )
                time.sleep(delay)
            else:
                print("Error: Rate limited after all retries")
                raise

        except APIConnectionError as e:
            last_error = e
            if attempt < MAX_API_RETRIES - 1:
                delay = API_RETRY_DELAY * (2**attempt)
                print(
                    f"Warning: Connection error, retrying in {delay}s (attempt {attempt + 1}/{MAX_API_RETRIES})..."
                )
                time.sleep(delay)
            else:
                print("Error: Cannot connect to API after all retries")
                raise

        except APIError as e:
            # For other API errors, don't retry (likely a permanent error)
            print(f"Error: API error: {e}")
            raise

        except Exception as e:
            # Catch-all for unexpected errors
            print(f"Error: Unexpected error: {e}")
            raise

    # This should not be reached, but just in case
    raise last_error or RuntimeError("Failed to generate script")
