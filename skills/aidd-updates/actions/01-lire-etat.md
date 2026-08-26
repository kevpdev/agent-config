# 01 - Lire l'état

Établit s'il y a un retard, et si un plan existe déjà, avant de dépenser quoi que ce soit à le
reconstruire.

## Output

Un verdict en une ligne, et la branche prise : `à jour`, `plan valide` (le plan est alors affiché tel
quel), ou `à planifier`.

## Process

1. **Interroger.** Lancer `--etat` du détecteur (`../references/detecteur.md`). Ne pas ouvrir le
   fichier d'état au préalable, le JSON porte déjà les champs calculés.
2. **Remonter la panne d'abord.** Si `derniere_erreur` n'est pas nul, l'afficher avant tout le reste,
   et dire que l'état peut être partiel.
   - Pourquoi en premier : un plan bâti sur des versions non rafraîchies serait faux sans le dire.
3. **Rafraîchir si l'état est vieux.** Si `verifie_le` est absent ou date de plus de 24 h, lancer
   `--refresh`, puis relancer `--etat`. Une seule fois, jamais en boucle.
4. **Brancher.**
   - `retards` vide → dire « à jour », s'arrêter. Ne pas dérouler 02.
   - `plan_a_refaire: false` et `corps_present: true` → lire le corps du fichier désigné par
     `fichier`, l'afficher tel quel, puis proposer l'action 03. **Ne rien replanifier.**
   - sinon → annoncer d'abord le coût, combien de plugins et combien de versions vont être lus, puis
     passer à l'action 02.
   - Pourquoi annoncer avant : lire 16 changelogs prend du temps et du contexte, et l'humain doit
     pouvoir dire « pas maintenant » avant la dépense, pas après.

## Test

| Cas | Preuve |
| --- | --- |
| `--etat` sur une machine à jour | `retards` est vide, et l'action s'arrête sans rien écrire |
| un appel juste après `--marquer-planifie` | l'action affiche le plan existant et ne relit aucun changelog |
| un `derniere_erreur` non nul dans l'état | il apparaît en tête de la sortie, avant le verdict |
| `bash wrappers/claude/scripts/tests/test-aidd-updates.sh` | la batterie du détecteur couvre les branches côté données et passe au vert |
