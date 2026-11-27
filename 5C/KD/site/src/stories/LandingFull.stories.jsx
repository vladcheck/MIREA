import { fullDesktopCheck } from './checks.js';

export default {
  title: 'Pages/Landing Full Desktop',
  parameters: { viewport: { defaultViewport: 'desktop' }, route: '/full' },
};

export const Desktop = {
  play: async ({ canvasElement }) => fullDesktopCheck(canvasElement),
};
