import React from 'react';

const parse = (p) => (Array.isArray(p) ? [p[0], p[1]] : [p, {}]);

function ProviderComposer({ providers, children }) {
  return (
    <>
      {providers.reduceRight((hierarchy, provider) => {
        const [Provider, props] = parse(provider);
        return <Provider {...props}>{hierarchy}</Provider>;
      }, children)}
    </>
  );
}

ProviderComposer.displayName = 'ProviderComposer';

export default ProviderComposer;
