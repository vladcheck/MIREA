import { popupCheck, menuPopupCheck } from './checks.js';

export default {
  title: 'Pages/Popups',
  parameters: { viewport: { defaultViewport: 'desktop' } },
};

const popupStory = (id, heading, viewport = 'desktop') => ({
  parameters: { viewport: { defaultViewport: viewport }, route: `/wireframe/popups/${id}` },
  play: async ({ canvasElement }) => popupCheck(heading)(canvasElement),
});

export const OrderWireframe = popupStory('order', 'Заказать решение задач');
export const PricesWireframe = popupStory('prices', 'Цены на занятия');
export const ConsultWireframe = popupStory('consult', 'Назначить консультацию');
export const WriteAuthorFull = {
  ...popupStory('write-author', 'Написать автору'),
  parameters: { viewport: { defaultViewport: 'desktop' }, route: '/full/popups/write-author' },
};
export const OrderFull = {
  ...popupStory('order', 'Заказать решение задач'),
  parameters: { viewport: { defaultViewport: 'desktop' }, route: '/full/popups/order' },
};
export const PricesFull = {
  ...popupStory('prices', 'Цены на занятия'),
  parameters: { viewport: { defaultViewport: 'desktop' }, route: '/full/popups/prices' },
};
export const MenuWireframeMobile = {
  parameters: { viewport: { defaultViewport: 'mobile' }, route: '/wireframe/popups/menu' },
  play: async ({ canvasElement }) => menuPopupCheck(canvasElement),
};
export const MenuFullMobile = {
  parameters: { viewport: { defaultViewport: 'mobile' }, route: '/full/popups/menu' },
  play: async ({ canvasElement }) => menuPopupCheck(canvasElement),
};
