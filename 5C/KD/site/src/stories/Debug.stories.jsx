import { expect } from '@storybook/test';

export default {
  title: 'Debug/Viewport',
  parameters: { viewport: { defaultViewport: 'mobile' }, route: '/wireframe' },
};

// Sanity probe: the mobile viewport parameter (390px) must actually apply.
export const Probe = {
  play: async ({ canvasElement }) => {
    const w = canvasElement.ownerDocument.documentElement.clientWidth;
    expect(w).toBe(390);
  },
};
