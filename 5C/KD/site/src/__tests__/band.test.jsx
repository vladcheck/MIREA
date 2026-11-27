import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App.jsx';

// jsdom cannot apply stylesheets, so geometry is enforced by the Storybook
// layer (checkBandContainment). Here: structure + the stylesheet contract,
// read from the real CSS sources (vitest stubs CSS imports to '').
const readCss = (rel) =>
  readFileSync(fileURLToPath(new URL(rel, import.meta.url)), 'utf8');
const bandCss = readCss('../components/Band.css');
const guideBarsCss = readCss('../components/GuideBars.css');

function renderAt(path) {
  render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>
  );
}

// The bars exist only in the wireframe theme.
describe.each([
  ['wireframe', '/wireframe', true],
  ['full', '/full', false],
])('band container (%s)', (_variant, path, wireframe) => {
  it('page has exactly one .band and NOTHING outside it', () => {
    renderAt(path);
    const page = document.querySelector('.page');
    expect(page).not.toBeNull();
    const bands = page.querySelectorAll(':scope > .band');
    expect(bands).toHaveLength(1);
    const band = bands[0];
    for (const el of page.querySelectorAll('*')) {
      expect(band.contains(el)).toBe(true);
    }
  });

  it('band owns the guide bars, all sections, dividers, header and footer', () => {
    renderAt(path);
    const band = document.querySelector('.band');
    expect(band.querySelector('.guides') !== null).toBe(wireframe);
    for (const sel of [
      'header',
      '.hero',
      '.themes-section',
      '.services',
      '.about',
      '.reviews',
      '.cta',
      '.footer',
    ]) {
      expect(band.querySelector(sel)).not.toBeNull();
    }
    expect(band.querySelectorAll('.divider')).toHaveLength(7);
    for (const section of document.querySelectorAll('.page section')) {
      expect(band.contains(section)).toBe(true);
    }
  });

  it('Band.css enforces clipping, insets and shrink-only children', () => {
    expect(bandCss).toMatch(/\.band\s*\{[^}]*margin:\s*0\s+150px/);
    expect(bandCss).toMatch(/\.band\s*\{[^}]*overflow:\s*hidden/);
    expect(bandCss).toMatch(/@media[^{]*\{[\s\S]*\.band\s*\{[^}]*margin:\s*0\s+16px/);
    expect(bandCss).toMatch(/\.band,\s*\.band \*\s*\{[^}]*min-width:\s*0/);
    expect(bandCss).toMatch(/\.band img[^{]*\{[^}]*max-width:\s*100%/);
    // The bars lost their own horizontal padding — the band owns the inset.
    expect(guideBarsCss).not.toMatch(/padding:\s*0\s+(150px|16px)/);
  });
});

describe('band container (popups)', () => {
  it('popup page keeps a single band holding the modal', () => {
    renderAt('/wireframe/popups/order');
    const page = document.querySelector('.popup-page');
    expect(page.querySelectorAll(':scope > .band')).toHaveLength(1);
    const band = page.querySelector(':scope > .band');
    expect(band.querySelector('.modal')).not.toBeNull();
    for (const el of page.querySelectorAll('*')) {
      expect(band.contains(el)).toBe(true);
    }
  });

  it('not-found popup also renders inside a single band', () => {
    renderAt('/wireframe/popups/nope');
    const page = document.querySelector('.popup-page');
    expect(page.querySelectorAll(':scope > .band')).toHaveLength(1);
    expect(page.querySelector(':scope > .band .modal')).not.toBeNull();
  });
});
