// Batterie du plugin OpenCode voice, lancée par `node` hors d'OpenCode.
//
// Pourquoi cette batterie existe : OpenCode v2 n'a plus d'événement « session
// inactive ». Le plugin recompose la réponse finale à partir des morceaux
// `session.text.ended`, et c'est ce montage qui peut lire la mauvaise chose : la
// narration d'avant un appel d'outil, ou une réponse interrompue.
//
// Sortie : 0 si tous les cas passent, 1 si un cas échoue.
import { Replies, type VoiceEvent } from "../plugins/voice/core.ts"

let echecs = 0

function egal(nom: string, obtenu: unknown, attendu: unknown) {
  const ok = JSON.stringify(obtenu) === JSON.stringify(attendu)
  console.log(`  ${ok ? "OK   " : "ECHEC"} ${nom}`)
  if (!ok) {
    console.log(`        attendu=${JSON.stringify(attendu)} obtenu=${JSON.stringify(obtenu)}`)
    echecs++
  }
}

const text = (sessionID: string, assistantMessageID: string, ordinal: number, t: string): VoiceEvent => ({
  type: "session.text.ended",
  data: { sessionID, assistantMessageID, ordinal, text: t },
})
const end = (sessionID: string, type: "succeeded" | "failed" | "interrupted" = "succeeded"): VoiceEvent => ({
  type: `session.execution.${type}`,
  data: { sessionID },
})

function rejouer(events: VoiceEvent[]) {
  const replies = new Replies()
  return events.map((e) => replies.feed(e)).filter((r) => r !== undefined)
}

egal("réponse simple", rejouer([text("s", "m1", 0, "Bonjour."), end("s")]), ["Bonjour."])
egal("narration d'un message précédent ignorée",
  rejouer([text("s", "m1", 0, "Je regarde."), text("s", "m2", 0, "Voici la réponse."), end("s")]),
  ["Voici la réponse."])
egal("morceaux remis dans l'ordre", rejouer([text("s", "m1", 1, "B"), text("s", "m1", 0, "A"), end("s")]), ["A\n\nB"])
egal("tour échoué : silence", rejouer([text("s", "m1", 0, "x"), end("s", "failed")]), [])
egal("tour interrompu : silence", rejouer([text("s", "m1", 0, "x"), end("s", "interrupted")]), [])
egal("tour suivant repart à vide", rejouer([text("s", "m1", 0, "x"), end("s", "failed"), end("s")]), [])
egal("sessions séparées",
  rejouer([text("a", "m1", 0, "pour a"), text("b", "m2", 0, "pour b"), end("b"), end("a")]),
  ["pour b", "pour a"])
egal("texte vide : silence", rejouer([text("s", "m1", 0, "  "), end("s")]), [])

console.log(`${echecs} échec(s)`)
process.exit(echecs ? 1 : 0)
