# strinz.de

Die Chronik von Strinz-Margarethä als statische Website.

## Starten

```bash
python3 tools/pipeline.py   # Inhalte aus dem Word-Dokument erzeugen
cd site
npm install
npm run dev                 # Entwicklung
npm test                    # Build + Tests
```

Benötigt Node.js 24 und Python 3. Deployment per `Dockerfile` (nginx).

## Lizenz

Code: [MIT](LICENSE). Der Inhalt der Chronik (Texte und Bilder) ist davon ausgenommen.
