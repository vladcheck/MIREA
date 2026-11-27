import Placeholder from './Placeholder.jsx';
import './Hero.css';

export default function Hero({ image }) {
  return (
    <section className="hero">
      <div className="hero-left">
        <h1>Высшая математика — просто и доступно</h1>
        <p className="sub">
          Разобранные примеры, теория «на пальцах» и помощь с контрольными —
          бесплатно, 24/7
        </p>
        <div className="hero-search">
          <input
            className="search-input"
            type="text"
            placeholder="Найти тему: пределы, производные, матрицы…"
          />
          <a className="btn btn-filled" href="#services">
            Заказать решение
          </a>
          <a className="btn btn-outlined" href="#themes">
            Найти тему
          </a>
        </div>
        <p className="trust">
          Бесплатные материалы · <b>Автор — преподаватель математики</b> ·
          Проект с 2010 года
        </p>
      </div>
      <Placeholder className="hero-img" src={image?.src} alt={image?.alt} />
    </section>
  );
}
