import { expect } from '@storybook/test';

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

// Image assertions, network-tolerant: when images.unsplash.com is reachable
// enforce strictly (all imgs loaded); when it's down, fall back to "src is a
// non-empty unsplash URL and no img fired error" so sandbox outages don't
// fail the story while locally broken images still do.
const expectImagesLoaded = async (_page, canvas) => {
  const imgs = Array.from(canvas.querySelectorAll('img'));
  expect(imgs.length).toBeGreaterThanOrEqual(1);
  // Lazy images below the fold never load until scrolled in — bring each
  // into view so every one gets a load attempt before we assert.
  for (const i of imgs) {
    i.scrollIntoView({ block: 'center' });
    await sleep(100);
  }
  imgs[0]?.scrollIntoView({ block: 'center' });
  await sleep(300);
  const errors = imgs.map((i) => {
    let fired = false;
    i.addEventListener('error', () => {
      fired = true;
    });
    return () => fired;
  });
  await Promise.all(imgs.map((i) => Promise.race([i.decode().catch(() => {}), sleep(3000)])));
  // Probe the network from inside the browser context (checks only receive
  // the canvas element, no Playwright page). no-cors HEAD to unsplash yields
  // an opaque response on success — resolves true iff DNS/TLS work.
  const networkUp = await Promise.race([
    (canvas.ownerDocument.defaultView || window)
      .fetch('https://images.unsplash.com/favicon.ico', { method: 'HEAD', mode: 'no-cors' })
      .then(() => true)
      .catch(() => false),
    sleep(4000).then(() => false),
  ]);
  if (networkUp) {
    const loaded = imgs.filter((i) => i.naturalWidth > 0);
    expect(loaded.length).toBe(imgs.length);
  } else {
    // eslint-disable-next-line no-console
    console.log('network unavailable — image assertions skipped');
    imgs.forEach((i, n) => {
      const src = i.getAttribute('src') || '';
      expect(src.length).toBeGreaterThan(0);
      expect(src).toContain('unsplash');
      expect(errors[n]()).toBe(false);
    });
  }
  return imgs;
};

// ПР3 card-grid band + row-gutter checks, shared by desktop stories.
// Band: content band is x=150..1290 (1140px); every card-like element must sit
// inside it (±2px). Gutter: horizontally adjacent cards in the same row must
// have ≥18px between them (desktop grid gap is 20px — catches sticking).
export const checkCardGrids = (page) => {
  const isCardLike = (el) =>
    /card/.test(el.className) || (el.parentElement && /grid-3/.test(el.parentElement.className));
  const cards = Array.from(page.querySelectorAll('[class*="card"], .grid-3 > *')).filter((el) => {
    if (!isCardLike(el)) return false;
    const box = el.getBoundingClientRect();
    const parentCard = el.parentElement && isCardLike(el.parentElement);
    return box.width > 0 && box.height > 0 && !parentCard;
  });
  expect(cards.length).toBeGreaterThan(0);
  const seen = new Set();
  for (const el of cards) {
    if (seen.has(el)) continue;
    seen.add(el);
    const box = el.getBoundingClientRect();
    expect(box.left).toBeGreaterThanOrEqual(148);
    expect(box.right).toBeLessThanOrEqual(1292);
  }

  // Row grouping: same row when tops within 10px; then check horizontal gaps.
  const rects = cards.map((el) => ({ el, box: el.getBoundingClientRect() }));
  rects.sort((a, b) => a.box.top - b.box.top || a.box.left - b.box.left);
  const rows = [];
  for (const r of rects) {
    const row = rows.find((row) => Math.abs(row[0].box.top - r.box.top) <= 10);
    if (row) row.push(r);
    else rows.push([r]);
  }
  let gapChecks = 0;
  for (const row of rows) {
    row.sort((a, b) => a.box.left - b.box.left);
    for (let i = 1; i < row.length; i++) {
      const gap = row[i].box.left - row[i - 1].box.right;
      expect(gap).toBeGreaterThanOrEqual(18);
      gapChecks++;
    }
  }
  expect(gapChecks).toBeGreaterThan(0);
};

// Band containment («весь контент в одном контейнере с полосками»):
// exactly one .band inside .page spanning the 150px/16px grid, and EVERY
// rendered descendant stays within band edges — children may only shrink.
export const checkBandContainment = (page) => {
  const bands = page.querySelectorAll(':scope > .band');
  expect(bands.length).toBe(1);
  const band = bands[0];
  const cs = getComputedStyle(band);
  expect(cs.overflowX).toBe('hidden');
  const inset = Math.round(parseFloat(cs.marginLeft));
  const expectedInset = document.documentElement.clientWidth <= 768 ? 16 : 150;
  expect(inset).toBe(expectedInset);
  expect(Math.abs(parseFloat(cs.marginRight) - inset)).toBeLessThanOrEqual(1);

  const bandRect = band.getBoundingClientRect();
  const pageRect = page.getBoundingClientRect();
  expect(Math.abs(bandRect.left - pageRect.left - inset)).toBeLessThanOrEqual(1);
  expect(Math.abs(pageRect.right - bandRect.right - inset)).toBeLessThanOrEqual(1);

  // Layout proof: no descendant forces horizontal overflow past the band.
  expect(band.scrollWidth).toBeLessThanOrEqual(band.clientWidth + 1);

  // Paint proof: every rendered descendant sits within band edges (±1px).
  let checked = 0;
  for (const el of band.querySelectorAll('*')) {
    const elCs = getComputedStyle(el);
    if (elCs.display === 'none') continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 && r.height === 0) continue;
    expect(r.left).toBeGreaterThanOrEqual(bandRect.left - 1);
    expect(r.right).toBeLessThanOrEqual(bandRect.right + 1);
    checked++;
  }
  expect(checked).toBeGreaterThan(0);
};


export const wireframeDesktopCheck = async (canvas) => {
  await sleep(300);
  const page = canvas.querySelector('.page.theme-wireframe');
  expect(page).not.toBeNull();

  // Header 100–120, hero 600–800
  const header = canvas.querySelector('header') ?? page.querySelector('.site-header');
  const headerBox = (header ?? page.children[1]).getBoundingClientRect();
  expect(headerBox.height).toBeGreaterThanOrEqual(100);
  expect(headerBox.height).toBeLessThanOrEqual(120);
  const hero = canvas.querySelector('.hero');
  expect(hero.getBoundingClientRect().height).toBeGreaterThanOrEqual(600);
  expect(hero.getBoundingClientRect().height).toBeLessThanOrEqual(800);

  // Sections are Band children: they span the band (150..1290 on the page);
  // the 150px inset lives in the Band margin, not in section padding.
  for (const s of page.querySelectorAll('section')) {
    const box = s.getBoundingClientRect();
    if (box.right - box.left > 100) {
      expect(box.left).toBeGreaterThanOrEqual(150 - 2);
      expect(box.right).toBeLessThanOrEqual(1290 + 2);
    }
  }

  checkBandContainment(page);

  // Exactly 12 visible desktop bars, width 76.66±1.5, gap 20±1, red translucent, no pointer events
  const bars = Array.from(page.querySelectorAll('.guides-desktop > div')).filter(
    (b) => getComputedStyle(b).display !== 'none'
  );
  expect(bars.length).toBe(12);
  const rects = bars.map((b) => b.getBoundingClientRect());
  for (const r of rects) {
    expect(Math.abs(r.width - 76.66)).toBeLessThanOrEqual(1.5);
  }
  for (let i = 1; i < rects.length; i++) {
    expect(Math.abs(rects[i].left - rects[i - 1].right - 20)).toBeLessThanOrEqual(1);
  }
  const style = getComputedStyle(bars[0]);
  expect(style.backgroundColor).toMatch(/rgba\(240,\s*128,\s*128/);
  expect(style.pointerEvents).toBe('none');

  // Divider color rgb(154,154,154)
  const divider = page.querySelector('.divider');
  expect(divider).not.toBeNull();
  const dParts = getComputedStyle(divider).backgroundColor;
  expect(dParts.replace(/\s+/g, '')).toBe('rgb(154,154,154)');

  // No <img> in wireframe
  expect(canvas.querySelectorAll('img').length).toBe(0);

  // No full-theme accent color anywhere
  const all = canvas.querySelectorAll('*');
  for (const el of all) {
    const c = getComputedStyle(el).color;
    expect(c.startsWith('rgb(31, 78, 140)')).toBe(false);
  }

  // ПР3 grid alignment: content stays inside the 150px grid band (0..1440 page).
  const gridTargets = [
    ...page.querySelectorAll('h1, h2, .themes-section .card, .services .card-outlined'),
  ];
  expect(gridTargets.length).toBeGreaterThan(0);
  for (const el of gridTargets) {
    const box = el.getBoundingClientRect();
    if (box.width === 0) continue;
    expect(box.left).toBeGreaterThanOrEqual(150 - 2);
    expect(box.right).toBeLessThanOrEqual(1290 + 2);
  }
  checkCardGrids(page);


  // ПР3 grayscale: every element-level computed color/background is gray or the guide red.
  const isGrayscaleish = (c) => {
    if (!c || c === 'transparent' || c === 'rgba(0, 0, 0, 0)') return true;
    const m = c.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
    if (!m) return false;
    if (m[4] !== undefined && parseFloat(m[4]) === 0) return true;
    const [r, g, b] = [Number(m[1]), Number(m[2]), Number(m[3])];
    if (r === 240 && g === 128 && b === 128) return true; // guide-bar red family
    return r === g && g === b;
  };
  for (const el of canvas.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || el.getBoundingClientRect().width === 0) continue;
    expect(isGrayscaleish(cs.color)).toBe(true);
    expect(isGrayscaleish(cs.backgroundColor)).toBe(true);
  }
};

export const wireframeMobileCheck = async (canvas) => {
  await sleep(300);
  const page = canvas.querySelector('.page.theme-wireframe');
  expect(page).not.toBeNull();

  const bars = Array.from(page.querySelectorAll('.guides-mobile > div')).filter(
    (b) => getComputedStyle(b).display !== 'none'
  );
  expect(bars.length).toBe(8);
  const rects = bars.map((b) => b.getBoundingClientRect());
  for (const r of rects) {
    expect(Math.abs(r.width - 36)).toBeLessThanOrEqual(1.5);
  }
  for (let i = 1; i < rects.length; i++) {
    expect(Math.abs(rects[i].left - rects[i - 1].right - 10)).toBeLessThanOrEqual(1);
  }
  const contRect = page.querySelector('.guides-mobile').getBoundingClientRect();
  const pageRect = page.getBoundingClientRect();
  // The 16px inset lives in the Band margin; bars span the band exactly.
  expect(Math.abs(contRect.left - pageRect.left - 16)).toBeLessThanOrEqual(1);
  expect(Math.abs(pageRect.right - contRect.right - 16)).toBeLessThanOrEqual(1);

  checkBandContainment(page);

  const burger = canvas.querySelector('.burger') ?? Array.from(canvas.querySelectorAll('button, [role="button"]')).find((b) => /burger|menu/i.test(b.className));
  expect(burger).not.toBeUndefined();
  expect(burger).not.toBeNull();
  const bb = burger.getBoundingClientRect();
  expect(Math.round(bb.width)).toBe(44);
  expect(Math.round(bb.height)).toBe(44);

  // Nav links hidden
  const navLinks = canvas.querySelectorAll('nav a');
  for (const a of navLinks) {
    const cs = getComputedStyle(a);
    const box = a.getBoundingClientRect();
    expect(cs.display === 'none' || box.width === 0).toBe(true);
  }

  // Interactive elements ≥44px tall
  const interactives = canvas.querySelectorAll('button, a.btn, input, textarea');
  for (const el of interactives) {
    if (getComputedStyle(el).display === 'none') continue;
    const box = el.getBoundingClientRect();
    if (box.height > 0) expect(box.height).toBeGreaterThanOrEqual(44);
  }

  expect(document.documentElement.scrollWidth).toBeLessThanOrEqual(391);

  // ПР5 CTA available on mobile: «Заказать решение» visible (in DOM, rendered).
  const ctas = Array.from(canvas.querySelectorAll('a.btn, button')).filter((el) =>
    el.textContent.includes('Заказать решение')
  );
  expect(ctas.length).toBeGreaterThan(0);
  expect(ctas.some((el) => el.offsetParent !== null)).toBe(true);

  // ПР5 compactness: first two topic cards stack vertically at full content width.
  const cards = Array.from(page.querySelectorAll('.themes-section .card, .themes .card')).filter(
    (el) => el.getBoundingClientRect().width > 0
  );
  expect(cards.length).toBeGreaterThanOrEqual(2);
  const c0 = cards[0].getBoundingClientRect();
  const c1 = cards[1].getBoundingClientRect();
  expect(Math.abs(c0.width - c1.width)).toBeLessThanOrEqual(2);
  expect(c1.top).toBeGreaterThan(c0.top);
  const contentWidth =
    pageRect.right - pageRect.left - 32; /* 16px inset each side */
  expect(Math.abs(c0.width - contentWidth)).toBeLessThanOrEqual(2);
};

export const fullDesktopCheck = async (canvas) => {
  await sleep(800);
  const page = canvas.querySelector('.page.theme-full');
  expect(page).not.toBeNull();

  const imgs = await expectImagesLoaded(page, canvas);

  const accent = Array.from(canvas.querySelectorAll('button, a.btn, .btn')).find((el) => {
    const c = getComputedStyle(el).backgroundColor.replace(/\s+/g, '');
    return c === 'rgb(31,78,140)';
  });
  expect(accent).toBeDefined();

  expect(canvas.querySelector('.guides')).toBeNull();

  // ПР6 «не более 4 цветов»: distinct non-gray computed colors.
  const isGray = (r, g, b) => r === g && g === b;
  const parseColor = (c) => {
    const m = c && c.match(/rgba?\((\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?\)/);
    if (!m) return null;
    if (m[4] !== undefined && parseFloat(m[4]) === 0) return null;
    return [Number(m[1]), Number(m[2]), Number(m[3])];
  };
  const nonGrays = new Set();
  for (const el of canvas.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || el.getBoundingClientRect().width === 0) continue;
    for (const c of [cs.color, cs.backgroundColor]) {
      const rgb = parseColor(c);
      if (rgb && !isGray(...rgb)) nonGrays.add(rgb.join(','));
    }
  }
  expect(nonGrays.size).toBeLessThanOrEqual(4);

  // ПР6 uniform border widths: every non-zero border-width uses the same token.
  const borderVals = new Set();
  for (const el of canvas.querySelectorAll('*')) {
    const cs = getComputedStyle(el);
    if (cs.display === 'none' || el.getBoundingClientRect().width === 0) continue;
    for (const side of ['Top', 'Right', 'Bottom', 'Left']) {
      const w = cs[`border${side}Width`];
      if (w && w !== '0px') borderVals.add(w);
    }
  }
  expect(Array.from(borderVals)).toHaveLength(1);

  // ПР6 uniform photo treatment: all imgs share one computed filter.
  const filters = new Set(
    imgs.filter((i) => i.getBoundingClientRect().width > 0).map((i) => getComputedStyle(i).filter)
  );
  expect(Array.from(filters)).toHaveLength(1);

  checkBandContainment(page);
  checkCardGrids(page);
};

export const fullMobileCheck = async (canvas) => {
  await sleep(800);
  const page = canvas.querySelector('.page.theme-full');
  expect(page).not.toBeNull();

  // ПР5/ПР6 no horizontal overflow at 391px viewport.
  expect(document.documentElement.scrollWidth).toBeLessThanOrEqual(391);

  checkBandContainment(page);

  // Interactive elements ≥44px tall.
  const interactives = canvas.querySelectorAll('button, a.btn, .btn, input, textarea, nav a');
  for (const el of interactives) {
    const cs = getComputedStyle(el);
    const box = el.getBoundingClientRect();
    if (cs.display === 'none' || box.height === 0) continue;
    expect(box.height).toBeGreaterThanOrEqual(44);
  }

  // ПР5 CTA available on mobile: accent button visible.
  const accentCandidates = Array.from(canvas.querySelectorAll('button, a.btn, .btn')).filter((el) => {
    const c = getComputedStyle(el).backgroundColor.replace(/\s+/g, '');
    return c === 'rgb(31,78,140)';
  });
  const accentBox0 = accentCandidates.map((el) => el.getBoundingClientRect()).find(
    (b) => b.width > 0 && b.height > 0
  );
  expect(accentBox0).toBeDefined();

  // Images actually loaded (lazy images need to be scrolled in).
  await expectImagesLoaded(page, canvas);
};

export function popupCheck(heading) {
  return async (canvas) => {
    await sleep(300);
    const modal = canvas.querySelector('.modal');
    expect(modal).not.toBeNull();
    const box = modal.getBoundingClientRect();
    expect(box.width).toBeGreaterThan(0);
    expect(box.height).toBeGreaterThan(0);
    const h2 = modal.querySelector('h2');
    if (h2) {
      expect(h2.textContent).toBe(heading);
    }
  };
}

export const menuPopupCheck = async (canvas) => {
  await sleep(300);
  const modal = canvas.querySelector('.modal');
  expect(modal).not.toBeNull();
  const links = modal.querySelectorAll('.menu-nav a');
  expect(links.length).toBe(5);
};
