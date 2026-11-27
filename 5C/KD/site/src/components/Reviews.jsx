import Placeholder from './Placeholder.jsx';
import './Reviews.css';

const REVIEWS = [
  {
    name: 'Анна, 1 курс',
    quote:
      '«Пределы объяснили за один вечер — на контрольной решила всё сама. Теперь здесь готовлюсь к каждой».',
  },
  {
    name: 'Дмитрий, заочное',
    quote:
      '«Учусь удалённо, некому спросить. Матрицы и определители наконец встали на свои места. Спасибо!»',
  },
  {
    name: 'Ольга, 2 курс',
    quote:
      '«Заказала консультацию перед зачётом — разобрали все типовые задачи. Зачёт сдала на отлично!»',
  },
];

export default function Reviews({ images }) {
  return (
    <section className="section reviews" id="reviews">
      <h2>Отзывы</h2>
      <div className="grid-3 reviews-grid">
        {REVIEWS.map((review, i) => (
          <div className="card" key={review.name}>
            <div className="review-head">
              <Placeholder
                className="review-avatar"
                src={images?.reviews?.[i]?.src}
                alt={images?.reviews?.[i]?.alt}
              />
              <div className="card-title">{review.name}</div>
            </div>
            <p className="review-quote">{review.quote}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
