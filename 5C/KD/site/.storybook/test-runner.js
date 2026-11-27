import { getStoryContext } from '@storybook/test-runner';

const DEFAULT_VIEWPORT_SIZE = { width: 1440, height: 900 };

const testRunnerConfig = {
  async preVisit(page, story) {
    const context = await getStoryContext(page, story);
    const viewportName = context.parameters?.viewport?.defaultViewport;
    const viewportParameter = context.parameters?.viewport?.viewports?.[viewportName];
    if (viewportParameter && viewportParameter.styles) {
      const size = Object.entries(viewportParameter.styles).reduce(
        (acc, [screen, size]) => ({
          ...acc,
          [screen.toLowerCase()]: Number(String(size).replace(/\D+$/g, '')),
        }),
        {}
      );
      await page.setViewportSize(size);
    } else {
      await page.setViewportSize(DEFAULT_VIEWPORT_SIZE);
    }
  },
};

export default testRunnerConfig;
