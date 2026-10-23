// core.ts — OpenCode side of the guard core (hooks/), without the plugin API.
//
// index.ts wires OpenCode's hooks to the two functions below. They import
// nothing from @opencode/plugin, so tests/test-harness-guards.ts runs them under
// plain `node`, outside OpenCode.
//
//   toEvent  permission evaluation + the call it belongs to → normalized event
//            (contract in hooks/check.py), or null when no guard looks at it
//   verdict  normalized event → hooks/check.py → deny with its reason, or allow
//
// Fails OPEN when check.py gives no verdict (exit 1, crash, python3 missing):
// the call goes through and the reason goes to the log. Refusing there would
// deny every shell call of the session, as the Claude adapter already reasons.
import { spawnSync } from "node:child_process"
import { existsSync, realpathSync } from "node:fs"
import { dirname, isAbsolute, join, resolve } from "node:path"
import { fileURLToPath } from "node:url"

// The plugin is linked into the agent's config dir: resolve the link to find
// the repo, as the Claude shims do. This file sits four levels under it.
const HERE = dirname(realpathSync(fileURLToPath(import.meta.url)))
export const CHECK = join(HERE, "..", "..", "..", "..", "hooks", "check.py")

/** What execute.before saw of a call, kept until its permission is evaluated. */
export type Call = { command?: string; workdir?: string; path?: string }

/** The fields of OpenCode's PermissionEvaluation this file reads. */
export type Evaluation = {
  sessionID: string
  action: string
  resources: ReadonlyArray<string>
}

export type Event = {
  event: "pre_tool"
  action: "shell" | "edit"
  command: string
  paths: string[]
  cwd: string
  session: string
  skills_used: null
}

/** Normalized event for this evaluation, or null when no guard looks at it.
 *
 * `call` comes from execute.before and carries the raw command and its workdir.
 * Without it (an evaluation no execute.before announced), the resources are all
 * there is: one entry per simple command, `cd` removed, so a guard that resolves
 * a path against the directory may judge less than it would with the call.
 */
export function toEvent(evaluation: Evaluation, call: Call | undefined, directory: string): Event | null {
  const base = { event: "pre_tool" as const, session: evaluation.sessionID, skills_used: null }
  if (evaluation.action === "shell") {
    const command = call?.command ?? evaluation.resources.join(" && ")
    const cwd = call?.workdir ? resolve(directory, call.workdir) : directory
    return { ...base, action: "shell", command, paths: [], cwd }
  }
  if (evaluation.action === "edit") {
    const paths = call?.path
      ? [call.path]
      : evaluation.resources.map((r) => (isAbsolute(r) ? r : join(directory, r)))
    return { ...base, action: "edit", command: "", paths, cwd: directory }
  }
  return null
}

export type Verdict = { deny: string } | { allow: true; warn?: string }

/** Run hooks/check.py on the event. Only its exit 2 refuses. */
export function verdict(event: Event, check: string = CHECK): Verdict {
  // python3 exits 2 on a script it cannot open, the very code check.py refuses
  // with: without this test, a broken link would read as a refusal.
  if (!existsSync(check))
    return { allow: true, warn: `harness-guards : ${check} introuvable, appel laissé passer.` }
  const run = spawnSync("python3", [check], { input: JSON.stringify(event), timeout: 5000, encoding: "utf8" })
  const reason = (run.stderr || "").trim()
  if (run.status === 2) return { deny: reason || "refusé par le cœur des gardes, sans raison donnée" }
  if (run.status === 0) return { allow: true }
  const cause = run.error?.message || reason || `code ${run.status}`
  return { allow: true, warn: `harness-guards : pas de verdict de ${check} (${cause}), appel laissé passer.` }
}
