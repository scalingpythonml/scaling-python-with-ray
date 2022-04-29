import React from 'react';

import Page404 from '../Page404';

describe('Page404', () => {
  it('should render without errors', () => {
    const component = <Page404 />;
    expect(component).toMatchSnapshot();
  });
});
