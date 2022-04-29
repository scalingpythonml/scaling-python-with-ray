import React from 'react';

import App from '../App';

describe('App', () => {
  it('should render without errors', () => {
    const component = <App />;
    expect(component).toMatchSnapshot();
  });
});
