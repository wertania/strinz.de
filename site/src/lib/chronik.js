// Loads the prepared chronicle and derives everything the pages need.
// The JSON files are produced by ../../tools/*.py and scripts/optimize-images.mjs.

import content from "../../../data/content.json";
import outline from "../../../data/outline.json";
import images from "../../../data/images.json";

export const stats = content.stats;
export const register = content.register;
export const imageMeta = images;

/** The 16 parts of the book, plus the appendix, without the year chronicle. */
export const parts = content.parts
  .map((part) => ({
    ...part,
    sections: part.sections.filter((s) => s.blocks.length > 0),
  }))
  .filter((part) => part.number !== "7" && part.sections.length > 0);

export const partsBySlug = new Map(parts.map((p) => [p.slug, p]));

/** Every heading of the original book, whether or not text could be attached. */
export const fullOutline = outline.outline;

const rendered = new Set(parts.flatMap((p) => p.sections.map((s) => s.number)));
export const isRendered = (number) => rendered.has(number);

export const sectionAnchor = (section) => `abschnitt-${section.number.replace(/\./g, "-")}`;

// ---------------------------------------------------------------- chronicle --

export const years = content.years;

/** The book's own division of the chronicle into epochs. */
export const epochs = outline.chronikParts
  .map((part) => {
    const from = part.from ?? -Infinity;
    const to = part.to ?? part.from ?? Infinity;
    const own = years.filter((y) => y.year >= from && y.year <= to);
    return {
      ...part,
      slug: slugifyEpoch(part.title),
      label: epochLabel(part),
      years: own,
      entries: own.reduce(
        (n, y) => n + y.groups.reduce((m, g) => m + g.blocks.length, 0),
        0,
      ),
    };
  })
  .filter((e) => e.years.length > 0);

export const epochBySlug = new Map(epochs.map((e) => [e.slug, e]));

function epochLabel(part) {
  if (part.from === null) return "Vor Christi Geburt";
  if (/Weltkrieg/i.test(part.title)) return "Der Erste Weltkrieg 1914–1918";
  const range = part.title.match(/(\d{3,4})\s*[–-]\s*(\d{3,4})/);
  if (range) return `${range[1]}–${range[2]}`;
  return part.title.replace(/^Chronik\s+(von\s+)?/i, "");
}

function slugifyEpoch(title) {
  const range = title.match(/(\d{3,4})\s*[–-]\s*(\d{3,4})/);
  if (range) return `${range[1]}-${range[2]}`;
  if (/vor Christi/i.test(title)) return "vor-christi-geburt";
  return title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

export const epochOf = (year) => epochs.find((e) => e.years.some((y) => y.year === year));

// ------------------------------------------------------------------ images --

/** Every plate in reading order, with the place it appears. */
export const plates = (() => {
  const out = [];
  const seen = new Set();
  const push = (file, context, href) => {
    if (!imageMeta[file] || seen.has(file)) return;
    seen.add(file);
    out.push({ file, ...imageMeta[file], context, href });
  };
  for (const epoch of epochs) {
    for (const year of epoch.years) {
      for (const group of year.groups) {
        for (const block of group.blocks) {
          if (block.type === "image") push(block.file, String(year.year), `/chronik/${epoch.slug}/#jahr-${year.year}`);
        }
      }
    }
  }
  for (const part of parts) {
    for (const section of part.sections) {
      for (const block of section.blocks) {
        if (block.type === "image") {
          push(block.file, section.title, `/kapitel/${part.slug}/#${sectionAnchor(section)}`);
        }
      }
    }
  }
  return out;
})();

// ------------------------------------------------------------------ search --

/** A compact index for the client-side search. */
export function searchIndex() {
  const docs = [];
  const clip = (blocks) =>
    blocks
      .filter((b) => b.type === "paragraph" || b.type === "verse")
      .map((b) => (b.type === "verse" ? b.lines.join(" ") : b.text))
      .join(" ")
      .slice(0, 1400);

  for (const part of parts) {
    for (const section of part.sections) {
      docs.push({
        t: section.title,
        k: part.title,
        u: `/kapitel/${part.slug}/#${sectionAnchor(section)}`,
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
