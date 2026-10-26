// Batterie du plugin OpenCode harness-guards, lancée par `node` hors d'OpenCode.
//
// Pourquoi cette batterie existe : le banc OpenCode passe par un modèle, donc il
// est lent et dépend de ce que le modèle accepte de lancer. Ici, on prouve sans
// modèle les deux fonctions du plugin, `toEvent` et `verdict`, contre le vrai
// `hooks/check.py`.
//
// Le cas central est le `cd` : `permission.evaluate` ne reçoit que les commandes
// simples, sans `cd` ni dossier courant. Le plugin doit donc juger la commande
// retenue par `execute.before`, et le cas « sans appel retenu » montre ce qu'on
// perdrait sans elle.
//
// Sortie : 0 si tous les cas passent, 1 si un cas échoue.
import { execFileSync } from "node:child_process"
import { chmodSync, mkdtempSync, rmSync, writeFileSync } from "node:fs"
import { tmpdir } from "node:os"
import { join } from "node:path"
import { type Call, type Evaluation, toEvent, verdict } from "../plugins/harness-guards/core.ts"

let echecs = 0

function verifier(nom: string, attendu: "PASSE" | "REFUS" | "AVERTI", evaluation: Evaluation, call: Call | undefined,
  directory: string, check?: string) {
  const event = toEvent(evaluation, call, directory)
  const v = event ? verdict(event, check) : { allow: true as const }
  const obtenu = "deny" in v ? "REFUS" : v.warn ? "AVERTI" : "PASSE"
  if (obtenu === attendu) console.log(`  OK    ${nom.padEnd(58)} ${obtenu}`)
  else {
    console.log(`  ECHEC ${nom.padEnd(58)} attendu=${attendu} obtenu=${obtenu}`)
    echecs++
  }
}

function egal(nom: string, obtenu: unknown, attendu: unknown) {
  const ok = JSON.stringify(obtenu) === JSON.stringify(attendu)
  console.log(`  ${ok ? "OK   " : "ECHEC"} ${nom}`)
  if (!ok) {
    console.log(`        attendu=${JSON.stringify(attendu)} obtenu=${JSON.stringify(obtenu)}`)
    echecs++
  }
}

const shell = (resources: string[]): Evaluation => ({ sessionID: "test", action: "shell", resources })

// Un dépôt jetable dont le message de commit, dans un fichier, porte une ligne
// de co-signature. Écrit ici, jamais cité dans un message de commit.
const repo = mkdtempSync(join(tmpdir(), "harness-guards-"))
execFileSync("git", ["init", "-q", repo])
writeFileSync(join(repo, "msg.txt"), "fix: x\n\n" + "Co-Authored" + "-By: Claude <noreply@anthropic.com>\n")
const vide = mkdtempSync(join(tmpdir(), "harness-guards-vide-"))

console.log("\nshell")
verifier("commit -F signé, workdir de l'appel", "REFUS",
  shell(["git commit -F msg.txt"]), { command: "git commit -F msg.txt", workdir: repo }, vide)
verifier("commit -F signé derrière un cd, commande retenue", "REFUS",
  shell(["git commit -F msg.txt"]), { command: `cd ${repo} && git commit -F msg.txt` }, vide)
verifier("même cas sans appel retenu : le cd est perdu", "PASSE",
  shell(["git commit -F msg.txt"]), undefined, vide)
verifier("ls", "PASSE", shell(["ls"]), { command: "ls" }, vide)
verifier("cat .env : sort un secret", "REFUS", shell(["cat .env"]), { command: "cat .env" }, vide)
verifier("cp .env.example .env : pose le squelette", "PASSE",
  shell(["cp .env.example .env"]), { command: "cp .env.example .env" }, vide)
verifier("./mvnw direct", "REFUS", shell(["./mvnw test"]), { command: "./mvnw test" }, vide)

console.log("\nsans verdict du cœur")
const casse = join(vide, "check-casse.py")
writeFileSync(casse, "import sys\nsys.exit(1)\n")
chmodSync(casse, 0o755)
verifier("check.py rend 1 : passe, avec avertissement", "AVERTI",
  shell(["./mvnw test"]), { command: "./mvnw test" }, vide, casse)
verifier("check.py absent : passe, avec avertissement", "AVERTI",
  shell(["./mvnw test"]), { command: "./mvnw test" }, vide, join(vide, "absent.py"))

console.log("\nforme de l'événement")
egal("read : aucun événement, donc aucun processus",
  toEvent({ sessionID: "test", action: "read", resources: ["x"] }, undefined, vide), null)
egal("edit sans appel : resources résolues contre le dossier",
  toEvent({ sessionID: "test", action: "edit", resources: ["a/b.md", "/abs.md"] }, undefined, "/r")?.paths,
  ["/r/a/b.md", "/abs.md"])
egal("edit avec appel : le path de l'appel",
  toEvent({ sessionID: "test", action: "edit", resources: ["b.md"] }, { path: "/x/b.md" }, "/r")?.paths, ["/x/b.md"])
egal("shell : workdir relatif résolu contre le dossier",
  toEvent(shell(["ls"]), { command: "ls", workdir: "sub" }, "/r")?.cwd, "/r/sub")

rmSync(repo, { recursive: true, force: true })
rmSync(vide, { recursive: true, force: true })
console.log(echecs ? `\n✗ ${echecs} cas en échec.` : "\n✓ tous les cas passent.")
process.exit(echecs ? 1 : 0)
