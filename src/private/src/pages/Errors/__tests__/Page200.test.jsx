import React from 'react';

import Page200 from '../Page200';

describe('Page200', () => {
  it('should render without errors', () => {
    const component = <Page200 />;
    expect(component).toMatchSnapshot();
  });
});
