#!/usr/bin/env node

const fs = require('fs');
const path = require('path');

/**
 * Frontend .env.local Auto-Generation Script
 * 
 * This script handles the automatic generation of .env.local file from .env.local.example
 * when the .env.local file is absent. It provides default values pointing to localhost:8000
 * and allows overrides via command-line flags.
 * 
 * Usage:
 *   node setup-env.js [options]
 * 
 * Options:
 *   --api-url <url>     Override the API base URL (default: http://localhost:8000/api/v1)
 *   --ws-url <url>      Override the WebSocket URL (default: http://localhost:8000)
 *   --force             Force regeneration even if .env.local exists
 *   --help              Show this help message
 */

const DEFAULT_API_URL = 'http://localhost:8000/api/v1';
const DEFAULT_WS_URL = 'http://localhost:8000';

const ENV_LOCAL_PATH = path.join(__dirname, '.env.local');
const ENV_EXAMPLE_PATH = path.join(__dirname, '.env.local.example');

function parseArgs() {
  const args = process.argv.slice(2);
  const options = {
    apiUrl: DEFAULT_API_URL,
    wsUrl: DEFAULT_WS_URL,
    force: false,
    help: false
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    
    switch (arg) {
      case '--api-url':
        if (i + 1 < args.length) {
          options.apiUrl = args[++i];
        } else {
          console.error('Error: --api-url requires a URL argument');
          process.exit(1);
        }
        break;
      
      case '--ws-url':
        if (i + 1 < args.length) {
          options.wsUrl = args[++i];
        } else {
          console.error('Error: --ws-url requires a URL argument');
          process.exit(1);
        }
        break;
      
      case '--force':
        options.force = true;
        break;
      
      case '--help':
        options.help = true;
        break;
      
      default:
        console.error(`Error: Unknown option '${arg}'`);
        console.error('Use --help to see available options');
        process.exit(1);
    }
  }

  return options;
}

function showHelp() {
  console.log(`
Frontend .env.local Auto-Generation Script

This script handles the automatic generation of .env.local file from .env.local.example
when the .env.local file is absent. It provides default values pointing to localhost:8000
and allows overrides via command-line flags.

Usage:
  node setup-env.js [options]

Options:
  --api-url <url>     Override the API base URL (default: ${DEFAULT_API_URL})
  --ws-url <url>      Override the WebSocket URL (default: ${DEFAULT_WS_URL})
  --force             Force regeneration even if .env.local exists
  --help              Show this help message

Examples:
  node setup-env.js
  node setup-env.js --api-url http://localhost:3001/api/v1
  node setup-env.js --ws-url ws://localhost:3001 --force
  node setup-env.js --api-url http://api.example.com/v1 --ws-url ws://api.example.com
`);
}

function fileExists(filePath) {
  try {
    fs.accessSync(filePath, fs.constants.F_OK);
    return true;
  } catch (err) {
    return false;
  }
}

function generateEnvLocal(options) {
  // Check if .env.local.example exists
  if (!fileExists(ENV_EXAMPLE_PATH)) {
    console.error('Error: .env.local.example file not found');
    console.error('Please ensure .env.local.example exists in the frontend directory');
    process.exit(1);
  }

  // Check if .env.local already exists and not forcing
  if (fileExists(ENV_LOCAL_PATH) && !options.force) {
    console.log('✓ .env.local already exists');
    console.log('  Use --force to regenerate it');
    return;
  }

  try {
    // Read the template file
    const templateContent = fs.readFileSync(ENV_EXAMPLE_PATH, 'utf8');
    
    // Replace the default values with the provided options
    let envContent = templateContent
      .replace(/NEXT_PUBLIC_API_BASE_URL=.*$/m, `NEXT_PUBLIC_API_BASE_URL=${options.apiUrl}`)
      .replace(/NEXT_PUBLIC_WS_URL=.*$/m, `NEXT_PUBLIC_WS_URL=${options.wsUrl}`);

    // Write the new .env.local file
    fs.writeFileSync(ENV_LOCAL_PATH, envContent);
    
    const action = options.force ? 'regenerated' : 'created';
    console.log(`✓ .env.local ${action} successfully`);
    console.log(`  API URL: ${options.apiUrl}`);
    console.log(`  WebSocket URL: ${options.wsUrl}`);
    
  } catch (error) {
    console.error('Error generating .env.local:', error.message);
    process.exit(1);
  }
}

function main() {
  const options = parseArgs();
  
  if (options.help) {
    showHelp();
    return;
  }

  console.log('🔧 Frontend Environment Setup');
  console.log('==============================');
  
  generateEnvLocal(options);
  
  console.log('\n✅ Environment setup complete!');
  console.log('You can now run your frontend application.');
}

// Only run if this script is executed directly
if (require.main === module) {
  main();
}

module.exports = { generateEnvLocal, parseArgs, fileExists };
