# Frontend Environment Setup

This document describes the automatic `.env.local` generation system for the frontend application.

## Overview

The frontend application uses environment variables to configure API endpoints and WebSocket connections. To streamline development setup, an automatic `.env.local` generation system has been implemented.

## How It Works

### Auto-Generation Logic

1. **Check for Existing File**: The system first checks if `frontend/.env.local` exists
2. **Template Duplication**: If absent, it duplicates `.env.local.example` to `.env.local`
3. **Default Values**: Sets default values pointing to `localhost:8000`
4. **Flag Overrides**: Allows customization via command-line flags

### Default Configuration

When no flags are provided, the generated `.env.local` will contain:

```env
# Frontend Environment Configuration Template
# Copy this file to .env.local and update the values as needed

# API Configuration
# Base URL for the backend API endpoints
# Used by the frontend to make HTTP requests to the backend
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1

# WebSocket Configuration  
# WebSocket URL for real-time communication with the backend
# Used for live updates and real-time features
NEXT_PUBLIC_WS_URL=http://localhost:8000
```

## Usage

### Automatic Setup

The environment setup runs automatically when you start the development server:

```bash
npm run dev
```

This is configured through the `predev` script in `package.json`.

### Manual Setup

You can also run the setup manually:

```bash
# Use default values (localhost:8000)
npm run setup-env

# Or run the script directly
node setup-env.js
```

### Custom Configuration

Override default values using command-line flags:

```bash
# Custom API URL
node setup-env.js --api-url http://localhost:3001/api/v1

# Custom WebSocket URL
node setup-env.js --ws-url ws://localhost:3001

# Both custom URLs
node setup-env.js --api-url http://api.example.com/v1 --ws-url ws://api.example.com

# Force regeneration even if .env.local exists
node setup-env.js --force

# Different backend port
node setup-env.js --api-url http://localhost:9000/api/v1 --ws-url http://localhost:9000
```

### Available Options

| Flag | Description | Default |
|------|-------------|---------|
| `--api-url <url>` | Override the API base URL | `http://localhost:8000/api/v1` |
| `--ws-url <url>` | Override the WebSocket URL | `http://localhost:8000` |
| `--force` | Force regeneration even if `.env.local` exists | `false` |
| `--help` | Show help message | - |

## Development Workflow

### First-Time Setup

1. Clone the repository
2. Navigate to the frontend directory
3. Run `npm install`
4. Run `npm run dev` (automatically generates `.env.local` if needed)

### Changing Backend Configuration

If you need to point to a different backend:

```bash
# Update to point to staging environment
node setup-env.js --api-url https://api-staging.example.com/v1 --ws-url wss://api-staging.example.com --force

# Update to point to different local port
node setup-env.js --api-url http://localhost:9000/api/v1 --ws-url http://localhost:9000 --force
```

### Team Development

Different team members can use different backend configurations without affecting each other:

```bash
# Developer A: Uses default localhost:8000
npm run dev

# Developer B: Uses custom local setup
node setup-env.js --api-url http://localhost:3001/api/v1 --ws-url ws://localhost:3001 --force
npm run dev

# Developer C: Uses remote staging
node setup-env.js --api-url https://api-staging.example.com/v1 --ws-url wss://api-staging.example.com --force
npm run dev
```

## File Structure

```
frontend/
├── .env.local.example    # Template file with default values
├── .env.local           # Generated file (git-ignored)
├── setup-env.js         # Environment setup script
├── test-setup-env.js    # Test script for the setup functionality
└── package.json         # Contains setup-env and predev scripts
```

## Testing

Run the test suite to verify the environment setup functionality:

```bash
node test-setup-env.js
```

This will test:
- Default value generation
- Custom value override
- Existing file handling
- Argument parsing

## Troubleshooting

### Common Issues

1. **Permission Errors**: Ensure the script has write permissions to the frontend directory
2. **Missing Template**: Verify that `.env.local.example` exists in the frontend directory
3. **Invalid URLs**: Ensure provided URLs are valid and accessible

### Manual Override

If automatic generation fails, you can manually create `.env.local`:

```bash
cp .env.local.example .env.local
# Then edit .env.local with your preferred values
```

## Integration with CI/CD

For continuous integration, you may want to skip the automatic generation:

```bash
# Skip predev script in CI
npm run dev --ignore-scripts

# Or set environment variables directly in CI
export NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
export NEXT_PUBLIC_WS_URL=http://localhost:8000
npm run dev
```

## Security Considerations

- The `.env.local` file is git-ignored to prevent accidental commits
- Only `NEXT_PUBLIC_*` variables are used, which are safe for client-side use
- The setup script only reads from `.env.local.example` and writes to `.env.local`
- No sensitive information should be stored in the template file
