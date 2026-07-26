#!/usr/bin/env node
// Step 3: prepare the 656 plates of the chronicle for the web.
//
// The originals are the raw media stream of the Word document: 113 MB of
// mixed JPEG/PNG/GIF, some of them 2 MB scans.  For every image that the
// content actually references we write a display version and a thumbnail.

import { mkdir, readFile, writeFile, readdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const SRC = path.join(ROOT, "assets/quelle/final_markdown/images");
const OUT = path.join(ROOT, "site/public/bilder");
const FULL = path.join(OUT, "gross");
const THUMB = path.join(OUT, "klein");

const FULL_WIDTH = 1400;
const THUMB_WIDTH = 520;
const CONCURRENCY = 8;

async function main() {
  const content = JSON.parse(await readFile(path.join(ROOT, "data/content.json"), "utf8"));
  const wanted = new Set();
  const walk = (blocks) => {
    for (const b of blocks ?? []) if (b.type === "image") wanted.add(b.file);
  };
  for (const part of content.parts) for (const s of part.sections) walk(s.blocks);
  for (const y of content.years) for (const g of y.groups) walk(g.blocks);
  walk(content.front);

  await mkdir(FULL, { recursive: true });
  await mkdir(THUMB, { recursive: true });

  const available = new Set(await readdir(SRC));
  const files = [...wanted].filter((f) => available.has(f)).sort();
  const missing = [...wanted].filter((f) => !available.has(f));

  const manifest = {};
  let done = 0;
  const queue = files.slice();
  const workers = Array.from({ length: CONCURRENCY }, async () => {
    while (queue.length) {
      const file = queue.shift();
      const name = path.parse(file).name;
      const src = path.join(SRC, file);
      try {
        const image = sharp(src, { animated: false });
        const meta = await image.metadata();
        const fullPath = path.join(FULL, `${name}.webp`);
        const thumbPath = path.join(THUMB, `${name}.webp`);
        if (!existsSync(fullPath)) {
          await sharp(src)
            .rotate()
            .resize({ width: FULL_WIDTH, withoutEnlargement: true })
            .webp({ quality: 80 })
            .toFile(fullPath);
        }
        if (!existsSync(thumbPath)) {
          await sharp(src)
            .rotate()
            .resize({ width: THUMB_WIDTH, withoutEnlargement: true })
            .webp({ quality: 72 })
            .toFile(thumbPath);
        }
        const ratio = meta.width && meta.height ? meta.height / meta.width : 0.75;
        const width = Math.min(meta.width ?? FULL_WIDTH, FULL_WIDTH);
        manifest[file] = { name, width, height: Math.round(width * ratio) };
      } catch (err) {
        console.warn(`  skipped ${file}: ${err.message}`);
      }
      if (++done % 100 === 0) console.log(`  ${done}/${files.length}`);
    }
  });
  await Promise.all(workers);

  await writeFile(
    path.join(ROOT, "data/images.json"),
    JSON.stringify(manifest, null, 0),
    "utf8",
  );
  console.log(`optimised ${Object.keys(manifest).length} images` +
    (missing.length ? `, ${missing.length} referenced but absent` : ""));
}

main();
