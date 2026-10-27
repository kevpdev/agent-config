// voice — hands OpenCode's final replies to hooks/speak.py, as the Claude Stop
// hook does. speak.py keeps the reply for `lis`, and plays it at once only in
// `auto` mode. The logic is in core.ts.
//
// Subagent sessions (`parentID` set) stay silent: only the session the human
// talks to is spoken.
import { Plugin } from "@opencode/plugin"
import { EVENT_TYPES, Replies, speak, type VoiceEvent } from "./core.ts"

export default Plugin.define({
  id: "voice",
  async setup(ctx) {
    const replies = new Replies()
    void (async () => {
      for await (const event of ctx.event.subscribe({ types: [...EVENT_TYPES] })) {
        const reply = replies.feed(event as VoiceEvent)
        if (!reply) continue
        const session = await ctx.session.get({ sessionID: event.data.sessionID }).catch(() => undefined)
        if (session?.parentID) continue
        speak(reply)
      }
    })().catch((err) => console.error(`voice: event stream stopped (${err})`))
  },
})
