// Checks on the prepared chronicle. These guard the pipeline, not the design:
// if a future change to tools/*.py loses text, scrambles the chronology or
// re-introduces the artefacts of the old export, these fail.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync, readdirSync } from "node:fs";
import { execFileSync } from "node:child_process";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const read = (p) => JSON.parse(readFileSync(path.join(ROOT, p), "utf8"));

const content = read("data/content.json");
const images = read("data/images.json");
const chapterFiles = readdirSync(path.join(ROOT, "content")).filter((f) => f.endsWith(".md"));

const allBlocks = [
  ...content.chapters.flatMap((c) => c.sections.flatMap((s) => s.blocks)),
  ...content.epochs.flatMap((e) => e.years.flatMap((y) => y.groups.flatMap((g) => g.blocks))),
];

test("the wording is identical to the Word document", () => {
  // The authoritative check: tools/verify_markdown.py compares every word.
  const out = execFileSync("python3", [path.join(ROOT, "tools/verify_markdown.py")], {
    encoding: "utf8",
  });
  assert.match(out, /fehlend\s+:\s+0/, out);
  assert.match(out, /zusätzlich\s+:\s+0/, out);
});

test("every chapter of the book has a Markdown file", () => {
  assert.ok(chapterFiles.length >= 18, `only ${chapterFiles.length} chapter files`);
  for (const file of chapterFiles) {
    const text = readFileSync(path.join(ROOT, "content", file), "utf8");
    assert.ok(text.startsWith("---\ntitle: "), `${file} has no front matter`);
    assert.ok(text.length > 100, `${file} is empty`);
  }
});

test("the chronicle is chronological", () => {
  const years = content.epochs.flatMap((e) => e.years.map((y) => y.year));
  assert.ok(years.length > 450, `only ${years.length} years`);
  for (let i = 1; i < years.length; i++) {
    assert.ok(years[i] >= years[i - 1], `year ${years[i]} follows ${years[i - 1]}`);
  }
  assert.ok(years[0] >= 900 && years.at(-1) <= 2025);
  for (const epoch of content.epochs) {
    for (const year of epoch.years) {
      const n = year.groups.reduce((sum, g) => sum + g.blocks.length, 0);
      assert.ok(n > 0, `year ${year.year} is empty`);
    }
  }
});

test("no block is an artefact of the old export", () => {
  const tocLine = /^\d+(\.\d+)*[A-ZÄÖÜ].{0,80}\d{2,4}$/;
  for (const block of allBlocks) {
    if (typeof block.text !== "string") continue;
    assert.ok(block.text.length > 0, "empty text block");
    assert.ok(!tocLine.test(block.text), `table-of-contents leftover: ${block.text}`);
    assert.ok(!block.text.startsWith("#"), `markdown heading leftover: ${block.text}`);
  }
});

test("sources are separated from the prose", () => {
  const inline = allBlocks.filter(
    (b) => typeof b.text === "string" && /\(Quelle\s*:[^)]*\)\s*$/i.test(b.text),
  );
  assert.equal(inline.length, 0, `${inline.length} paragraphs still end in a source`);
  assert.ok(allBlocks.filter((b) => b.type === "source").length > 500);
});

test("songs are set as verse, not as paragraphs", () => {
  const verses = allBlocks.filter((b) => b.type === "verse");
  assert.ok(verses.length >= 8, `only ${verses.length} verse blocks`);
  for (const verse of verses) assert.ok(verse.lines.length >= 2);
  const liedgut = content.chapters.find((c) => c.slug === "liedgut");
  assert.ok(liedgut.sections.some((s) => s.blocks.some((b) => b.type === "verse")));
});

test("the dialect dictionary is paired term by term", () => {
  const mundart = content.chapters.find((c) => c.slug === "die-heimatliche-mundart");
  const glossaries = mundart.sections.flatMap((s) =>
    s.blocks.filter((b) => b.type === "glossary"),
  );
  assert.ok(glossaries.length >= 20, `only ${glossaries.length} glossary blocks`);
  const pairs = glossaries.flatMap((g) => g.pairs);
  assert.ok(pairs.length > 90, `only ${pairs.length} word pairs`);
  const known = new Map([["aber", "awwer"], ["Pferd", "Gaul"], ["Friedhof", "Käschhop"]]);
  for (const [term, form] of known) {
    const hit = pairs.find((p) => p.term === term);
    assert.ok(hit, `missing dictionary entry ${term}`);
    assert.equal(hit.form, form, `${term} is paired wrongly`);
  }
});

test("every referenced image exists in the optimised set", () => {
  const referenced = new Set(allBlocks.filter((b) => b.type === "image").map((b) => b.file));
  assert.ok(referenced.size > 600, `only ${referenced.size} images referenced`);
  for (const file of referenced) {
    assert.ok(images[file], `no optimised version of ${file}`);
    assert.ok(images[file].width > 0 && images[file].height > 0, `bad size for ${file}`);
  }
});

test("the register only holds plausible names", () => {
  assert.ok(content.register.length >= 4);
  for (const office of content.register) {
    for (const holder of office.holders) {
      assert.match(holder.name, /^[A-ZÄÖÜ]/, `odd name: ${holder.name}`);
      assert.ok(holder.name.length <= 48, `overlong name: ${holder.name}`);
      for (const year of holder.years) assert.ok(year >= 1000 && year <= 2025);
    }
  }
});
