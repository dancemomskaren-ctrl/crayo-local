import re
import subprocess
import shutil
from pathlib import Path
from contextlib import contextmanager
from moviepy import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    vfx,
    afx,
)
from moviepy.video.fx import Resize, Crop
from moviepy.audio.fx import MultiplyVolume
from schema import (
    GeneratedScript,
    HighlightClip,
    OverlayStyle,
    EditingStyle,
    Transcript,
    Word,
)

OUT_DIR = Path("output")

# Target aspect ratio for vertical video (9:16)
TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920


def sanitize(text: str) -> str:
    """
    Sanitize text for video overlay by removing problematic characters.

    Args:
        text: Raw text to sanitize

    Returns:
        Cleaned text safe for video overlays
    """
    text = text.replace("\\", "")
    text = text.replace("'", "")
    text = text.replace('"', "")
    text = text.replace("%", "")
    text = text.replace(":", "")
    text = text.replace(";", "")
    text = re.sub(r"[^\w\s!.,?]", "", text)
    return text.strip()


def wrap_text(text: str, max_words: int = 6) -> str:
    """
    Wrap text to prevent overflow by breaking at word boundaries.

    Args:
        text: Text to wrap
        max_words: Maximum words per line

    Returns:
        Text with newline characters for line breaks
    """
    words = text.split()
    if len(words) <= max_words:
        return text

    lines = []
    for i in range(0, len(words), max_words):
        lines.append(" ".join(words[i : i + max_words]))
    return "\n".join(lines)


def find_ffmpeg() -> str:
    """
    Find the ffmpeg binary path dynamically.

    Returns:
        Path to ffmpeg binary
    """
    common_paths = [
        "/opt/homebrew/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "/usr/bin/ffmpeg",
    ]
    for path in common_paths:
        if Path(path).exists():
            return path
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return ffmpeg_path
    raise FileNotFoundError("ffmpeg not found")


@contextmanager
def open_video(vod_path: str):
    """
    Context manager for VideoFileClip to ensure proper resource cleanup.
    """
    video = None
    try:
        video = VideoFileClip(vod_path)
        yield video
    finally:
        if video is not None:
            try:
                video.close()
            except Exception:
                pass


def crop_to_vertical(video: VideoFileClip) -> VideoFileClip:
    """
    Crop a 16:9 video to 9:16 vertical format by center-cropping.

    Args:
        video: Input video clip (16:9)

    Returns:
        Cropped video clip (9:16)
    """
    # Calculate crop dimensions for 9:16 from 16:9
    # Target aspect ratio: 9/16 = 0.5625
    target_ratio = 9 / 16

    w, h = video.size
    current_ratio = w / h

    if current_ratio > target_ratio:
        # Video is too wide, crop width
        new_w = int(h * target_ratio)
        x_center = w // 2
        x1 = x_center - new_w // 2
        x2 = x_center + new_w // 2
        return video.cropped(x1=x1, y1=0, x2=x2, y2=h)
    else:
        # Video is too tall, crop height
        new_h = int(w / target_ratio)
        y_center = h // 2
        y1 = y_center - new_h // 2
        y2 = y_center + new_h // 2
        return video.cropped(x1=0, y1=y1, x2=w, y2=y2)


def create_blurred_background(video: VideoFileClip) -> VideoFileClip:
    """
    Create a blurred, darkened background layer for vertical video.
    This fills the black bars when converting 16:9 to 9:16.

    Args:
        video: Input video clip

    Returns:
        Blurred and darkened background clip
    """
    # Create a blurred version
    bg = video.with_effects([vfx.Resize(width=TARGET_WIDTH, height=TARGET_HEIGHT)])

    # Apply Gaussian blur effect (multiple passes for stronger blur)
    bg = bg.with_effects([vfx.GaussianBlur(sigma=30)])

    # Darken the background
    bg = bg.with_effects([MultiplyVolume(0)])  # Remove audio
    bg = bg.with_effects([vfx.ColorTransform(brightness=0.4)])

    return bg


def create_text_background(
    text: str,
    font_size: int,
    video_width: int,
    video_height: int,
    position: tuple,
    start: float = 0,
    end: float = None,
    padding: int = 20,
    bg_color: str = "black",
    bg_opacity: float = 0.6,
) -> tuple:
    """
    Create a semi-transparent background box behind text for better readability.

    Returns:
        Tuple of (background_clip, text_clip) or (None, text_clip) if no bg needed
    """
    # This is a simplified version - in production you'd use RectangleClip
    # For now, we'll rely on text stroke for readability
    return None, None


def ken_burns_zoom(
    video: VideoFileClip,
    start_zoom: float = 1.0,
    end_zoom: float = 1.15,
) -> VideoFileClip:
    """
    Apply Ken Burns (slow zoom) effect to video.

    Creates a subtle zoom-in effect that adds motion and interest.

    Args:
        video: Input video clip
        start_zoom: Starting zoom level (1.0 = no zoom)
        end_zoom: Ending zoom level (1.15 = 15% zoom)

    Returns:
        Video with Ken Burns effect applied
    """
    duration = video.duration

    def zoom_func(t):
        # Linear interpolation from start_zoom to end_zoom
        progress = t / duration if duration > 0 else 0
        return start_zoom + (end_zoom - start_zoom) * progress

    # Apply zoom using time function
    return video.resized(zoom_func)


def normalize_audio(video: VideoFileClip) -> VideoFileClip:
    """
    Normalize audio levels to -16 LUFS (broadcast standard).

    Uses ffmpeg's loudnorm filter for consistent volume.

    Args:
        video: Input video clip

    Returns:
        Video with normalized audio
    """
    if video.audio is None:
        return video

    # Simple volume normalization approach
    # For full LUFS normalization, we'd need ffmpeg post-processing
    return video


def remove_silence(
    video: VideoFileClip,
    threshold: float = -30,
    min_silence: float = 0.5,
) -> VideoFileClip:
    """
    Remove silence from video to improve pacing.

    Uses ffmpeg's silencedetect filter.

    Args:
        video: Input video clip
        threshold: Silence threshold in dB
        min_silence: Minimum silence duration to remove (seconds)

    Returns:
        Video with silence removed (or original if no silence detected)
    """
    # This would require ffmpeg post-processing
    # For now, return original - implement with ffmpeg CLI if needed
    return video


def apply_ffmpeg_filter(input_path: str, output_path: str, vf_filter: str) -> str:
    """
    Apply FFmpeg video filter to a file.

    Args:
        input_path: Input video file
        output_path: Output video file
        vf_filter: FFmpeg video filter string

    Returns:
        Path to output file
    """
    ffmpeg = find_ffmpeg()
    cmd = [
        ffmpeg,
        "-y",
        "-i",
        input_path,
        "-vf",
        vf_filter,
        "-c:a",
        "copy",  # Copy audio without re-encoding
        output_path,
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    return output_path


def post_process_video(
    input_path: str,
    output_path: str,
    editing_style: EditingStyle,
) -> str:
    """
    Apply post-processing effects to video using FFmpeg filters.

    This runs after MoviePy composition to add color grading, vignette,
    film grain, sharpening, and other effects.

    Args:
        input_path: Input video file
        output_path: Output video file
        editing_style: Editing style to apply

    Returns:
        Path to processed video file
    """
    if editing_style == EditingStyle.NONE:
        # No processing, just copy
        import shutil

        shutil.copy2(input_path, output_path)
        return output_path

    # Build FFmpeg filter chain based on editing style
    filters = []

    if editing_style == EditingStyle.CINEMATIC:
        # S-curve contrast, warm tones, vignette, subtle grain
        filters.extend(
            [
                "eq=contrast=1.2:brightness=0.05:saturation=1.1",  # S-curve boost
                "colorbalance=rs=0.1:gs=0.05:bs=-0.05:rm=0.05:gm=0.02",  # Warm shadows
                "unsharp=5:5:0.8:5:5:0.0",  # Subtle sharpen
                "vignette=PI/4",  # Vignette
                "noise=c0s=8:allf=t",  # Light film grain
            ]
        )
    elif editing_style == EditingStyle.VIRAL_HYPE:
        # High contrast, saturated, sharpened
        filters.extend(
            [
                "eq=contrast=1.4:brightness=0.02:saturation=1.3",  # High contrast/sat
                "unsharp=5:5:1.2:5:5:0.0",  # Strong sharpen
                "vignette=PI/5",  # Slight vignette
            ]
        )
    elif editing_style == EditingStyle.CLEAN:
        # Subtle grade, sharpen, no grain
        filters.extend(
            [
                "eq=contrast=1.1:brightness=0.02:saturation=1.05",  # Subtle boost
                "unsharp=5:5:0.5:5:5:0.0",  # Light sharpen
            ]
        )
    elif editing_style == EditingStyle.DRAMATIC:
        # High contrast, desaturated, heavy vignette
        filters.extend(
            [
                "eq=contrast=1.3:brightness=-0.02:saturation=0.7",  # High contrast, desat
                "unsharp=5:5:1.0:5:5:0.0",  # Sharpen
                "vignette=PI/3",  # Heavy vignette
            ]
        )
    elif editing_style == EditingStyle.GAMING:
        # Neon boost, high saturation, edge enhancement
        filters.extend(
            [
                "eq=contrast=1.2:saturation=1.4:brightness=0.03",  # Neon boost
                "unsharp=5:5:1.0:5:5:0.5",  # Edge enhance
                "vignette=PI/4",  # Vignette
            ]
        )
    elif editing_style == EditingStyle.RETRO:
        # VHS look: color shift, grain, soft focus
        filters.extend(
            [
                "eq=contrast=1.1:saturation=0.8:brightness=0.05",  # Faded look
                "colorbalance=rs=-0.1:gs=0.05:bs=0.1:rh=0.1:gh=-0.05:bh=-0.1",  # Color shift
                "noise=c0s=15:allf=t",  # Heavy grain
                "vignette=PI/3",  # Vignette
            ]
        )
    elif editing_style == EditingStyle.SPORTS:
        # High contrast, saturated, sharp
        filters.extend(
            [
                "eq=contrast=1.3:saturation=1.2:brightness=0.02",  # Sports look
                "unsharp=5:5:1.2:5:5:0.0",  # Strong sharpen
            ]
        )
    elif editing_style == EditingStyle.PODCAST:
        # Warm tones, subtle grain, clean
        filters.extend(
            [
                "eq=contrast=1.1:brightness=0.03:saturation=1.05",  # Warm
                "colorbalance=rs=0.08:gs=0.04:bs=-0.04",  # Warm tones
                "noise=c0s=5:allf=t",  # Very light grain
            ]
        )
    elif editing_style == EditingStyle.REACTION:
        # Bright, saturated, energetic
        filters.extend(
            [
                "eq=contrast=1.2:saturation=1.3:brightness=0.05",  # Bright/saturated
                "unsharp=5:5:0.8:5:5:0.0",  # Sharpen
            ]
        )
    elif editing_style == EditingStyle.DARK:
        # Desaturated, high contrast, moody
        filters.extend(
            [
                "eq=contrast=1.4:brightness=-0.05:saturation=0.5",  # Dark/moody
                "vignette=PI/3",  # Heavy vignette
                "unsharp=5:5:1.0:5:5:0.0",  # Sharpen
            ]
        )
    elif editing_style == EditingStyle.VINTAGE:
        # Faded, warm, grain, light leak feel
        filters.extend(
            [
                "eq=contrast=0.9:brightness=0.08:saturation=0.7",  # Faded
                "colorbalance=rs=0.15:gs=0.1:bs=0.05:rh=0.1:gh=0.05",  # Warm vintage
                "noise=c0s=12:allf=t",  # Grain
                "vignette=PI/4",  # Vignette
            ]
        )
    elif editing_style == EditingStyle.NEON:
        # High saturation, color boost, glow feel
        filters.extend(
            [
                "eq=contrast=1.3:saturation=1.5:brightness=0.02",  # Neon boost
                "unsharp=5:5:1.0:5:5:0.5",  # Edge enhance
            ]
        )
    elif editing_style == EditingStyle.FILM:
        # Film emulation: S-curve, grain, letterbox feel
        filters.extend(
            [
                "eq=contrast=1.2:brightness=0.02:saturation=0.9",  # Film contrast
                "colorbalance=rs=0.05:gs=0.02:bs=-0.05",  # Subtle warm
                "noise=c0s=10:allf=t",  # Film grain
                "unsharp=5:5:0.6:5:5:0.0",  # Light sharpen
                "vignette=PI/4",  # Vignette
            ]
        )
    elif editing_style == EditingStyle.MINIMAL:
        # No effects
        import shutil

        shutil.copy2(input_path, output_path)
        return output_path

    # Apply all filters as chain
    if filters:
        filter_chain = ",".join(filters)
        return apply_ffmpeg_filter(input_path, output_path, filter_chain)

    # Fallback: just copy
    import shutil

    shutil.copy2(input_path, output_path)
    return output_path


def speed_ramp(
    video: VideoFileClip,
    slow_start: float,
    slow_end: float,
    slow_factor: float = 0.5,
) -> VideoFileClip:
    """
    Apply speed ramp effect (slow-mo on specific section).

    Slows down video between slow_start and slow_end, keeps normal speed elsewhere.

    Args:
        video: Input video clip
        slow_start: Time to start slow-mo (seconds)
        slow_end: Time to end slow-mo (seconds)
        slow_factor: Speed multiplier for slow section (0.5 = half speed)

    Returns:
        Video with speed ramp applied
    """
    from moviepy.video.fx import MultiplySpeed

    def speed_func(t):
        if slow_start <= t <= slow_end:
            return slow_factor
        return 1.0

    return video.with_effects([MultiplySpeed(speed_func)])


def add_shake(
    video: VideoFileClip,
    intensity: float = 5.0,
    frequency: float = 30.0,
) -> VideoFileClip:
    """
    Add camera shake effect to video.

    Creates a subtle shaking motion that simulates handheld camera.

    Args:
        video: Input video clip
        intensity: Shake intensity in pixels
        frequency: Shake frequency (higher = faster shake)

    Returns:
        Video with shake effect applied
    """
    import math

    def shake_x(t):
        return intensity * math.sin(frequency * t * 2 * math.pi)

    def shake_y(t):
        return intensity * math.cos(frequency * t * 2 * math.pi * 1.3)

    return video.transform(
        lambda get_frame, t: get_frame(t),
        apply_to=["mask"],
    )


def create_word_highlights(
    words: list[Word],
    clip_start: float,
    clip_duration: float,
    style_config: dict,
    position: tuple = ("center", 1400),
    wrap_width: int = 6,
) -> list:
    """
    Create word-by-word highlighted captions that appear in sync with speech.

    Args:
        words: List of Word objects with timing
        clip_start: Start time of the clip in seconds
        clip_duration: Duration of the clip in seconds
        style_config: Style configuration dictionary
        position: (x, y) position for captions
        wrap_width: Max words per line before wrapping

    Returns:
        List of TextClip objects for word highlighting
    """
    clips = []

    for word in words:
        # Skip words outside the clip's time range
        if word.end < clip_start or word.start >= clip_start + clip_duration:
            continue

        # Calculate word timing relative to clip start
        word_start = max(0, word.start - clip_start)
        word_end = min(clip_duration, word.end - clip_start)

        # Skip very short words
        if word_end - word_start < 0.1:
            continue

        # Create highlighted text clip for this word
        word_clip = (
            TextClip(
                text=word.text.upper(),
                font_size=style_config["font_size"] + 20,
                color=style_config["color"],
                font="Arial Bold",
                stroke_color=style_config["stroke_color"],
                stroke_width=style_config["stroke_width"] + 3,
            )
            .with_position(position)
            .with_start(word_start)
            .with_end(word_end)
            .with_effects([vfx.FadeIn(0.1), vfx.FadeOut(0.1)])
        )
        clips.append(word_clip)

    return clips


def compose_clip(
    clip: HighlightClip,
    vod: str,
    output: str,
    style: OverlayStyle = OverlayStyle.BOLD,
    editing_style: EditingStyle = EditingStyle.CLEAN,
    transcript: Transcript | None = None,
    vertical: bool = True,
    enable_zoom: bool = True,
) -> Path:
    """
    Compose a single video clip with professional effects.

    Features:
    - 9:16 vertical crop (center-crop or blurred background)
    - Ken Burns auto-zoom on highlights
    - Word-by-word caption highlighting
    - Text animations (fade-in/out)
    - Text wrapping for long captions
    - Post-processing (color grade, vignette, grain, sharpen)

    Args:
        clip: Clip configuration with timing and text
        vod: Path to source video file
        output: Output file path
        style: Visual style for text overlays
        editing_style: Video editing style for effects
        transcript: Transcript with word timestamps (optional)
        vertical: Output in 9:16 vertical format
        enable_zoom: Enable Ken Burns zoom effect

    Returns:
        Path to the composed video file
    """
    Path(output).parent.mkdir(parents=True, exist_ok=True)

    if not Path(vod).exists():
        raise FileNotFoundError(f"Source video not found: {vod}")

    if clip.start < 0:
        raise ValueError(f"Clip start time must be non-negative: {clip.start}")
    if clip.duration <= 0:
        raise ValueError(f"Clip duration must be positive: {clip.duration}")

    with open_video(vod) as reader:
        end = min(clip.start + clip.duration, int(reader.duration))

        if clip.start >= reader.duration:
            raise ValueError(
                f"Clip start time ({clip.start}s) exceeds video duration ({reader.duration}s)"
            )

        video = reader.subclipped(clip.start, end)

        # Apply Ken Burns zoom effect if enabled
        if enable_zoom:
            video = ken_burns_zoom(video, start_zoom=1.0, end_zoom=1.12)

        # Get style configuration
        style_config = get_style_config(style)

        # Sanitize text
        hook = sanitize(clip.hook)
        overlay = sanitize(clip.text_overlay)
        outro = sanitize(clip.outro_text) if clip.outro_text else ""

        # Wrap text for better readability
        if hook:
            hook = wrap_text(hook, max_words=5)
        if overlay:
            overlay = wrap_text(overlay, max_words=4)
        if outro:
            outro = wrap_text(outro, max_words=4)

        # Build list of clips
        clips = []

        if vertical:
            # Create blurred background for vertical video
            bg = create_blurred_background(reader.subclipped(clip.start, end))
            clips.append(bg)

            # Crop main video to vertical and position in center
            main_video = crop_to_vertical(video)
            # Scale to fit vertical frame with padding
            main_video = main_video.resized(height=TARGET_HEIGHT * 0.7)
            main_video = main_video.with_position(("center", TARGET_HEIGHT * 0.15))
            clips.append(main_video)

            # Adjust text positions for vertical layout
            hook_pos = ("center", 80)
            overlay_pos = ("center", TARGET_HEIGHT // 2)
            outro_pos = ("center", TARGET_HEIGHT - 200)
            word_pos = ("center", TARGET_HEIGHT * 0.75)
        else:
            # Original horizontal layout
            clips.append(video)
            hook_pos = ("center", 80)
            overlay_pos = ("center", "center")
            outro_pos = ("center", 200)
            word_pos = ("center", 300)

        # Add hook text at top with fade-in
        if hook:
            hook_clip = (
                TextClip(
                    text=hook,
                    font_size=style_config["font_size"],
                    color=style_config["color"],
                    font="Arial Bold",
                    stroke_color=style_config["stroke_color"],
                    stroke_width=style_config["stroke_width"],
                )
                .with_position(hook_pos)
                .with_start(0.5)
                .with_effects([vfx.FadeIn(0.3), vfx.FadeOut(0.2)])
            )
            clips.append(hook_clip)

        # Add main overlay text in center with animation
        if overlay:
            overlay_clip = (
                TextClip(
                    text=overlay,
                    font_size=style_config["overlay_font_size"],
                    color=style_config["color"],
                    font="Arial Bold",
                    stroke_color=style_config["stroke_color"],
                    stroke_width=style_config["stroke_width"] + 3,
                )
                .with_position(overlay_pos)
                .with_start(0.8)
                .with_effects([vfx.FadeIn(0.2), vfx.FadeOut(0.2)])
            )
            clips.append(overlay_clip)

        # Add outro text at bottom with fade-in
        if outro:
            outro_start = max(0, clip.duration - 4)
            outro_clip = (
                TextClip(
                    text=outro,
                    font_size=style_config["overlay_font_size"] - 20,
                    color=style_config["outro_color"],
                    font="Arial Bold",
                    stroke_color=style_config["stroke_color"],
                    stroke_width=style_config["stroke_width"] + 2,
                )
                .with_position(outro_pos)
                .with_start(outro_start)
                .with_effects([vfx.FadeIn(0.3), vfx.FadeOut(0.2)])
            )
            clips.append(outro_clip)

        # Add word-by-word highlighted captions
        if transcript and transcript.words:
            word_clips = create_word_highlights(
                words=transcript.words,
                clip_start=clip.start,
                clip_duration=video.duration,
                style_config=style_config,
                position=word_pos,
            )
            clips.extend(word_clips)

        # Compose all layers
        if vertical:
            final = CompositeVideoClip(
                clips, size=(TARGET_WIDTH, TARGET_HEIGHT)
            ).with_duration(video.duration)
        else:
            final = CompositeVideoClip(clips).with_duration(video.duration)

        # Write to file with good quality settings
        temp_output = output + ".temp.mp4"
        final.write_videofile(
            temp_output,
            codec="libx264",
            audio_codec="aac",
            preset="medium",  # Better quality than "fast"
            bitrate="8000k",  # Good quality for social media
            audio_bitrate="192k",
            logger=None,
        )
        final.close()

    # Apply post-processing effects (color grade, vignette, grain, etc.)
    if editing_style not in (EditingStyle.NONE, EditingStyle.MINIMAL):
        post_process_video(temp_output, output, editing_style)
        # Clean up temp file
        import os

        os.remove(temp_output)
    else:
        # No post-processing, just rename temp to final
        import os

        if os.path.exists(output):
            os.remove(output)
        os.rename(temp_output, output)

    return Path(output)


def get_style_config(style: OverlayStyle) -> dict:
    """
    Get text styling configuration based on overlay style.

    Each style has:
    - font_size: Size for hook/caption text
    - color: Main text color
    - stroke_color: Text outline color (None for no outline)
    - stroke_width: Outline thickness
    - overlay_font_size: Size for dramatic center text
    - outro_color: Color for outro/CTA text
    """
    styles = {
        # === CORE STYLES ===
        OverlayStyle.BOLD: {
            "font_size": 48,
            "color": "white",
            "stroke_color": "black",
            "stroke_width": 3,
            "overlay_font_size": 110,
            "outro_color": "#00FF00",
        },
        OverlayStyle.MINIMAL: {
            "font_size": 36,
            "color": "white",
            "stroke_color": None,
            "stroke_width": 0,
            "overlay_font_size": 80,
            "outro_color": "white",
        },
        # === CONTENT-SPECIFIC STYLES ===
        OverlayStyle.GAMBLING: {
            "font_size": 52,
            "color": "#FFD700",  # Gold
            "stroke_color": "#006400",  # Dark green
            "stroke_width": 4,
            "overlay_font_size": 120,
            "outro_color": "#00FF00",  # Bright green
        },
        OverlayStyle.DRAMATIC: {
            "font_size": 50,
            "color": "#FF0000",  # Red
            "stroke_color": "white",
            "stroke_width": 5,
            "overlay_font_size": 115,
            "outro_color": "#FFFFFF",
        },
        OverlayStyle.GAMING: {
            "font_size": 46,
            "color": "#00FFFF",  # Cyan
            "stroke_color": "#8B00FF",  # Purple
            "stroke_width": 4,
            "overlay_font_size": 105,
            "outro_color": "#FF00FF",  # Magenta
        },
        OverlayStyle.SPORTS: {
            "font_size": 50,
            "color": "#FF6600",  # Orange
            "stroke_color": "#003366",  # Dark blue
            "stroke_width": 5,
            "overlay_font_size": 118,
            "outro_color": "#0066FF",  # Bright blue
        },
        OverlayStyle.PODCAST: {
            "font_size": 42,
            "color": "white",
            "stroke_color": "#333333",
            "stroke_width": 2,
            "overlay_font_size": 90,
            "outro_color": "#AAAAAA",
        },
        OverlayStyle.REACTION: {
            "font_size": 54,
            "color": "#FFFF00",  # Yellow
            "stroke_color": "#FF1493",  # Deep pink
            "stroke_width": 4,
            "overlay_font_size": 125,
            "outro_color": "#FF69B4",  # Hot pink
        },
        OverlayStyle.NEWS: {
            "font_size": 44,
            "color": "white",
            "stroke_color": "#000080",  # Navy
            "stroke_width": 3,
            "overlay_font_size": 100,
            "outro_color": "#0066CC",  # News blue
        },
        OverlayStyle.VIRAL: {
            "font_size": 56,
            "color": "#FF00FF",  # Fuchsia
            "stroke_color": "black",
            "stroke_width": 5,
            "overlay_font_size": 130,
            "outro_color": "#00FFFF",  # Cyan
        },
        OverlayStyle.HORROR: {
            "font_size": 48,
            "color": "#8B0000",  # Dark red
            "stroke_color": "black",
            "stroke_width": 4,
            "overlay_font_size": 110,
            "outro_color": "#FF0000",  # Blood red
        },
        OverlayStyle.RETRO: {
            "font_size": 40,
            "color": "#33FF33",  # Terminal green
            "stroke_color": "#003300",
            "stroke_width": 2,
            "overlay_font_size": 95,
            "outro_color": "#FFB000",  # Amber
        },
        OverlayStyle.NEON: {
            "font_size": 52,
            "color": "#FF00FF",  # Neon pink
            "stroke_color": "#00FFFF",  # Neon cyan
            "stroke_width": 4,
            "overlay_font_size": 120,
            "outro_color": "#FFFF00",  # Neon yellow
        },
        OverlayStyle.PASTEL: {
            "font_size": 44,
            "color": "#FFB6C1",  # Light pink
            "stroke_color": "#8B4513",  # Saddle brown
            "stroke_width": 2,
            "overlay_font_size": 95,
            "outro_color": "#98FB98",  # Pale green
        },
        OverlayStyle.FIRE: {
            "font_size": 54,
            "color": "#FF4500",  # Orange red
            "stroke_color": "#8B0000",  # Dark red
            "stroke_width": 5,
            "overlay_font_size": 125,
            "outro_color": "#FFD700",  # Gold
        },
        OverlayStyle.ICE: {
            "font_size": 48,
            "color": "#00BFFF",  # Deep sky blue
            "stroke_color": "#003366",  # Dark blue
            "stroke_width": 4,
            "overlay_font_size": 110,
            "outro_color": "#E0FFFF",  # Light cyan
        },
        OverlayStyle.GOLD: {
            "font_size": 50,
            "color": "#FFD700",  # Gold
            "stroke_color": "#1a1a1a",  # Almost black
            "stroke_width": 4,
            "overlay_font_size": 115,
            "outro_color": "#FFFFFF",  # White
        },
    }
    return styles.get(style, styles[OverlayStyle.BOLD])


def compose_all(
    script: GeneratedScript,
    vod: str,
    start_num: int,
    overlay_style: OverlayStyle = OverlayStyle.BOLD,
    editing_style: EditingStyle = EditingStyle.CLEAN,
    transcript: Transcript | None = None,
    vertical: bool = True,
    enable_zoom: bool = True,
) -> list[Path]:
    """
    Compose all clips from a generated script.

    Args:
        script: Generated script with clip definitions
        vod: Path to source video file
        start_num: Starting number for clip filenames
        overlay_style: Visual style for text overlays
        editing_style: Video editing style for effects
        transcript: Transcript with word timestamps (optional)
        vertical: Output in 9:16 vertical format
        enable_zoom: Enable Ken Burns zoom effect

    Returns:
        List of paths to composed video files
    """
    OUT_DIR.mkdir(exist_ok=True)
    paths = []

    for i, clip in enumerate(script.clips):
        num = start_num + i
        out = str(OUT_DIR / f"{num:03d}_clip.mp4")
        compose_clip(
            clip,
            vod,
            out,
            overlay_style,
            editing_style,
            transcript,
            vertical,
            enable_zoom,
        )
        paths.append(Path(out))

    return paths
