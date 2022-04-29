import React from 'react';

import LogoSVG from '@src/assets/logo.svg';

export default function Page200() {
  return (
    <div className="w-100 h-100 d-flex align-items-center justify-content-center flex-direction-column">
      <div className="d-flex align-items-center justify-content-center">
        <LogoSVG className="m-16" />
        <div className="sf-vertical-divider sf-vertical-divider-sm" />
        <h3 className="m-16 sf-text-color-primary">It Works!</h3>
      </div>
    </div>
  );
}
