const path = require('path');

const DashboardPlugin = require('webpack-dashboard/plugin');
const { merge } = require('webpack-merge');

const base = require('./base');
const constants = require('./constants');

module.exports = merge(base, {
  mode: 'development',
  devtool: 'cheap-module-source-map',
  plugins: [new DashboardPlugin()],
  optimization: {
    removeAvailableModules: false,
    removeEmptyChunks: false,
    splitChunks: false,
  },
  output: {
    pathinfo: false,
    globalObject: 'this',
  },
  devServer: {
    hot: 'only',
    host: '0.0.0.0',
    port: 9000,
    historyApiFallback: true,
    client: {
      overlay: {
        warnings: true,
        errors: true,
      },
    },
    static: [
      { directory: constants.SRC },
      {
        directory: path.resolve(path.join('./src', 'assets')),
        publicPath: '/assets',
        serveIndex: true,
        watch: true,
      },
    ],
    devMiddleware: {
      stats: 'errors-only',
    },
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        use: ['babel-loader'],
        exclude: /node_modules/,
        include: constants.SRC,
      },
    ],
  },
});
