from pydantic import BaseModel
from enum import Enum
from typing import Optional


class Platform(str, Enum):
    """
    Supported video platforms for export.
    Each platform has different aspect ratios and duration limits.
    """

    YOUTUBE_SHORTS = "youtube_shorts"  # 9:16, max 60s
    TIKTOK = "tiktok"  # 9:16, max 3min
    X = "x"  # 16:9 or 1:1, max 2min 20s
    INSTAGRAM_REELS = "instagram_reels"  # 9:16, max 90s


class Word(BaseModel):
    """
    A single word with timing information from Whisper transcription.

    Attributes:
        text: The word text
        start: Start time in seconds
        end: End time in seconds
        probability: Confidence score (0.0 to 1.0)
    """

    text: str
    start: float
    end: float
    probability: float = 1.0


class Segment(BaseModel):
    """
    A segment of transcribed text with word-level timing.

    Attributes:
        text: Full segment text
        start: Segment start time in seconds
        end: Segment end time in seconds
        words: List of words with individual timing
    """

    text: str
    start: float
    end: float
    words: list[Word] = []


class Transcript(BaseModel):
    """
    Complete transcription with word-level timestamps.

    Attributes:
        text: Full transcript text
        segments: List of segments with timing
        words: Flattened list of all words with timing
    """

    text: str
    segments: list[Segment] = []
    words: list[Word] = []


class OverlayStyle(str, Enum):
    """
    Text overlay styles for video composition.
    Controls font size, color, stroke, and overall aesthetic.
    """

    # Core styles
    BOLD = "bold"  # Large white text with black stroke (default)
    MINIMAL = "minimal"  # Smaller text, clean look, no stroke

    # Content-specific styles
    GAMBLING = "gambling"  # Green/gold theme for casino/gambling content
    DRAMATIC = "dramatic"  # Red/white for intense moments
    GAMING = "gaming"  # Neon cyan/purple for gaming content
    SPORTS = "sports"  # Bold orange/blue for sports highlights
    PODCAST = "podcast"  # Clean white on dark for podcast clips
    REACTION = "reaction"  # Fun yellow/pink for reaction videos
    NEWS = "news"  # Professional blue/white for news clips
    VIRAL = "viral"  # Trendy gradient-style for viral content
    HORROR = "horror"  # Dark red/black for spooky content
    RETRO = "retro"  # Pixel-art style green/amber for nostalgia
    NEON = "neon"  # Bright neon colors on dark background
    PASTEL = "pastel"  # Soft pastel colors for lifestyle content
    FIRE = "fire"  # Orange/red gradient for hype moments
    ICE = "ice"  # Blue/cyan for cool/calm moments
    GOLD = "gold"  # Premium gold/black for luxury content


class EditingStyle(str, Enum):
    """
    Video editing style templates.
    Controls color grading, effects, transitions, and overall visual treatment.
    """

    # Core styles
    NONE = "none"  # No post-processing (raw footage)
    CLEAN = "clean"  # Subtle grade, sharpen, smooth transitions
    MINIMAL = "minimal"  # No effects, simple text (for pure content)

    # Cinematic styles
    CINEMATIC = "cinematic"  # S-curve, warm grade, vignette, grain
    DRAMATIC = "dramatic"  # High contrast, B&W option, vignette, freeze
    FILM = "film"  # Film emulation LUT, grain, letterbox

    # Social media styles
    VIRAL_HYPE = "viral_hype"  # High contrast, speed ramp, shake, strobe
    GAMING = "gaming"  # Neon grade, edge glow, pop text, bass boost
    RETRO = "retro"  # VHS color shift, grain, letterbox, vintage

    # Content-specific
    SPORTS = "sports"  # High contrast, saturated colors, quick cuts
    PODCAST = "podcast"  # Warm tones, subtle grain, clean text
    REACTION = "reaction"  # Bright, saturated, quick zooms

    # Mood-based
    DARK = "dark"  # Desaturated, high contrast, vignette
    VINTAGE = "vintage"  # Faded colors, grain, light leak
    NEON = "neon"  # High saturation, color shift, glow


class CampaignConfig(BaseModel):
    """
    Configuration for a video clipping campaign.

    Attributes:
        streamer_name: Name of the streamer being clipped
        game: Game being played (e.g., CS2, Valorant)
        tone: Content tone - affects AI prompt and text styling
        target_duration: Target length for each clip in seconds
        platforms: Target platforms for export (affects aspect ratio)
        max_clips: Maximum number of clips to generate
        overlay_style: Visual style for text overlays
        editing_style: Video editing style for effects and color grading
    """

    streamer_name: str
    game: str
    tone: str = "hype"
    target_duration: int = 40
    platforms: list[Platform] = [Platform.YOUTUBE_SHORTS]
    max_clips: int = 5
    overlay_style: OverlayStyle = OverlayStyle.BOLD
    editing_style: EditingStyle = EditingStyle.CLEAN


class HighlightClip(BaseModel):
    """
    A single highlight clip definition.

    Attributes:
        title: Catchy name for the clip
        start: Start time in seconds from beginning of video
        duration: Clip length in seconds
        hook: Short caption at top of video (4 words max)
        text_overlay: Large dramatic text in center (2-3 words)
        outro_text: Call-to-action text at end (optional)
    """

    title: str
    start: int
    duration: int
    hook: str
    text_overlay: str
    outro_text: str = ""


class GeneratedScript(BaseModel):
    """
    Complete script generated by AI for a video.

    Attributes:
        clips: List of highlight clips to create
        caption: Caption for social media post
        hashtags: Relevant hashtags for discoverability
    """

    clips: list[HighlightClip]
    caption: str = ""
    hashtags: list[str] = []
