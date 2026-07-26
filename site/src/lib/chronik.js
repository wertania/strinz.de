// Everything the pages need, derived from the prepared chronicle.
// data/content.json is written by ../../tools/build_site_data.py from the
// original Word document; data/images.json by scripts/optimize-images.mjs.

import content from "../../../data/content.json";
import images from "../../../data/images.json";

export const stats = content.stats;
export const register = content.register;
export const population = content.population;
export const imageMeta = images;

/** The chapters of the book, without the year chronicle. */
export const chapters = content.chapters;
export const chapterBySlug = new Map(chapters.map((c) => [c.slug, c]));

/** The chronicle, divided into the epochs the book itself uses. */
export const epochs = content.epochs.map((epoch) => ({
  ...epoch,
  label: epochLabel(epoch.title),
  entries: epoch.years.reduce(
    (n, y) => n + y.groups.reduce((m, g) => m + g.blocks.length, 0),
    0,
  ),
}));
export const epochBySlug = new Map(epochs.map((e) => [e.slug, e]));

function epochLabel(title) {
  const range = title.match(/(\d{3,4})\s*[–-]\s*(\d{3,4})/);
  if (range) return `${range[1]}–${range[2]}`;
  return title.replace(/^Chronik\s+(von\s+|des\s+)?/i, "");
}

/** Every plate in reading order, with the place it appears. */
export const plates = content.plates
  .filter((p) => imageMeta[p.file])
  .map((p) => ({ ...p, ...imageMeta[p.file] }));

/** A compact index for the client-side search. */
export function searchIndex() {
  const clip = (blocks) =>
    blocks
      .flatMap((b) =>
        b.type === "verse" ? b.lines
        : b.type === "glossary" ? b.pairs.map((p) => `${p.term} ${p.form}`)
        : b.type === "table" ? [...b.head, ...b.rows.flat()]
        : [b.text ?? ""],
      )
      .join(" ")
      .slice(0, 1400);

  const docs = [];
  for (const chapter of chapters) {
    for (const section of chapter.sections) {
      docs.push({
        t: section.title,
        k: chapter.title,
        u: `/kapitel/${chapter.slug}/#${section.slug}`,
        b: clip(section.blocks),
      });
    }
  }
  for (const epoch of epochs) {
    for (const year of epoch.years) {
      docs.push({
        t: String(year.year),
        k: "Chronik",
        u: `/chronik/${epoch.slug}/#jahr-${year.year}`,
        b: clip(year.groups.flatMap((g) => g.blocks)),
      });
    }
  }
  return docs;
}
