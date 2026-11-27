import { wireframeDesktopCheck } from './checks.js';

export default {
  title: 'Pages/Landing Wireframe Desktop',
  parameters: { viewport: { defaultViewport: 'desktop' }, route: '/wireframe' },
};

export const Desktop = {
  play: async ({ canvasElement }) => wireframeDesktopCheck(canvasElement),
};
