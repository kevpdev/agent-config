# Sources par domaine — hiérarchie de fiabilité

> Table de référence de la Phase 1 du skill `fact-checker`. Le domaine **sélectionne** la
> stratégie de sources ; il ne crée pas d'agent. **À compléter / calibrer** — squelette.

## Tiers de fiabilité (colonne vertébrale, tous domaines)

Du plus fiable au moins fiable. Une source de tier bas ne rend pas une affirmation fausse, mais
plafonne le niveau de confiance.

| Tier | Nature | Niveau de confiance plafond |
|---|---|---|
| **T1** | Méta-analyses, revues systématiques, sources primaires officielles (texte de loi voté, données statistiques d'un institut public) | haut |
| **T2** | Étude primaire à comité de lecture, rapport d'institution reconnue, donnée officielle brute | moyen-haut |
| **T3** | Média de référence avec méthode vérifiable, fact-checkers établis | moyen |
| **T4** | Média orienté, presse d'opinion, expert isolé | bas |
| **T5** | Blog, réseau social, source anonyme, contenu non daté | à corroborer obligatoirement, jamais seul |

**Règle transverse** : consensus = ≥ 2 sources **indépendantes** de tier T2+ **et** une
contre-recherche menée. Sinon → confiance basse.

## Stratégie par domaine

> Pour chaque domaine : sources à viser en priorité, seuil de corroboration, pièges. **À affiner.**

### Santé / médecine
- **Viser** : Cochrane, PubMed (méta-analyses > RCT > observationnel), HAS/OMS.
- **Piège** : preprint non relu présenté comme établi ; corrélation vendue comme causalité ;
  étude unique généralisée.

### Politique / droit
- **Viser** : texte de loi ou règlement (source primaire), Journal officiel / EUR-Lex, comptes
  rendus institutionnels.
- **Piège** : confondre **proposition / rapport / recommandation** avec **texte voté** ;
  interprétation politique d'un texte présentée comme son contenu.

### Économie
- **Viser** : INSEE, Eurostat, OCDE, banques centrales, données brutes avant commentaire.
- **Piège** : chiffre sorti de son périmètre temporel ; nominal vs réel ; effet vs corrélation.

### Histoire
- **Viser** : travaux d'historiens à comité de lecture, sources primaires contextualisées.
- **Piège** : anachronisme ; source primaire isolée sans historiographie ; citation apocryphe.

### Sociologie / société
- **Viser** : études quantitatives avec méthodo publiée, enquêtes d'instituts reconnus.
- **Piège** : échantillon non représentatif ; sondage commandité ; généralisation abusive.

### Sport
- **Viser** : données officielles des fédérations/organisateurs, statistiques primaires.
- **Piège** : record/chiffre non daté ; source secondaire recopiée en boucle.

### Science / tech
- **Viser** : publications à comité de lecture, doc primaire, organismes de normalisation.
- **Piège** : vulgarisation qui déforme ; hype d'annonce vs résultat reproduit.

## À compléter

- [ ] Calibrer les seuils de corroboration par domaine avec l'utilisateur.
- [ ] Ajouter une liste de fact-checkers / instituts de référence par pays/langue.
- [ ] Décider du traitement des sources en langue étrangère.
