<title>Flux du Research Kit</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<style>
  /* Concept : un schéma d'ingénieur, vertical, lu de haut en bas. Trace à gauche, fichiers à droite. */
  :root {
    --bg: #F3F6F8;
    --surface: #FFFFFF;
    --fg: #14202A;
    --muted: #566672;
    --line: #B6C3CC;
    --accent: #0A6C8C;
    --stop: #B3471D;
    --sans: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
    --mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
  }
  @media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
      --bg: #0E151B; --surface: #151F27; --fg: #E3EBF0; --muted: #93A4B0;
      --line: #34454F; --accent: #4FB6D6; --stop: #E58A5E; color-scheme: dark;
    }
  }
  :root[data-theme="dark"] {
    --bg: #0E151B; --surface: #151F27; --fg: #E3EBF0; --muted: #93A4B0;
    --line: #34454F; --accent: #4FB6D6; --stop: #E58A5E; color-scheme: dark;
  }
  body {
    background: var(--bg);
    color: var(--fg);
    font-family: var(--sans);
    font-size: 15px;
    line-height: 1.55;
    padding-inline: 16px;
    padding-block: 32px 48px;
  }
  main { max-width: 920px; margin-inline: auto; display: flex; flex-direction: column; gap: 40px; }
  h1 { font-size: clamp(26px, 5vw, 36px); line-height: 1.15; font-weight: 600; margin: 0; text-wrap: balance; letter-spacing: -0.01em; }
  h2 { font-size: 18px; font-weight: 600; margin: 0 0 6px; }
  p { margin: 0; }
  header p { color: var(--muted); max-width: 65ch; margin-top: 12px; }
  code { font-family: var(--mono); font-size: 0.9em; }
  .note { color: var(--muted); font-size: 13px; max-width: 65ch; }

  figure { margin: 0; display: flex; flex-direction: column; gap: 12px; }
  .scroll { overflow-x: auto; border: 1px solid var(--line); border-radius: 6px; background: var(--bg); padding: 12px; }
  svg { display: block; width: 100%; min-width: 720px; height: auto; font-family: var(--sans); }
  figcaption { color: var(--muted); font-size: 13px; max-width: 70ch; }

  .box { fill: var(--surface); stroke: var(--line); stroke-width: 1.2; }
  .box.key { stroke: var(--accent); stroke-width: 2; }
  .box.stop { stroke: var(--stop); stroke-width: 1.6; }
  .t { fill: var(--fg); }
  .s { fill: var(--muted); }
  .mono { font-family: var(--mono); }
  .flow { stroke: var(--fg); stroke-width: 1.6; fill: none; }
  .side { stroke: var(--muted); stroke-width: 1.2; stroke-dasharray: 4 3; fill: none; }
  .trace { stroke: var(--accent); stroke-width: 2.5; fill: none; }
  .trace-t { stroke: var(--accent); stroke-width: 1.2; stroke-dasharray: 3 3; fill: none; }
  .mk-flow { fill: var(--fg); }
  .mk-side { fill: var(--muted); }
  .mk-trace { fill: var(--accent); }

  .tbl { overflow-x: auto; border: 1px solid var(--line); border-radius: 6px; background: var(--surface); }
  table { border-collapse: collapse; width: 100%; min-width: 520px; font-size: 14px; }
  th, td { text-align: left; padding: 9px 12px; border-bottom: 1px solid var(--line); vertical-align: top; }
  th { font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); font-weight: 500; background: var(--bg); }
  tr:last-child td { border-bottom: 0; }
  td.no { color: var(--muted); }
  td.num, th.num { font-variant-numeric: tabular-nums; }
  td.k { font-weight: 500; }
  section { display: flex; flex-direction: column; gap: 10px; }
</style>

<main>
  <header>
    <h1>Flux du Research Kit</h1>
    <p>Ce que fait un agent qui suit le kit, de la demande à la livraison. Le schéma se lit de haut en bas. À gauche, la trace s'écrit étape par étape. À droite, les fichiers lus ou écrits à chaque étape.</p>
  </header>

  <figure>
    <div class="scroll">
%%SVG%%
    </div>
    <figcaption>Chaque demande traverse le triage, puis les étapes 1 à 8 selon la profondeur retenue. La trace s'écrit pendant l'exécution et le niveau de garantie atteint est annoncé avec la réponse.</figcaption>
  </figure>

  <section>
    <h2>Profondeur : quelles étapes tournent</h2>
    <div class="tbl">
      <table>
        <thead><tr><th>Étape</th><th>L0</th><th>L1</th><th>L2</th><th>L3</th></tr></thead>
        <tbody>
          <tr><td class="k">1 Cadrage</td><td class="no">non</td><td>léger</td><td>oui</td><td>oui</td></tr>
          <tr><td class="k">2 Plan de recherche</td><td class="no">non</td><td class="no">non</td><td>oui</td><td>oui</td></tr>
          <tr><td class="k">3 Collecte</td><td class="no">non</td><td>1 à 3 recherches</td><td>oui</td><td>oui, en parallèle si possible</td></tr>
          <tr><td class="k">4 Évaluation des sources</td><td class="no">non</td><td>minimale</td><td>oui</td><td>oui</td></tr>
          <tr><td class="k">5 Registre d'affirmations</td><td class="no">non</td><td class="no">non</td><td>oui</td><td>oui</td></tr>
          <tr><td class="k">6 Synthèse</td><td>oui</td><td>oui</td><td>oui</td><td>oui</td></tr>
          <tr><td class="k">7 Vérification</td><td class="no">non</td><td>6 contrôles</td><td>échantillon</td><td>complète</td></tr>
          <tr><td class="k">8 Livraison</td><td>oui</td><td>oui</td><td>oui</td><td>oui</td></tr>
          <tr><td class="k">Recherches au plus</td><td class="no">0</td><td class="num">3</td><td class="num">8</td><td class="num">20</td></tr>
        </tbody>
      </table>
    </div>
    <p class="note">L0 est interdit pour un sujet sensible (médical, juridique, financier, sécurité des personnes) ou en temps réel. Dans le doute, on commence en L1 et on monte seulement si une étape échoue.</p>
  </section>

  <section>
    <h2>Ce qui varie selon l'environnement</h2>
    <div class="tbl">
      <table>
        <thead><tr><th>Moyen</th><th>Principal</th><th>Repli</th><th>Annoncé en sortie</th></tr></thead>
        <tbody>
          <tr><td class="k">Contrôles</td><td>lancer <code>check_claims.py</code></td><td>liste parcourue à la main, un oui ou non par critère</td><td>« contrôles : script » ou « manuels »</td></tr>
          <tr><td class="k">Vérification</td><td>contexte séparé du raisonnement initial</td><td>étape distincte, sources rouvertes</td><td>« indépendante » ou « non indépendante »</td></tr>
          <tr><td class="k">Source et extrait</td><td><code>check_claims.py --en-ligne</code> retrouve l'extrait dans la page</td><td>rouvrir la page et chercher l'extrait</td><td>« sources : script » ou « à la main »</td></tr>
          <tr><td class="k">Collecte large</td><td>en parallèle</td><td>en séquence, mêmes budgets</td><td>rien</td></tr>
          <tr><td class="k">Trace</td><td>fichier <code>trace.jsonl</code> dans le dossier de travail</td><td>bloc <code>jsonl</code> dans la section « Trace » de la réponse</td><td>le support utilisé</td></tr>
        </tbody>
      </table>
    </div>
    <p class="note">Seul le moyen change, jamais le résultat exigé. Un moyen indisponible se déclare, il ne se tait pas.</p>
  </section>

  <p class="note">Sources : <code>pipeline.md</code> §3 et §5, <code>guardrails.md</code> §5 à §7. Les budgets et les seuils sont des valeurs de départ, non calibrées.</p>
</main>
