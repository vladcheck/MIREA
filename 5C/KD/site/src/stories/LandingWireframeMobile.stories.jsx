import { wireframeMobileCheck } from './checks.js';

export default {
  title: 'Pages/Landing Wireframe Mobile',
  parameters: { viewport: { defaultViewport: 'mobile' }, route: '/wireframe' },
};

export const Mobile = {
  play: async ({ canvasElement }) => wireframeMobileCheck(canvasElement),
};
