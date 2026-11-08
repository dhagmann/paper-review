#!/usr/bin/env node
// Local HTML -> bookmarked PDF; dependency paths are discovered or supplied.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { pathToFileURL } = require('node:url');

const [htmlFile, pdfFile, ...args] = process.argv.slice(2);
if (!htmlFile || !pdfFile) throw new Error('Usage: render_pdf.js input.html output.pdf [--browser path] [--playwright-module path] [--preview-dir path]');
const options = {};
for (let i = 0; i < args.length; i += 2) {
  if (!['--browser', '--playwright-module', '--preview-dir'].includes(args[i]) || !args[i + 1]) {
    throw new Error('Invalid renderer option.');
  }
  options[args[i]] = args[i + 1];
}

function playwrightModule() {
  const explicit = options['--playwright-module'] || process.env.PAPER_REVIEW_PLAYWRIGHT_MODULE;
  if (explicit) return require(path.resolve(explicit));
  for (const name of ['playwright', 'playwright-core']) {
    try { return require(name); } catch (error) {
      if (error.code !== 'MODULE_NOT_FOUND') throw error;
    }
  }
  const cache = path.join(os.homedir(), '.npm', '_npx');
  if (fs.existsSync(cache)) {
    for (const dir of fs.readdirSync(cache).sort()) {
      const candidate = path.join(cache, dir, 'node_modules', 'playwright');
      if (fs.existsSync(path.join(candidate, 'package.json'))) return require(candidate);
    }
  }
  throw new Error('Playwright is unavailable. Supply --playwright-module or install it in the project environment. HTML remains available.');
}

function browserPath(chromium) {
  const explicit = options['--browser'] || process.env.PAPER_REVIEW_CHROMIUM;
  if (explicit) {
    if (!fs.existsSync(explicit)) throw new Error('Configured Chromium executable does not exist.');
    return path.resolve(explicit);
  }
  const builtIn = chromium.executablePath();
  if (fs.existsSync(builtIn)) return builtIn;
  const cache = path.join(os.homedir(), '.cache', 'ms-playwright');
  if (fs.existsSync(cache)) {
    for (const dir of fs.readdirSync(cache).sort().reverse()) {
      if (!/^chromium-\d+$/.test(dir)) continue;
      for (const suffix of ['chrome-linux64/chrome', 'chrome-linux/chrome', 'chrome-win/chrome.exe']) {
        const candidate = path.join(cache, dir, suffix);
        if (fs.existsSync(candidate)) return candidate;
      }
    }
  }
  for (const dir of (process.env.PATH || '').split(path.delimiter)) {
    for (const name of ['google-chrome', 'chromium', 'chromium-browser']) {
      const candidate = path.join(dir, name);
      if (fs.existsSync(candidate)) return candidate;
    }
  }
  throw new Error('Chromium is unavailable. Supply --browser or use an appropriate PDF tool. HTML remains available.');
}

(async () => {
  const { chromium } = playwrightModule();
  const browser = await chromium.launch({
    executablePath: browserPath(chromium), headless: true,
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });
  try {
    const page = await browser.newPage({ viewport: { width: 1200, height: 1500 } });
    await page.route(/^https?:\/\//, route => route.abort());
    await page.goto(pathToFileURL(path.resolve(htmlFile)).href, { waitUntil: 'load' });
    await page.evaluate(() => document.fonts.ready);
    if (options['--preview-dir']) {
      const dir = path.resolve(options['--preview-dir']);
      fs.mkdirSync(dir, { recursive: true });
      const firstIssue = page.locator('article.issue').first();
      const count = await page.locator('article.issue').count();
      if (count === 1) {
        await page.evaluate(() => window.scrollTo(0, 0));
        await page.screenshot({ path: path.join(dir, 'first-issue.png'), fullPage: true });
      } else if (count) await firstIssue.screenshot({ path: path.join(dir, 'first-issue.png') });
    }
    await page.pdf({
      path: path.resolve(pdfFile), printBackground: true, preferCSSPageSize: true,
      outline: true, tagged: true, displayHeaderFooter: true,
      headerTemplate: '<div style="font-family:Arial,sans-serif;font-size:7px;color:#7c8797;width:100%;padding:0 0.65in">Paper review · proposed manuscript edits</div>',
      footerTemplate: '<div style="font-family:Arial,sans-serif;font-size:7px;color:#7c8797;width:100%;text-align:center">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>',
    });
    console.log('PDF created from the report HTML.');
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error.message); process.exit(1); });
