import './Footer.css';

const SECTIONS = [
  ['Темы', '#themes'],
  ['Услуги', '#services'],
  ['Отзывы', '#reviews'],
  ['Об авторе', '#about'],
];

export default function Footer({ variant }) {
  return (
    <footer className="footer" id="contacts">
      <div>
        <div className="logo">
          {variant === 'wireframe' ? 'Лого' : 'Матпрофи'}
        </div>
        <p className="footer-tagline">Высшая математика — просто и доступно</p>
      </div>
      <div className="footer-col footer-col-1">
        <div className="footer-col-title">Разделы</div>
        {SECTIONS.map(([label, href]) => (
          <a key={href} href={href}>
            {label}
          </a>
        ))}
      </div>
      <div className="footer-col footer-col-2">
        <div className="footer-col-title">Контакты</div>
        <span>e-mail: help@матпрофи.ru</span>
        <span>ВК: vk.com/матпрофи</span>
        <span>Ответим в течение пары часов</span>
      </div>
    </footer>
  );
}
