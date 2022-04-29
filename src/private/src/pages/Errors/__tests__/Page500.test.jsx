import React from 'react';

import Page500 from '../Page500';

describe('Page500', () => {
  it('should render without errors', () => {
    const component = <Page500 />;
    expect(component).toMatchSnapshot();
  });
});
