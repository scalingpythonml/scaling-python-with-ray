import React from 'react';
import { Link } from 'react-router-dom';

export default function Page500() {
  return (
    <div className="w-100 h-100 d-flex align-items-center justify-content-center flex-direction-column">
      <h3 className="sf-text-color-primary"> 500 | Internal Server Error</h3>
      <h4>
        <Link to="/">Go to main page</Link>
      </h4>
    </div>
  );
}
