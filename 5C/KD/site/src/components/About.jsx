import Placeholder from './Placeholder.jsx';
import './About.css';

export default function About({ image }) {
  return (
    <section className="section about" id="about">
      <div className="about-inner">
        <Placeholder className="avatar" src={image?.src} alt={image?.alt} />
        <h2>Александр — преподаватель математики</h2>
        <p className="about-text">
          Более 15 лет объясняю высшую математику студентам так, чтобы её
          понимали даже «чайники». На сайте — мои авторские разборы, примеры и
          методички, которыми я пользуюсь на занятиях.
        </p>
        <a className="btn btn-outlined" href="#contacts">
          Написать автору
        </a>
      </div>
    </section>
  );
}
