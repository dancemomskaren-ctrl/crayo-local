import { describe, test, expect } from "bun:test";
import { generateFakeText } from "../src/fake-text";
import { existsSync, unlinkSync } from "fs";
import { join } from "path";

describe("generateFakeText", () => {
  test("generates a fake text video", async () => {
    const outPath = join(
      import.meta.dir,
      "../../../data/renders/test-fake-text.mp4",
    );
    await generateFakeText({
      messages: [
        { sender: "Them", text: "Hey!", isMe: false },
        { sender: "Me", text: "What's up?", isMe: true },
        { sender: "Them", text: "Not much, you?", isMe: false },
      ],
      output: outPath,
      senderName: "Test Contact",
      fontSize: 28,
    });

    expect(existsSync(outPath)).toBe(true);
    const { statSync } = await import("fs");
    const stat = statSync(outPath);
    expect(stat.size).toBeGreaterThan(1000);
    unlinkSync(outPath);
  }, 30000);

  test("generates with custom sender name", async () => {
    const outPath = join(
      import.meta.dir,
      "../../../data/renders/test-fake-text-2.mp4",
    );
    await generateFakeText({
      messages: [{ sender: "Me", text: "Hello!", isMe: true }],
      output: outPath,
      senderName: "Mom",
    });
    expect(existsSync(outPath)).toBe(true);
    unlinkSync(outPath);
  }, 30000);
});
