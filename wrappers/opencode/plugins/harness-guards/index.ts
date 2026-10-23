// harness-guards — runs the guard core (hooks/check.py) before OpenCode's tool
// calls, as the Claude shims do before Claude Code's. The logic is in core.ts.
//
// WHY TWO HOOKS. `permission.evaluate` is the documented place to refuse, and a
// deny there reaches the model as a failed tool call. But for the shell it only
// gets `resources`, one entry per simple command split by OpenCode's parser
// (packages/core/src/tool/plugin/shell.ts, l. 140): `cd` commands are taken out
// (shell/parse.ts, l. 192), and the event carries no working directory. The
// commit guard resolves `-F msg.txt` against that directory.
// `tool.execute.before` sees the raw command and its `workdir`. It fires before
// the tool runs, hence before the shell asks for permission (core/src/tool.ts,
// l. 272), with the same call id the shell passes as `source.id` (shell.ts,
// l. 118-122). So it records the call, and evaluate judges it.
import { Plugin } from "@opencode/plugin"
import { type Call, toEvent, verdict } from "./core.ts"

export default Plugin.define({
  id: "harness-guards",
  async setup(ctx) {
    const calls = new Map<string, Call>()

    await ctx.tool.hook("execute.before", (event) => {
      const input = (event.input ?? {}) as Record<string, unknown>
      const text = (key: string) => (typeof input[key] === "string" ? (input[key] as string) : undefined)
      calls.set(event.id, { command: text("command"), workdir: text("workdir"), path: text("path") })
    })

    await ctx.tool.hook("execute.after", (event) => {
      calls.delete(event.id)
    })

    await ctx.permission.hook("evaluate", (event) => {
      const call = event.source?.type === "tool" ? calls.get(event.source.id) : undefined
      const normalized = toEvent(event, call, ctx.location.directory)
      if (!normalized) return
      const result = verdict(normalized)
      if ("deny" in result) {
        event.effect = "deny"
        event.message = result.deny
      } else if (result.warn) console.error(result.warn)
    })
  },
})
