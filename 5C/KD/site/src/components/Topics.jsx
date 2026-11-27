import Placeholder from './Placeholder.jsx';
import './Topics.css';

const TOPICS = [
  {
    title: 'Высшая математика для чайников',
    body: 'Пределы, производные и интегралы на примерах. Начни с нуля — без страшных формул.',
  },
  {
    title: 'Пределы и производные',
    body: 'Разбор задач из контрольных шаг за шагом. Таблица производных и правила дифференцирования.',
  },
  {
    title: 'Интегралы и ряды',
    body: 'Интегралы с решениями — от простых к сложным. Ряды — от числовых к функциональным.',
  },
  {
    title: 'Матрицы и определители',
    body: 'Действия с матрицами, ранг и обратная матрица. Решение систем методом Крамера и Гаусса.',
  },
  {
    title: 'Теория вероятностей',
    body: 'Классическое определение и формулы вероятности. Задачи с монетами, кубиками и урнами.',
  },
  {
    title: 'Статистика',
    body: 'Выборки, доверительные интервалы и гипотезы. Обработка данных для лабораторных работ.',
  },
];

export default function Topics({ images }) {
  return (
    <section className="section themes-section" id="themes">
      <h2>Темы</h2>
      <p className="sub">Выбери раздел — и начинай с понятной теории</p>
      <div className="grid-3 themes">
        {TOPICS.map((topic, i) => (
          <div className="card theme-card" key={topic.title}>
            <Placeholder
              className="card-img"
              src={images?.topics?.[i]?.src}
              alt={images?.topics?.[i]?.alt}
            />
            <div className="card-title">{topic.title}</div>
            <p className="card-body">{topic.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
