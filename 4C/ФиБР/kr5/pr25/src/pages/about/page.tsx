import { Suspense, useEffect, useState } from "react";
import Header from "../../shared/Header";

export default function AboutPage() {
  return <>
    <Header />
    <main>
      <section id="who-are-we">
        <h2>Кто мы?</h2>
        <p>Мы - команда независимых разработчиков, которая решает важную миссию: отсутствие магазинов подушек в России.</p>
        <Suspense fallback={<i>Загружаем...</i>}>
          <DelayedImageSimple />
        </Suspense>
      </section>
    </main>
  </>
}

function DelayedImageSimple() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      setShow(true);
    }, Math.min(1000, 100 + Math.random() * 1000));

    return () => clearTimeout(timer);
  }, []);

  if (!show) {
    return <div>Загружаем...</div>;
  }

  return <img src="/matress.png" width={600} alt="matress" />;
}
