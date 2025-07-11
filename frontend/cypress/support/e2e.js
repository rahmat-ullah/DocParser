// ***********************************************************
// This file is processed and loaded automatically before test files.
// You can change the location of this file or turn off loading
// the support files entirely in the 'supportFile' configuration option.
// ***********************************************************

// Import commands.js
import './commands'

// Alternatively you can use CommonJS syntax:
// require('./commands')

// Global error handler to prevent Cypress from failing tests due to uncaught exceptions
Cypress.on('uncaught:exception', (err, runnable) => {
  // Returning false here prevents Cypress from failing the test
  // You might want to log the error or handle specific cases
  console.error('Uncaught exception:', err);
  return false;
});
