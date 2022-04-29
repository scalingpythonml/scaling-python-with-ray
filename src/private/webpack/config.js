const localConf = require('./local');
const productionConf = require('./production');

module.exports = (() => {
  switch (process.env.NODE_ENV) {
    case 'production':
      return productionConf;
    default:
      return localConf;
  }
})();
