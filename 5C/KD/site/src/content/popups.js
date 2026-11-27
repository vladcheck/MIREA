// The five popups, ported from pr4/popup.html and pr6/design/popup*.html.
export const POPUPS = {
  order: {
    id: 'order',
    caption: 'попап заказать решение задач',
    title: 'Заказать решение задач',
    fields: [
      { type: 'input', placeholder: 'Ваше имя' },
      { type: 'input', placeholder: 'E-mail / телефон' },
      { type: 'textarea', placeholder: 'Опишите задание или прикрепите файл' },
    ],
    submit: 'Отправить заявку',
    hint: 'Ответим в течение пары часов',
  },
  prices: {
    id: 'prices',
    caption: 'попап цены',
    title: 'Цены на занятия',
    priceRows: [
      ['Консультация', 'от 1500 ₽ / час'],
      ['Решение задач', 'от 500 ₽ / задача'],
      ['Подготовка к ЕГЭ', 'от 2000 ₽ / час'],
      ['Подготовка к ОГЭ', 'от 1800 ₽ / час'],
    ],
    hint: 'Первичная консультация — бесплатно',
  },
  consult: {
    id: 'consult',
    caption: 'попап назначить консультацию',
    title: 'Назначить консультацию',
    fields: [
      { type: 'input', placeholder: 'Ваше имя' },
      { type: 'input', placeholder: 'Телефон или e-mail' },
      { type: 'input', placeholder: 'Удобные дата и время' },
    ],
    submit: 'Записаться',
    hint: 'Подтвердим время в течение часа',
  },
  'write-author': {
    id: 'write-author',
    caption: 'попап написать автору',
    title: 'Написать автору',
    fields: [
      { type: 'input', placeholder: 'Ваше имя' },
      { type: 'input', placeholder: 'E-mail для ответа' },
      { type: 'textarea', placeholder: 'Ваше сообщение' },
    ],
    submit: 'Отправить сообщение',
    hint: null,
  },
  menu: {
    id: 'menu',
    caption: 'попап меню (по кнопке ☰)',
    menu: true,
    navLinks: [
      ['Темы', '#themes'],
      ['Услуги', '#services'],
      ['Отзывы', '#reviews'],
      ['Об авторе', '#about'],
      ['Контакты', '#contacts'],
    ],
  },
};

export const POPUP_IDS = Object.keys(POPUPS);
