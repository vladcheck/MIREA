import './Services.css';

const SERVICES = [
  {
    title: 'Заказ решения задач',
    body: 'Пришлёшь условие — получишь готовое решение с пояснениями к каждому шагу.',
    button: 'Заказать',
    kind: 'btn-filled',
  },
  {
    title: 'Консультация перед зачётом',
    body: 'Разберём твои вопросы онлайн в удобное время и повторим всё, что попадётся на зачёте.',
    button: 'Подробнее',
    kind: 'btn-outlined',
  },
  {
    title: 'Цены и тарифы',
    body: 'Разовая задача, пакет на сессию или сопровождение. Студентам — скидка.',
    button: 'Подробнее',
    kind: 'btn-outlined',
  },
];

export default function Services() {
  return (
    <section className="section services" id="services">
      <h2>Услуги</h2>
      <p className="sub">Поможем сдать — от консультации до полного решения</p>
      <div className="grid-3">
        {SERVICES.map((service) => (
          <div className="card-outlined" key={service.title}>
            <div className="card-title">{service.title}</div>
            <p className="card-body">{service.body}</p>
            <a className={`btn ${service.kind}`} href="#">
              {service.button}
            </a>
          </div>
        ))}
      </div>
    </section>
  );
}
