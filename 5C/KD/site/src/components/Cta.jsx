import './Cta.css';

export default function Cta() {
  return (
    <section className="section cta">
      <h2>Получи подборку «Топ-10 тем высшей математики»</h2>
      <p className="sub">Оставь e-mail — пришлём полезные материалы</p>
      <div className="cta-form">
        <input className="email-input" type="email" placeholder="Ваш e-mail" />
        <a className="btn btn-filled cta-btn" href="#">
          Подписаться
        </a>
      </div>
    </section>
  );
}
