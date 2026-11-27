import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from '../App.jsx';

function renderAt(path) {
  render(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>
  );
}

describe('popup content', () => {
  it('order: name, contact fields and Отправить заявку', () => {
    renderAt('/wireframe/popups/order');
    expect(screen.getByPlaceholderText('Ваше имя')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('E-mail / телефон')).toBeInTheDocument();
    expect(screen.getByText('Отправить заявку')).toBeInTheDocument();
  });

  it('prices: at least 4 rows containing ₽', () => {
    renderAt('/wireframe/popups/prices');
    const rows = document.querySelectorAll('.price-row');
    expect(rows.length).toBeGreaterThanOrEqual(4);
    for (const row of rows) {
      expect(row.textContent).toMatch(/₽/);
    }
  });

  it('consult: date/time field and Записаться', () => {
    renderAt('/wireframe/popups/consult');
    expect(screen.getByPlaceholderText('Удобные дата и время')).toBeInTheDocument();
    expect(screen.getByText('Записаться')).toBeInTheDocument();
  });

  it('write-author: textarea Ваше сообщение and Отправить сообщение', () => {
    renderAt('/wireframe/popups/write-author');
    const textarea = screen.getByPlaceholderText('Ваше сообщение');
    expect(textarea.tagName).toBe('TEXTAREA');
    expect(screen.getByText('Отправить сообщение')).toBeInTheDocument();
  });

  it('menu: 5 nav links and a ✕ close control', () => {
    renderAt('/wireframe/popups/menu');
    const links = [...document.querySelectorAll('.menu-nav a')].map((a) =>
      a.textContent
    );
    expect(links).toEqual(['Темы', 'Услуги', 'Отзывы', 'Об авторе', 'Контакты']);
    expect(screen.getByText('✕')).toBeInTheDocument();
  });
});
