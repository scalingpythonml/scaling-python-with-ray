import { configureStore } from '@reduxjs/toolkit';
import logger from 'redux-logger';
import thunk from 'redux-thunk';

// https://redux-toolkit.js.org/api/configureStore

// Provider you reducers here
export default configureStore({
  reducer: {},
  middleware: [thunk, logger],
})
