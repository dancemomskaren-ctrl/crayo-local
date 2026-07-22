import { describe, test, expect } from "bun:test";
import { escapeDrawtext, getDuration, run } from "../src/ffmpeg";
import { existsSync, writeFileSync, unlinkSync } from "fs";
import { join } from "path";

describe("escapeDrawtext", () => {
  test("escapes backslashes", () => {
    expect(escapeDrawtext("hello\\world")).toBe("hello\\\\world");
  });

  test("escapes percent signs", () => {
    expect(escapeDrawtext("50%")).toBe("50%%");
  });

  test("escapes colons", () => {
    expect(escapeDrawtext("time: 10:30")).toBe("time\\: 10\\:30");
  });

  test("escapes brackets", () => {
    expect(escapeDrawtext("[test]")).toBe("\\[test\\]");
  });

  test("escapes semicolons and commas", () => {
    expect(escapeDrawtext("a;b,c")).toBe("a\\;b\\,c");
  });

  test("replaces newlines with spaces", () => {
    expect(escapeDrawtext("line1\nline2")).toBe("line1 line2");
  });

  test("handles complex mixed text", () => {
    const input = "50% off: [today] only! Price: $10\\$";
    const result = escapeDrawtext(input);
    expect(result).toContain("%%");
    expect(result).toContain("\\:");
    expect(result).toContain("\\[");
    expect(result).toContain("\\]");
    expect(result).toContain("\\\\");
  });
});

describe("getDuration", () => {
  test("returns duration of a valid audio file", async () => {
    // Use the TTS test file from earlier if it exists, otherwise skip
    const testFile = join(import.meta.dir, "../../../data/renders");
    const { readdirSync } = await import("fs");
    if (!existsSync(testFile)) return;

    const files = readdirSync(testFile).filter((f) => f.endsWith(".mp4"));
    if (files.length === 0) return;

    const dur = await getDuration(join(testFile, files[0]));
    expect(dur).toBeGreaterThan(0);
  });

  test("returns 0 for non-existent file", async () => {
    const dur = await getDuration("/nonexistent/file.mp4");
    expect(dur).toBe(0);
  });
});

describe("ffmpeg.run", () => {
  test("generates a test video", async () => {
    const outPath = join(import.meta.dir, "../../../data/renders/test-gen.mp4");
    await run([
      "-f",
      "lavfi",
      "-i",
      "color=c=black:s=320x240:d=1",
      "-f",
      "lavfi",
      "-i",
      "anullsrc=r=44100:cl=stereo",
      "-t",
      "1",
      "-c:v",
      "libx264",
      "-preset",
      "ultrafast",
      "-crf",
      "28",
      "-c:a",
      "aac",
      "-b:a",
      "64k",
      "-shortest",
      outPath,
    ]);
    expect(existsSync(outPath)).toBe(true);
    const dur = await getDuration(outPath);
    expect(dur).toBeGreaterThan(0.5);
    expect(dur).toBeLessThan(2);
    unlinkSync(outPath);
  });
});
