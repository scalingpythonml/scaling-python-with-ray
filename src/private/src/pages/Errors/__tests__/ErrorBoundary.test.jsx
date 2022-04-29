import React from 'react';

import ErrorBoundary from '../ErrorBoundary';

describe('ErrorBoundary', () => {
  it('should render without errors', () => {
    const component = <ErrorBoundary />;
    expect(component).toMatchSnapshot();
  });
});
