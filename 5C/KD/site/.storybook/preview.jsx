import React from 'react';
import { MemoryRouter } from 'react-router-dom';
import App from '../src/App.jsx';
import '../src/styles/tokens-wireframe.css';
import '../src/styles/tokens-full.css';
import '../src/styles/base.css';

export const decorators = [
  (Story, { parameters }) => (
    <MemoryRouter initialEntries={[parameters.route || '/wireframe']}>
      <App />
    </MemoryRouter>
  ),
];

export const parameters = {
  viewport: {
    viewports: {
      desktop: { name: 'Desktop 1440x900', styles: { width: '1440px', height: '900px' } },
      mobile: { name: 'Mobile 390x844', styles: { width: '390px', height: '844px' } },
    },
    defaultViewport: 'desktop',
  },
};
