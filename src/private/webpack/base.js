require('core-js/stable');
require('regenerator-runtime/runtime');

const path = require('path');

const FaviconsWebpackPlugin = require('favicons-webpack-plugin');
const HtmlWebpackHarddiskPlugin = require('html-webpack-harddisk-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MomentLocalesPlugin = require('moment-locales-webpack-plugin');
const webpack = require('webpack');

const constants = require('./constants');

const devMode = process.env.NODE_ENV === 'development';
const bundleCSS = devMode ? 'bundle.css' : '[contenthash].css';
const bundleJS = devMode ? 'bundle.js' : '[contenthash].js';

module.exports = {
  entry: ['core-js/stable', 'regenerator-runtime/runtime', constants.APP],
  output: {
    path: constants.DIST,
    filename: bundleJS,
    publicPath: `${constants.VARS.STATIC_URL}dist/`,
  },
  plugins: [
    new webpack.EnvironmentPlugin([
      'SSL',
      'NODE_ENV',
      'ENVIRONMENT',
      'DOMAIN',
      'STATIC_URL',
      'MEDIA_URL',
      'SENTRY_DSN_FRONTEND',
    ]),
    new webpack.LoaderOptionsPlugin({
      debug: constants.DEVELOPMENT,
      options: {
        context: constants.SRC,
        output: {
          path: constants.DIST,
        },
      },
    }),
    new MomentLocalesPlugin({
      // 'en' is built into Moment
      localesToKeep: [],
    }),
    new HtmlWebpackPlugin({
      cache: !devMode,
      template: path.resolve(path.join(constants.SRC, 'index.ejs')),
      alwaysWriteToDisk: true,
      filename: 'index.html',
      compile: true,
      showErrors: true,
      chunks: 'all',
      excludeChunks: [],
      css: [bundleCSS],
    }),
    new HtmlWebpackHarddiskPlugin({
      outputPath: constants.SRC,
    }),
    new FaviconsWebpackPlugin({
      logo: path.resolve(path.join(constants.SRC, 'assets', 'favicon.png')),
      devMode: 'webapp',
    }),
  ],
  resolve: {
    alias: {
      '@src': path.resolve(path.join(constants.SRC)),
    },
    modules: [constants.SRC, 'node_modules'],
    extensions: ['*', '.json', '.js', '.jsx', '.css'],
  },
  module: {
    rules: [
      {
        test: /\.(jpe?g|png|gif)$/,
        type: 'asset/resource',
      },
      {
        test: /\.(pdf)$/,
        type: 'asset/resource',
      },
      {
        test: /\.svg(\?v=\d+\.\d+\.\d+)?$/,
        use: ['@svgr/webpack'],
      },
      {
        test: /\.(woff|woff2|eot|ttf)$/,
        type: 'asset/inline',
      },
      {
        test: /\.s[ac]ss$/i,
        use: [
          // Creates `style` nodes from JS strings
          'style-loader',
          // Translates CSS into CommonJS
          'css-loader',
          // Compiles Sass to CSS
          'sass-loader',
        ],
      },
      {
        test: /\.js$/,
        use: 'babel-loader',
        exclude: /node_modules\/(?!tributejs)/,
      },
    ],
  },
};
