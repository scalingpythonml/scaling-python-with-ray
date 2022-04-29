const path = require('path');

module.exports = {
  root: true,
  env: {
    browser: true,
    es6: true,
    jest: true,
  },
  extends: ['plugin:react/recommended', 'airbnb', 'prettier'],
  plugins: ['react', 'react-hooks', 'import'],
  globals: {
    Atomics: 'readonly',
    SharedArrayBuffer: 'readonly',
  },
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
    allowImportExportEverywhere: false,
    requireConfigFile: false,
    ecmaFeatures: {
      globalReturn: false,
    },
  },
  rules: {
    // General
    'prefer-const': 'error',
    'prefer-arrow-callback': 0,
    'prefer-object-spread': 0,
    camelcase: ['error', { ignoreDestructuring: true }],
    'comma-dangle': ['error', 'only-multiline'],
    'no-nested-ternary': 1,
    'no-underscore-dangle': 0,
    'array-callback-return': 0,
    'consistent-return': 0,
    'func-names': ['error', 'never'],
    'arrow-body-style': [0, 'as-needed'],
    'max-classes-per-file': ['error', { ignoreExpressions: true, max: 2 }],
    // React rules
    'react/jsx-pascal-case': [2, { allowAllCaps: false }],
    'react/jsx-filename-extension': [2, { extensions: ['.js', '.jsx'] }],
    'react/require-default-props': 0,
    'react/destructuring-assignment': 0,
    'react/no-multi-comp': 0,
    'react/forbid-prop-types': 0,
    'react/prop-types': 0,
    'react/no-unused-prop-types': 0,
    'react/jsx-boolean-value': 0,
    'react/no-array-index-key': 0,
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    'react/jsx-props-no-spreading': 0,
    'react/function-component-definition': [2, { namedComponents: 'function-declaration' }],
    // Import rules
    'import/first': 'error',
    'import/no-duplicates': 'error',
    'import/newline-after-import': 'error',
    'import/prefer-default-export': 'off',
    'import/no-extraneous-dependencies': ['error', { devDependencies: true }],
    'import/extensions': [
      'error',
      'ignorePackages',
      {
        js: 'never',
        jsx: 'never',
      },
    ],
    'import/order': [
      'error',
      {
        groups: ['builtin', 'external', 'internal', ['parent', 'sibling'], 'index', 'object'],
        pathGroups: [
          {
            pattern: 'react+(|-router-dom|-dom)',
            group: 'external',
            position: 'before',
          },
          {
            pattern: 'prop-types',
            group: 'external',
            position: 'before',
          },
          {
            pattern: '@src/**',
            group: 'internal',
            position: 'before',
          },
        ],
        'newlines-between': 'always',
        pathGroupsExcludedImportTypes: ['react'],
        alphabetize: {
          order: 'asc',
          caseInsensitive: true,
        },
      },
    ],
  },
  settings: {
    'import/resolver': {
      alias: {
        map: [['@src', path.resolve(path.join(__dirname, 'src'))]],
        extensions: ['.js', '.jsx'],
      },
    },
  },
};
