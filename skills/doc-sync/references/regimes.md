# Régimes de doc — qui fait foi

Le mot « doc » recouvre des surfaces d'autorité opposée. Confondre les deux fait écraser une décision d'équipe par du code, ou l'inverse. Chaque document reçoit son régime avant d'être touché.

| Régime | Ce que c'est | Exemples | Qui fait foi | Ce que fait doc-sync |
| --- | --- | --- | --- | --- |
| **reflet** | décrit ce que le code fait | README, guide d'installation | le code | réécrit, selon les règles du type |
| **mémoire AIDD** | reflet relu par les agents à chaque session | `aidd_docs/memory/` hors décisions | le code, filtré par le critère d'inclusion | cadre, livre par `/10-learn`, fait contrôler |
| **décision** | prescrit ce qui a été décidé | ADR, contrat partagé, spec, mémoire `decisions` et `coding-assertions` | la décision, sur l'intention | signale l'écart, n'écrit jamais |

**Pourquoi la décision ne se réécrit pas.** Quand le code ajoute un champ que le contrat ne prévoit pas, rien ne dit si c'est une découverte ou une bavure. Réécrire le contrat graverait peut-être un bug dans la loi.

## Le cas qui se classe mal

`coding-assertions`. Que `./mvnw test` existe est un fait, donc du reflet. En faire une porte avant chaque commit est une politique, donc une décision. C'est la politique qui gouverne le fichier, il part en décision. La prose de détail qui ne change ni une commande de porte ni un prérequis bloquant reste du reflet.

## En coordinateur

L'autorité ne change pas, seuls les homes changent. Le code d'un enfant vit dans l'enfant. Sa mémoire vit chez lui (distribuée) ou dans `aidd_docs/memory/<enfant>/` au parent (centralisée). Le repo qui implémente fait foi : le backend sur les endpoints et le schéma, le front sur les routes et ce qu'il consomme. Deux enfants qui se contredisent se signalent, ils ne se départagent pas.
