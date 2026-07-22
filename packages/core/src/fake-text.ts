import { run, escapeDrawtext } from "./ffmpeg";
import { join } from "path";
import { existsSync, mkdirSync, unlinkSync } from "fs";

export interface Message {
  sender: string;
  text: string;
  isMe?: boolean;
}

export interface FakeTextOpts {
  messages: Message[];
  bgVideo?: string;
  bgImage?: string;
  bg_color?: string;
  output: string;
  duration?: number;
  senderName?: string;
  fontSize?: number;
}

const DEFAULTS = {
  bg_color: "#000000",
  fontSize: 32,
  senderName: "Contact",
};

export async function generateFakeText(opts: FakeTextOpts): Promise<string> {
  const {
    messages,
    bgVideo,
    bgImage,
    bg_color = DEFAULTS.bg_color,
    output,
    duration,
    fontSize = DEFAULTS.fontSize,
    senderName = DEFAULTS.senderName,
  } = opts;

  const tmpDir = join(output, "..");
  if (!existsSync(tmpDir)) mkdirSync(tmpDir, { recursive: true });

  const validMsgs = messages.filter((m) => m.text.trim());
  if (validMsgs.length === 0) {
    // Empty conversation: just make a blank video
    const d = duration ?? 5;
    await run([
      "-f",
      "lavfi",
      "-i",
      `color=c=black:s=1080x1920:d=${d}`,
      "-f",
      "lavfi",
      "-i",
      "anullsrc=r=44100:cl=stereo",
      "-t",
      String(d),
      "-c:v",
      "libx264",
      "-preset",
      "fast",
      "-crf",
      "23",
      "-c:a",
      "aac",
      "-shortest",
      output,
    ]);
    return output;
  }

  const timeline = buildTimeline(validMsgs);

  const bgPath = join(tmpDir, `bg-${Date.now()}.mp4`);
  const lastEntry = timeline[timeline.length - 1];
  const totalDuration =
    duration ?? (lastEntry ? lastEntry.endMs / 1000 + 3 : 30);

  const bgAudioPath = join(tmpDir, `bg-audio-${Date.now()}.mp4`);

  try {
    // Create background video
    if (bgVideo && existsSync(bgVideo)) {
      await run([
        "-i",
        bgVideo,
        "-t",
        String(totalDuration),
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-an",
        bgPath,
      ]);
    } else if (bgImage && existsSync(bgImage)) {
      await run([
        "-loop",
        "1",
        "-i",
        bgImage,
        "-t",
        String(totalDuration),
        "-vf",
        "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2:black",
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        bgPath,
      ]);
    } else {
      await run([
        "-f",
        "lavfi",
        "-i",
        `color=c=${bg_color}:s=1080x1920:d=${totalDuration}`,
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-pix_fmt",
        "yuv420p",
        bgPath,
      ]);
    }

    // Add silent audio track
    await run([
      "-i",
      bgPath,
      "-f",
      "lavfi",
      "-i",
      "anullsrc=r=44100:cl=stereo",
      "-c:v",
      "copy",
      "-c:a",
      "aac",
      "-b:a",
      "128k",
      "-shortest",
      bgAudioPath,
    ]);

    // Build and apply drawtext filters
    const filters = buildMessageFilters(
      validMsgs,
      timeline,
      fontSize,
      senderName,
    );
    await run([
      "-i",
      bgAudioPath,
      "-vf",
      filters.join(","),
      "-c:v",
      "libx264",
      "-preset",
      "fast",
      "-crf",
      "23",
      "-c:a",
      "copy",
      output,
    ]);
  } finally {
    try {
      unlinkSync(bgPath);
    } catch {}
    try {
      unlinkSync(bgAudioPath);
    } catch {}
  }

  return output;
}

interface TimelineEntry {
  index: number;
  startMs: number;
  endMs: number;
  message: Message;
}

function buildTimeline(messages: Message[]): TimelineEntry[] {
  const timeline: TimelineEntry[] = [];
  let ms = 500;
  const gap = 800;
  const typingDelay = 600;

  for (let i = 0; i < messages.length; i++) {
    const msg = messages[i];
    const textLen = msg.text.length;
    const displayMs = Math.max(Math.min(textLen * 40, 4000), 1500);

    timeline.push({
      index: i,
      startMs: ms + typingDelay,
      endMs: ms + typingDelay + displayMs,
      message: msg,
    });
    ms += typingDelay + displayMs + gap;
  }

  return timeline;
}

function buildMessageFilters(
  messages: Message[],
  timeline: TimelineEntry[],
  fontSize: number,
  senderName: string,
): string[] {
  const filters: string[] = [];

  // Header bar
  filters.push(`drawbox=x=0:y=0:w=1080:h=120:color=black@0.8:t=fill`);
  filters.push(
    `drawtext=text='${escapeDrawtext(senderName)}':fontsize=36:fontcolor=white:x=(w-text_w)/2:y=42:font=Arial`,
  );
  filters.push(
    `drawtext=text='<':fontsize=40:fontcolor=white:x=40:y=38:font=Arial`,
  );

  // Calculate each bubble's final Y position (stack from bottom)
  const bubblePositions = calcBubblePositions(timeline, fontSize);

  for (let i = 0; i < timeline.length; i++) {
    const t = timeline[i];
    const msg = t.message;
    const isMe = msg.isMe ?? i % 2 === 1;
    const pos = bubblePositions[i];
    const enable = `between(t,${(t.startMs / 1000).toFixed(2)},999)`;

    const escaped = escapeDrawtext(msg.text);
    const textLines = wrapText(msg.text, 30);
    const maxLineLen = Math.max(...textLines.map((l) => l.length), 1);
    const bubbleW = Math.min(700, maxLineLen * fontSize * 0.6 + 40);
    const bubbleH = estimateBubbleHeight(msg.text, fontSize);
    const x = isMe ? 1080 - bubbleW - 30 : 30;
    const y = pos.y;

    // Bubble background with enable
    const bgColor = isMe ? "0x007AFF@0.95" : "0x3A3A3C@0.95";
    filters.push(
      `drawbox=x=${x}:y=${y}:w=${bubbleW}:h=${bubbleH}:color=${bgColor}:t=fill:enable='${enable}'`,
    );

    // Multi-line text: one drawtext per line
    for (let li = 0; li < textLines.length; li++) {
      const line = textLines[li];
      if (!line) continue;
      const lineEscaped = escapeDrawtext(line);
      const lineY = y + 12 + li * (fontSize + 6);
      filters.push(
        `drawtext=text='${lineEscaped}':fontsize=${fontSize}:fontcolor=white:x=${x + 20}:y=${lineY}:font=Arial:enable='${enable}'`,
      );
    }
  }

  return filters;
}

function calcBubblePositions(timeline: TimelineEntry[], fontSize: number) {
  const positions: { y: number }[] = [];
  const gap = 20;
  const bottomPad = 160;

  // Calculate total height first
  let totalH = 0;
  for (const t of timeline) {
    totalH += estimateBubbleHeight(t.message.text, fontSize) + gap;
  }

  // Stack from bottom up
  let currentY = 1920 - bottomPad;
  for (let i = 0; i < timeline.length; i++) {
    const h = estimateBubbleHeight(timeline[i].message.text, fontSize);
    currentY -= h;
    positions.push({ y: Math.max(currentY, 140) });
    currentY -= gap;
  }

  return positions;
}

function estimateBubbleHeight(text: string, fontSize: number): number {
  const lines = wrapText(text, 30);
  return Math.max(lines.length * (fontSize + 6) + 24, fontSize + 30);
}

function wrapText(text: string, maxChars: number): string[] {
  const words = text.split(/\s+/);
  const lines: string[] = [];
  let line = "";
  for (const word of words) {
    if (line.length + word.length + 1 > maxChars && line) {
      lines.push(line);
      line = word;
    } else {
      line += (line ? " " : "") + word;
    }
  }
  if (line) lines.push(line);
  return lines.length ? lines : [""];
}
