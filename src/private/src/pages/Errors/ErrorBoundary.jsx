import React from 'react';

import * as Sentry from '@sentry/browser';

import LogoSVG from '@src/assets/logo.svg';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, eventId: null };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    Sentry.withScope((scope) => {
      scope.setExtras(errorInfo);
      const eventId = Sentry.captureException(error);
      this.setState({ eventId });
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="w-100 h-100 d-flex align-items-center justify-content-center flex-direction-column">
          <div className="d-flex align-items-center justify-content-center">
            <LogoSVG className="m-16" />
            <div className="sf-vertical-divider sf-vertical-divider-sm" />
            <button
              type="button"
              className="m-16 sf-btn"
              onClick={() => Sentry.showReportDialog({ eventId: this.state.eventId })}
            >
              Report this error
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
