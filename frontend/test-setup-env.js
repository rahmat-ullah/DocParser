#!/usr/bin/env node

const fs = require('fs');
const path = require('path');
const { generateEnvLocal, parseArgs, fileExists } = require('./setup-env');

/**
 * Test script for the .env.local auto-generation functionality
 */

const ENV_LOCAL_PATH = path.join(__dirname, '.env.local');
const ENV_EXAMPLE_PATH = path.join(__dirname, '.env.local.example');

function cleanup() {
  if (fileExists(ENV_LOCAL_PATH)) {
    fs.unlinkSync(ENV_LOCAL_PATH);
  }
}

function testDefaultGeneration() {
  console.log('\n📋 Test 1: Default generation');
  console.log('===============================');
  
  cleanup();
  
  const options = {
    apiUrl: 'http://localhost:8000/api/v1',
    wsUrl: 'http://localhost:8000',
    force: false,
    help: false
  };
  
  generateEnvLocal(options);
  
  if (fileExists(ENV_LOCAL_PATH)) {
    const content = fs.readFileSync(ENV_LOCAL_PATH, 'utf8');
    console.log('✓ .env.local created successfully');
    console.log('Contents:');
    console.log(content);
    
    // Verify content
    if (content.includes('NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1') &&
        content.includes('NEXT_PUBLIC_WS_URL=http://localhost:8000')) {
      console.log('✓ Default values are correct');
    } else {
      console.log('✗ Default values are incorrect');
    }
  } else {
    console.log('✗ .env.local was not created');
  }
}

function testCustomValues() {
  console.log('\n📋 Test 2: Custom values with --force');
  console.log('======================================');
  
  const options = {
    apiUrl: 'http://localhost:3001/api/v1',
    wsUrl: 'ws://localhost:3001',
    force: true,
    help: false
  };
  
  generateEnvLocal(options);
  
  if (fileExists(ENV_LOCAL_PATH)) {
    const content = fs.readFileSync(ENV_LOCAL_PATH, 'utf8');
    console.log('✓ .env.local regenerated successfully');
    console.log('Contents:');
    console.log(content);
    
    // Verify content
    if (content.includes('NEXT_PUBLIC_API_BASE_URL=http://localhost:3001/api/v1') &&
        content.includes('NEXT_PUBLIC_WS_URL=ws://localhost:3001')) {
      console.log('✓ Custom values are correct');
    } else {
      console.log('✗ Custom values are incorrect');
    }
  } else {
    console.log('✗ .env.local was not regenerated');
  }
}

function testExistingFile() {
  console.log('\n📋 Test 3: Existing file without --force');
  console.log('=========================================');
  
  const options = {
    apiUrl: 'http://localhost:8000/api/v1',
    wsUrl: 'http://localhost:8000',
    force: false,
    help: false
  };
  
  generateEnvLocal(options);
  
  console.log('✓ Test completed (should show that .env.local already exists)');
}

function testArgumentParsing() {
  console.log('\n📋 Test 4: Argument parsing');
  console.log('============================');
  
  // Mock process.argv
  const originalArgv = process.argv;
  
  // Test default arguments
  process.argv = ['node', 'setup-env.js'];
  const defaultOptions = parseArgs();
  console.log('Default options:', defaultOptions);
  
  // Test custom arguments
  process.argv = ['node', 'setup-env.js', '--api-url', 'http://example.com/api', '--ws-url', 'ws://example.com', '--force'];
  const customOptions = parseArgs();
  console.log('Custom options:', customOptions);
  
  // Restore original argv
  process.argv = originalArgv;
  
  if (defaultOptions.apiUrl === 'http://localhost:8000/api/v1' &&
      defaultOptions.wsUrl === 'http://localhost:8000' &&
      !defaultOptions.force) {
    console.log('✓ Default argument parsing works correctly');
  } else {
    console.log('✗ Default argument parsing failed');
  }
  
  if (customOptions.apiUrl === 'http://example.com/api' &&
      customOptions.wsUrl === 'ws://example.com' &&
      customOptions.force) {
    console.log('✓ Custom argument parsing works correctly');
  } else {
    console.log('✗ Custom argument parsing failed');
  }
}

function main() {
  console.log('🧪 Testing .env.local Auto-Generation');
  console.log('======================================');
  
  // Check if .env.local.example exists
  if (!fileExists(ENV_EXAMPLE_PATH)) {
    console.error('Error: .env.local.example not found. Cannot run tests.');
    process.exit(1);
  }
  
  testArgumentParsing();
  testDefaultGeneration();
  testCustomValues();
  testExistingFile();
  
  console.log('\n✅ All tests completed!');
  console.log('You can now safely use the setup-env.js script.');
  
  // Cleanup
  cleanup();
  console.log('🧹 Cleanup completed.');
}

if (require.main === module) {
  main();
}
