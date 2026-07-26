// Checks on the reconstructed data. These guard the pipeline, not the design:
// if a future change to tools/*.py silently loses content or scrambles the
// order again, these fail.

import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const read = (p) => JSON.parse(readFileSync(path.join(ROOT, p), "utf8"));

const content = read("data/content.json");
const outline = read("data/outline.json");
const images = read("data/images.json");

const allBlocks = [
  ...content.parts.flatMap((p) => p.sections.flatMap((s) => s.blocks)),
  ...content.years.flatMap((y) => y.groups.flatMap((g) => g.blocks)),
];

test("the outline covers the whole book", () => {
  assert.ok(outline.outline.length >= 200, `only ${outline.outline.length} outline entries`);
  assert.equal(outline.parts.length, 16);
  for (const entry of outline.outline) {
    assert.ok(entry.title.length > 1, `empty title for ${entry.number}`);
    assert.ok(entry.page > 0 && entry.page <= 780, `bad page for ${entry.number}`);
  }
});

test("outline entries are numbered in ascending order", () => {
  const key = (n) => n.split(".").map(Number);
  const nums = outline.outline.map((e) => key(e.number));
  for (let i = 1; i < nums.length; i++) {
    assert.ok(
      compare(nums[i - 1], nums[i]) < 0,
      `${outline.outline[i - 1].number} should sort before ${outline.outline[i].number}`,
    );
  }
  function compare(a, b) {
    for (let i = 0; i < Math.max(a.length, b.length); i++) {
      const d = (a[i] ?? -1) - (b[i] ?? -1);
      if (d) return d;
    }
    return 0;
  }
});

test("the year chronicle is chronological and plausible", () => {
  const years = content.years.map((y) => y.year);
  assert.ok(years.length > 400, `only ${years.length} years`);
  for (let i = 1; i < years.length; i++) {
    assert.ok(years[i] > years[i - 1], `year ${years[i]} follows ${years[i - 1]}`);
  }
  assert.ok(years[0] >= 900 && years.at(-1) <= 2025);
});

test("every year carries content", () => {
  for (const year of content.years) {
    const n = year.groups.reduce((sum, g) => sum + g.blocks.length, 0);
    assert.ok(n > 0, `year ${year.year} is empty`);
  }
});

test("no block is an unresolved artefact of the extraction", () => {
  const tocLine = /^\d+(\.\d+)*[A-ZÄÖÜ].{0,80}\d{2,4}$/;
  for (const block of allBlocks) {
    if (block.type !== "paragraph") continue;
    assert.ok(block.text.length > 0, "empty paragraph");
    assert.ok(!tocLine.test(block.text), `table-of-contents leftover: ${block.text}`);
    assert.ok(!block.text.startsWith("#"), `markdown heading leftover: ${block.text}`);
  }
});

test("sources are split off, not left inline", () => {
  const inline = allBlocks.filter(
    (b) => b.type === "paragraph" && /\(Quelle\s*:[^)]*\)\s*$/i.test(b.text),
  );
  assert.equal(inline.length, 0, `${inline.length} paragraphs still end in a source`);
});

test("no section repeats the same line twice", () => {
  for (const part of content.parts) {
    for (const section of part.sections) {
      const short = section.blocks
        .filter((b) => b.type === "paragraph" && b.text.length < 200)
        .map((b) => b.text);
      assert.equal(new Set(short).size, short.length, `duplicates in ${section.number}`);
    }
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
      if (holder.from) assert.ok(holder.from >= 1000 && holder.to <= 2025);
    }
  }
});

test("nothing was silently dropped", () => {
  // Every stream item ends up as a block, a rubric label, a duplicate or a
  // table-of-contents leftover. Allow for those, but not for wholesale loss.
  assert.ok(
    content.stats.blocks / content.stats.streamItems > 0.7,
    `only ${content.stats.blocks} of ${content.stats.streamItems} items placed`,
  );
});
