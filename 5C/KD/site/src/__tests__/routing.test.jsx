import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App.jsx';

const POPUP_TITLES = {
  order: 'Заказать решение задач',
  prices: 'Цены на занятия',
  consult: 'Назначить консультацию',
  'write-author': 'Написать автору',
  menu: null, // menu popup has no heading; checked via nav links in popups.test.jsx
};

function renderAt(path) {
  render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>
  );
}

describe('routing', () => {
  it('redirects / to /wireframe', () => {
    renderAt('/');
    expect(document.querySelector('.theme-wireframe')).toBeInTheDocument();
    expect(
      screen.getByRole('heading', { level: 1, name: /Высшая математика/ })
    ).toBeInTheDocument();
  });

  it('redirects unknown variant to /wireframe', () => {
    renderAt('/bogus');
    expect(document.querySelector('.theme-wireframe')).toBeInTheDocument();
  });

  it('shows Попап не найден for unknown popup id', () => {
    renderAt('/wireframe/popups/nope');
    expect(screen.getByText('Попап не найден')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'На главную' })).toBeInTheDocument();
  });
});

describe.each([
  ['wireframe'],
  ['full'],
])('popup ids render on %s', (variant) => {
  for (const [id, title] of Object.entries(POPUP_TITLES)) {
    const itFn = id === 'menu' ? it.skip : it;
    itFn(`renders ${id} popup`, () => {
      renderAt(`/${variant}/popups/${id}`);
      expect(screen.getByRole('heading', { level: 2, name: title })).toBeInTheDocument();
    });
  }

  it('renders menu popup nav links', () => {
    renderAt(`/${variant}/popups/menu`);
    expect(document.querySelectorAll('.menu-nav a')).toHaveLength(5);
    expect(screen.getByText('✕')).toBeInTheDocument();
  });
});
