import { render } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App.jsx';

function renderAt(path) {
  render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>
  );
}

describe('variants', () => {
  it('wireframe renders zero <img>', () => {
    renderAt('/wireframe');
    expect(document.querySelectorAll('img')).toHaveLength(0);
  });

  it('full renders images with unsplash sources', () => {
    renderAt('/full');
    const imgs = document.querySelectorAll('img');
    expect(imgs.length).toBeGreaterThan(0);
    for (const img of imgs) {
      expect(img.getAttribute('src')).toMatch(/unsplash/);
    }
  });

  it('wireframe renders 12 desktop bars + 8 mobile bars', () => {
    renderAt('/wireframe');
    expect(document.querySelectorAll('.guides-desktop > div')).toHaveLength(12);
    expect(document.querySelectorAll('.guides-mobile > div')).toHaveLength(8);
  });

  it('full renders no GuideBars', () => {
    renderAt('/full');
    expect(document.querySelector('.guides')).toBeNull();
  });

  it('wireframe wraps page in theme-wireframe, full in theme-full', () => {
    renderAt('/wireframe');
    expect(document.querySelector('.page.theme-wireframe')).toBeInTheDocument();
    renderAt('/full');
    expect(document.querySelector('.page.theme-full')).toBeInTheDocument();
  });
});
