# _shared — ce que plusieurs skills partagent

Ce dossier n'est pas un skill : il n'a pas de `SKILL.md`. `tools/install.py` le lie dans `skills/` comme les autres dossiers, mais aucun agent ne le charge.

- **Ce qui entre ici** : un script ou un fait utilisé par au moins deux skills. Un script s'exécute (`scripts/`), un fait se lit (`references/`).
- **Comment le désigner** : `$SKILLS_ROOT/_shared/scripts/<script>.sh` pour un script, `../_shared/references/<fichier>.md` pour une référence. Jamais par le chemin d'un agent précis.
- **Ce qui casse si on le déplace** : tous les skills qui le citent, et `scripts/check-vault-bridge.sh`, qui dérive la racine des skills de son propre emplacement (`../..`).
