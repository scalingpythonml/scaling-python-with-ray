import '@src/styles/global.scss';

import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

import { Provider } from 'react-redux'

import { ProviderComposer } from '@src/components';
import { ErrorBoundary, Page200, Page404, Page500 } from '@src/pages';
import store from '@src/store';

const PROVIDERS = [
  [Provider, { store }],
];

export default function App() {
  return (
    <ErrorBoundary>
      <BrowserRouter>
        <ProviderComposer providers={PROVIDERS}>
        <Routes>
          <Route path="/" name="index" element={<Page200 />} />
          <Route path="404" name="404" element={<Page404 />} />
          <Route path="500" name="500" element={<Page500 />} />
          <Route path="*" element={<Page404 />} />
        </Routes>
        </ProviderComposer>
      </BrowserRouter>
    </ErrorBoundary>
  );
}
