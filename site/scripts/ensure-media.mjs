#!/usr/bin/env node
// The 714 plates live inside the original Word document, which is committed as
// a split zip. They are not committed a second time, so the first build
// extracts them. Everything else the site needs is committed as JSON.

import { existsSync } from "node:fs";
import { readdir } from "node:fs/promises";
import { spawnSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const MEDIA = path.join(ROOT, "data/media");

const count = existsSync(MEDIA) ? (await readdir(MEDIA)).length : 0;
if (count > 700) process.exit(0);

console.log("Bildmaterial fehlt — entpacke das Originaldokument …");
for (const python of ["python3", "python", "py"]) {
  const run = spawnSync(python, [path.join(ROOT, "tools/extract_docx.py")], { stdio: "inherit" });
  if (run.status === 0) process.exit(0);
  if (run.error?.code !== "ENOENT") break;
}
console.error(
  "\nPython wurde nicht gefunden. Zum Entpacken der Bilder einmalig ausführen:\n" +
  "    python tools/extract_docx.py\n",
);
process.exit(1);
