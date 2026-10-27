// core.ts — OpenCode side of the voice readout (hooks/speak.py), without the plugin API.
//
// index.ts feeds it OpenCode's session events. It imports nothing from
// @opencode/plugin, so tests/test-voice.ts runs it under plain `node`.
//
//   Replies  keeps the text of each session's current assistant message and
//            hands it over when the turn ends
//   speak    sends a reply to hooks/speak.py, detached, without waiting
//
// OpenCode v2 has no `session.idle`: a turn ends with `session.execution.*`, and
// the text comes as `session.text.ended` parts (packages/schema/src/session-event.ts).
import { spawn } from "node:child_process"
import { realpathSync } from "node:fs"
import { dirname, join } from "node:path"
import { fileURLToPath } from "node:url"

// The plugin is linked into the agent's config dir: resolve the link to find
// the repo, as harness-guards does. This file sits four levels under it.
const HERE = dirname(realpathSync(fileURLToPath(import.meta.url)))
export const SPEAK = join(HERE, "..", "..", "..", "..", "hooks", "speak.py")

/** The fields of the events this file reads. */
export type VoiceEvent =
  | { type: "session.text.ended"; data: { sessionID: string; assistantMessageID: string; ordinal: number; text: string } }
  | { type: "session.execution.succeeded" | "session.execution.failed" | "session.execution.interrupted"; data: { sessionID: string } }

export const EVENT_TYPES = [
  "session.text.ended",
  "session.execution.succeeded",
  "session.execution.failed",
  "session.execution.interrupted",
] as const

/**
 * Text parts per session, for its latest assistant message only: the narration
 * of a message followed by a tool call is not spoken. Returns the reply to speak
 * when a turn succeeds, else undefined.
 */
export class Replies {
  private readonly buffers = new Map<string, { messageID: string; parts: Map<number, string> }>()

  feed(event: VoiceEvent): string | undefined {
    const { sessionID } = event.data
    if (event.type === "session.text.ended") {
      const { assistantMessageID, ordinal, text } = event.data
      let buffer = this.buffers.get(sessionID)
      if (!buffer || buffer.messageID !== assistantMessageID) {
        buffer = { messageID: assistantMessageID, parts: new Map() }
        this.buffers.set(sessionID, buffer)
      }
      buffer.parts.set(ordinal, text)
      return undefined
    }
    const buffer = this.buffers.get(sessionID)
    this.buffers.delete(sessionID)
    if (event.type !== "session.execution.succeeded" || !buffer) return undefined
    const reply = [...buffer.parts.entries()].sort(([a], [b]) => a - b).map(([, text]) => text).join("\n\n")
    return reply.trim() ? reply : undefined
  }
}

/** Hands a reply to speak.py and returns at once; speak.py detaches the playback. */
export function speak(reply: string, script = SPEAK) {
  const child = spawn("python3", [script], { stdio: ["pipe", "ignore", "ignore"], detached: true })
  child.on("error", (err) => console.error(`voice: speak.py not started (${err.message})`))
  child.stdin.on("error", () => {})
  child.stdin.end(reply)
  child.unref()
}
