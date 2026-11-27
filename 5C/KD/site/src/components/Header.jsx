import { Link } from 'react-router-dom';
import './Header.css';

const NAV = [
  ['Темы', '#themes'],
  ['Услуги', '#services'],
  ['Отзывы', '#reviews'],
  ['Об авторе', '#about'],
  ['Контакты', '#contacts'],
];

export default function Header({ variant }) {
  return (
    <header className="header">
      <div className="logo">{variant === 'wireframe' ? 'Лого' : 'Матпрофи'}</div>
      <nav className="nav">
        {NAV.map(([label, href]) => (
          <a key={href} href={href}>
            {label}
          </a>
        ))}
      </nav>
      <div className="header-actions">
        <a className="btn btn-outlined" href="#themes">
          Найти тему
        </a>
        <a className="btn btn-filled" href="#services">
          Заказать решение
        </a>
      </div>
      <Link className="burger" to={`/${variant}/popups/menu`} aria-label="Меню">
        ☰
      </Link>
    </header>
  );
}
