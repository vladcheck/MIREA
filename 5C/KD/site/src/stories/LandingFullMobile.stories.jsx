import { fullMobileCheck } from './checks.js';

export default {
  title: 'Pages/Landing Full Mobile',
  parameters: { viewport: { defaultViewport: 'mobile' }, route: '/full' },
};

export const Mobile = {
  play: async ({ canvasElement }) => fullMobileCheck(canvasElement),
};
