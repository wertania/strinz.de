// End-to-end checks against the built site in site/dist.
// Run `npm run build` first; `npm test` in site/ does both.

import { test, before, after } from "node:test";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readFile, stat, readdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "../..");
const DIST = path.join(ROOT, "site/dist");

const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript",
  ".css": "text/css",
  ".json": "application/json",
  ".webp": "image/webp",
  ".svg": "image/svg+xml",
  ".woff2": "font/woff2",
  ".xml": "application/xml",
  ".txt": "text/plain",
};

let server;
let base;
let browser;

before(async () => {
  server = createServer(async (req, res) => {
    let file = path.join(DIST, decodeURIComponent(req.url.split("?")[0]));
    try {
      if ((await stat(file)).isDirectory()) file = path.join(file, "index.html");
    } catch {
      res.writeHead(404).end("not found");
      return;
    }
    try {
      const body = await readFile(file);
      res.writeHead(200, { "content-type": TYPES[path.extname(file)] ?? "application/octet-stream" });
      res.end(body);
    } catch {
      res.writeHead(404).end("not found");
    }
  });
  await new Promise((r) => server.listen(0, r));
  base = `http://127.0.0.1:${server.address().port}`;
  // this sandbox ships a prepared Chromium; CI uses the one Playwright installs
  const local = "/opt/pw-browsers/chromium";
  browser = await chromium.launch(existsSync(local) ? { executablePath: local } : {});
});

after(async () => {
  await browser?.close();
  server?.close();
});

const open = async (url, opts = {}) => {
  const page = await browser.newPage(opts);
  const problems = [];
  page.on("console", (m) => m.type() === "error" && problems.push(m.text()));
  page.on("pageerror", (e) => problems.push(String(e)));
  const res = await page.goto(base + url, { waitUntil: "networkidle" });
  assert.equal(res.status(), 200, `${url} returned ${res.status()}`);
  return { page, problems };
};

test("the build produced a fully static site", async () => {
  assert.ok(existsSync(path.join(DIST, "index.html")));
  const pages = [];
  const walk = async (dir) => {
    for (const entry of await readdir(dir, { withFileTypes: true })) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) await walk(full);
      else if (entry.name === "index.html") pages.push(full);
    }
  };
  await walk(DIST);
  assert.ok(pages.length >= 30, `only ${pages.length} pages built`);
});

test("the home page renders and has no console errors", async () => {
  const { page, problems } = await open("/");
  assert.equal(problems.length, 0, problems.join("\n"));
  assert.equal(await page.locator("h1").first().innerText(), "Strinz‑Margarethä");
  assert.ok((await page.locator(".stat").count()) >= 4);
  await page.close();
});

test("every internal link resolves", async () => {
  const { page } = await open("/kapitel/");
  const hrefs = await page.$$eval("a[href^='/']", (as) => [...new Set(as.map((a) => a.getAttribute("href")))]);
  await page.close();
  assert.ok(hrefs.length > 20);
  for (const href of hrefs) {
    const res = await fetch(base + href.split("#")[0]);
    assert.equal(res.status, 200, `${href} is broken`);
  }
});

test("a chronicle page shows years, rubrics and sources", async () => {
  const { page, problems } = await open("/chronik/chronik-von-1800-1899/");
  assert.equal(problems.length, 0, problems.join("\n"));
  assert.ok((await page.locator("article.year").count()) > 50);
  assert.ok((await page.locator(".rubric").count()) > 50);
  assert.ok((await page.locator("cite.source").count()) > 10);
  const first = page.locator("article.year").first();
  assert.match(await first.locator(".year__label").innerText(), /^1[89]\d\d$/);
  await page.close();
});

test("a chapter page shows its sections and images", async () => {
  const { page, problems } = await open("/kapitel/strinzer-geschichten/");
  assert.equal(problems.length, 0, problems.join("\n"));
  assert.ok((await page.locator("section.section").count()) > 5);
  const broken = await page.$$eval("img", (imgs) =>
    imgs.filter((i) => i.complete && i.naturalWidth === 0).map((i) => i.src),
  );
  assert.deepEqual(broken, [], "broken images");
  await page.close();
});

test("no image on the gallery page fails to load", async () => {
  const { page } = await open("/bilder/");
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  await page.waitForTimeout(1500);
  const broken = await page.$$eval("img", (imgs) =>
    imgs.filter((i) => i.complete && i.naturalWidth === 0).map((i) => i.getAttribute("src")),
  );
  assert.deepEqual(broken, [], "broken thumbnails");
  await page.close();
});

test("the search finds a known entry", async () => {
  const { page, problems } = await open("/suche/");
  await page.fill("#q", "Starfighter");
  await page.waitForFunction(() => document.querySelectorAll("#treffer li").length > 0, null, { timeout: 5000 });
  const first = await page.locator("#treffer li").first().innerText();
  assert.match(first, /Starfighter/i);
  assert.equal(problems.length, 0, problems.join("\n"));
  await page.close();
});

test("the page does not scroll sideways on a phone", async () => {
  for (const url of ["/", "/chronik/chronik-von-1900-1914-kriegsbeginn/", "/kapitel/die-heimatliche-mundart/", "/register/"]) {
    const { page } = await open(url, { viewport: { width: 360, height: 780 } });
    const overflow = await page.evaluate(
      () => document.documentElement.scrollWidth - document.documentElement.clientWidth,
    );
    assert.ok(overflow <= 1, `${url} overflows by ${overflow}px`);
    await page.close();
  }
});

test("the dark theme applies", async () => {
  const { page } = await open("/", { colorScheme: "dark" });
  const bg = await page.evaluate(() => getComputedStyle(document.body).backgroundColor);
  assert.notEqual(bg, "rgb(246, 242, 234)", "still the light paper colour");
  await page.close();
});

test("pages carry title, description and canonical", async () => {
  for (const url of ["/", "/chronik/", "/kapitel/strinzer-geschichten/", "/ueber/"]) {
    const { page } = await open(url);
    assert.ok((await page.title()).includes("Strinz-Margarethä"), `${url} title`);
    const desc = await page.getAttribute('meta[name="description"]', "content");
    assert.ok(desc && desc.length > 40, `${url} description`);
    assert.ok(await page.getAttribute('link[rel="canonical"]', "href"), `${url} canonical`);
    await page.close();
  }
});
