import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App.jsx';

function renderAt(initialEntries) {
  return render(
    <MemoryRouter initialEntries={initialEntries}>
      <App />
    </MemoryRouter>
  );
}

describe.each([
  ['wireframe', '/wireframe'],
  ['full', '/full'],
])('landing (%s)', (_variant, path) => {
  it('renders the h1 hero title exactly once', () => {
    renderAt([path]);
    const h1s = screen.getAllByRole('heading', { level: 1 });
    expect(h1s).toHaveLength(1);
    expect(h1s[0]).toHaveTextContent('Высшая математика — просто и доступно');
  });

  it('has nav links Темы, Услуги, Отзывы, Об авторе, Контакты', () => {
    renderAt([path]);
    for (const label of ['Темы', 'Услуги', 'Отзывы', 'Об авторе', 'Контакты']) {
      expect(screen.getAllByRole('link', { name: label }).length).toBeGreaterThan(0);
    }
  });

  it('has header actions Найти тему and Заказать решение', () => {
    renderAt([path]);
    expect(screen.getAllByRole('link', { name: 'Найти тему' }).length).toBeGreaterThan(0);
    expect(
      screen.getAllByRole('link', { name: 'Заказать решение' }).length
    ).toBeGreaterThan(0);
  });

  it('renders 6 topics, 3 services, 3 reviews', () => {
    renderAt([path]);
    expect(document.querySelectorAll('.themes-section .card')).toHaveLength(6);
    expect(document.querySelectorAll('.services .card-outlined')).toHaveLength(3);
    expect(document.querySelectorAll('.reviews .card')).toHaveLength(3);
  });

  it('CTA has an email input and a submit button', () => {
    renderAt([path]);
    expect(screen.getByPlaceholderText('Ваш e-mail')).toBeInTheDocument();
    expect(screen.getByRole('link', { name: 'Подписаться' })).toBeInTheDocument();
  });

  it('renders sections in order Hero → Темы → Услуги → Об авторе → Отзывы → CTA → Footer', () => {
    renderAt([path]);
    const order = [
      '.hero',
      '.themes-section',
      '.services',
      '.about',
      '.reviews',
      '.cta',
      '.footer',
    ];
    const positions = order.map((sel) => {
      const el = document.querySelector(sel);
      const all = [...document.querySelectorAll('.page *')];
      return all.indexOf(el);
    });
    expect(positions.every((p) => p >= 0)).toBe(true);
    expect(positions).toEqual([...positions].sort((a, b) => a - b));
  });

  it('uses final copy everywhere — no lorem/filler text', () => {
    renderAt([path]);
    const text = document.body.textContent;
    expect(text).not.toMatch(/lorem|ipsum|рыб[ау]|placeholder text/i);
    expect(text).toContain('Высшая математика — просто и доступно');
    expect(text).toContain('Разобранные примеры');
  });
});
