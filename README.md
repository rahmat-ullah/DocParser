# Document Parser - Frontend Refactor

## Overview
This project is undergoing a comprehensive frontend refactor to improve code quality, performance, and maintainability. The refactor is being conducted on the `feat/frontend-refactor` branch to allow for parallel development and thorough testing.

## Project Structure
```
DocParser/
├── frontend/                 # Next.js frontend application
│   ├── app/                 # Next.js app router
│   ├── components/          # React components
│   ├── lib/                 # Utility functions and services
│   ├── types/               # TypeScript type definitions
│   ├── __tests__/           # Test files
│   └── ...
├── documentations/          # Project documentation
├── .github/                 # GitHub workflows and configurations
└── TASK_BOARD.md           # Refactor task board
```

## Getting Started

### Prerequisites
- Node.js 18.x or 20.x
- npm or yarn
- Git

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd DocParser

# Switch to the refactor branch
git checkout feat/frontend-refactor

# Install frontend dependencies
cd frontend
npm install

# Start the development server
npm run dev
```

### Development Scripts
```bash
# Development
npm run dev              # Start development server
npm run build           # Build for production
npm run start           # Start production server

# Code Quality
npm run lint            # Run ESLint
npm run lint:fix        # Fix ESLint issues
npm run type-check      # Run TypeScript type checking

# Testing
npm run test            # Run tests
npm run test:watch      # Run tests in watch mode
npm run test:coverage   # Run tests with coverage

# CI/CD
npm run ci:all          # Run all CI checks
```

## CI/CD Pipeline
The project uses GitHub Actions for continuous integration:

- **Type Checking**: Ensures TypeScript code is valid
- **Linting**: Enforces code style and quality standards
- **Testing**: Runs unit tests with coverage reporting
- **Build**: Verifies the application builds successfully
- **Security**: Audits dependencies for vulnerabilities

## Code Quality Standards
- **ESLint**: Enforces consistent code style
- **TypeScript**: Strong typing for better code reliability
- **Jest**: Unit testing framework
- **Pre-commit hooks**: Ensures code quality before commits
- **Code coverage**: Minimum 70% coverage required

## Branch Strategy
- `main`: Production-ready code
- `feat/frontend-refactor`: Active refactor work
- Feature branches: Individual feature development

## Contributing
1. Create a feature branch from `feat/frontend-refactor`
2. Make your changes
3. Ensure all tests pass: `npm run ci:all`
4. Submit a pull request

## Task Board
See [TASK_BOARD.md](./TASK_BOARD.md) for detailed refactor progress and remaining tasks.

## Architecture Decisions
- **Next.js 13**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Radix UI**: Accessible component primitives
- **Jest**: Testing framework
- **ESLint**: Code linting and formatting

## Performance Targets
- **Core Web Vitals**: LCP < 2.5s, FID < 100ms, CLS < 0.1
- **Bundle Size**: < 500KB gzipped
- **Test Coverage**: > 80%
- **Accessibility**: WCAG 2.1 AA compliance

## Security
- Regular dependency audits
- Input validation and sanitization
- Secure authentication patterns
- CSP headers implementation

## Support
For questions or issues related to the refactor, please:
1. Check the [TASK_BOARD.md](./TASK_BOARD.md) for current status
2. Review existing issues on GitHub
3. Create a new issue with detailed description

## License
[Add your license information here]
