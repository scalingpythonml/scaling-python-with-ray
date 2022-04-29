const path = require('path');

const envalid = require('envalid');

module.exports = {
  SRC: path.resolve(path.join('.', 'src')),
  APP: path.resolve(path.join('./src', 'index')),
  DIST: path.resolve(path.join('../static', 'dist')),
  VARS: envalid.cleanEnv(
    process.env,
    {
      __ENV__: envalid.str(),
      SSL: envalid.str(),
      ENVIRONMENT: envalid.str(),
      NODE_ENV: envalid.str(),
      DOMAIN: envalid.str(),
      STATIC_URL: envalid.str(),
      MEDIA_URL: envalid.str(),
      SENTRY_DSN_FRONTEND: envalid.str(),
    },
    { strict: true }
  ),
};
