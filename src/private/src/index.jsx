import React from 'react';
import ReactDOM from 'react-dom';

import * as Sentry from '@sentry/browser';

import App from './App';

if (process.env.NODE_ENV === 'production') {
  Sentry.init({
    dsn: process.env.SENTRY_DSN_FRONTEND,
    environment: process.env.ENVIRONMENT,
    // Or however deep you want your state context to be.
    normalizeDepth: 10,
    // We recommend adjusting this value in production, or using tracesSampler
    // for finer control
    tracesSampleRate: 0,
  });
}

const target = document.getElementById('root');
ReactDOM.render(<App />, target);
