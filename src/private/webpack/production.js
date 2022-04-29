const { CleanWebpackPlugin } = require('clean-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const TerserPlugin = require('terser-webpack-plugin');
const { merge } = require('webpack-merge');
const WebpackBar = require('webpackbar');

const base = require('./base');
const constants = require('./constants');

module.exports = merge(base, {
  mode: 'production',
  devtool: 'nosources-source-map',
  performance: {
    maxEntrypointSize: 512000,
    maxAssetSize: 512000,
  },
  optimization: {
    minimize: true,
    minimizer: [
      new TerserPlugin({
        parallel: true,
        exclude: /\/vendors/,
      }),
    ],
    chunkIds: 'named',
    splitChunks: {
      cacheGroups: {
        commons: {
          chunks: 'all',
          name: 'commons',
          minChunks: 1,
          minSize: 3,
          priority: -20,
        },
        defaultVendors: {
          test: /[\\/]node_modules[\\/]/,
          name: 'vendors',
          chunks: 'all',
          priority: -10,
          enforce: true,
          reuseExistingChunk: true,
        },
      },
    },
  },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].[hash].css',
      chunkFilename: '[id].[hash].css',
    }),
    new CleanWebpackPlugin({
      cleanOnceBeforeBuildPatterns: ['**/*', '!.git', '!now.json'],
      protectWebpackAssets: false,
      cleanStaleWebpackAssets: true,
      verbose: true,
      dry: false,
      dangerouslyAllowCleanPatternsOutsideProject: true,
    }),
    new WebpackBar({
      name: 'Client (build)',
      color: 'blue',
      profile: true,
      fancy: true,
      basic: true,
    }),
  ],
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        use: 'babel-loader',
        exclude: /node_modules/,
        include: constants.SRC,
      },
    ],
  },
});
