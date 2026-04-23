# QA Project

Comprehensive QA automation and testing framework for internal applications.

## Overview

This project provides a complete QA solution including automated testing, continuous integration support, and deployment pipelines for the test-internal-app.

## Project Structure

```
qa/
├── README.md              # This file
├── .env.example           # Environment template
├── docker-compose.yml     # Docker orchestration
├── .dockerignore          # Docker ignore rules
├── src/                   # Source code
│   ├── components/        # Test components
│   ├── utils/             # Helper functions
│   └── config/            # Configuration files
├── tests/                 # Test suites
│   ├── e2e/              # End-to-end tests
│   ├── unit/             # Unit tests
│   └── integration/       # Integration tests
├── docs/                  # Documentation
└── scripts/               # Utility scripts
```

## Prerequisites

- Node.js 18.x or higher
- Docker 20.x or higher
- Docker Compose 2.x or higher

## Installation

### Quick Start (Docker)

```bash
# Clone the repository
git clone <repository-url>

# Copy environment template
cp .env.example .env

# Start with Docker Compose
docker-compose up -d
```

### Manual Setup

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Run initial setup
npm run setup
```

## Environment Configuration

Create a `.env` file in the root directory:

```env
# Docker settings
DOCKER_HOST=localhost
DOCKER_PORT=2375

# Database settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=test_db
DB_USER=test_user
DB_PASSWORD=test_password

# API settings
API_URL=http://localhost:3000
API_KEY=your-api-key-here

# Test settings
TEST_MODE=development
COVERAGE=true
```

## Docker Compose Usage

### Start All Services

```bash
docker-compose up -d
```

### Start Specific Services

```bash
# Only database
docker-compose up -d db

# Only application
docker-compose up -d app

# All services with logs
docker-compose up
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop with data volume preservation
docker-compose down -v
```

### View Logs

```bash
# All logs
docker-compose logs -f

# Specific service logs
docker-compose logs -f app
docker-compose logs -f db
```

### Exec into Containers

```bash
# Enter app container
docker-compose exec app bash

# Run npm commands in app
docker-compose exec app npm test
```

## Available Scripts

| Command | Description |
|---------|-------------|
| `npm install` | Install dependencies |
| `npm test` | Run tests with coverage |
| `npm run lint` | Lint source code |
| `npm run dev` | Run development server |
| `npm run build` | Run lint and tests |
| `npm run setup` | Initial project setup |

## Development Workflow

1. Clone the repository
2. Copy `.env.example` to `.env`
3. Configure environment variables
4. Run `npm install` to install dependencies
5. Start development server with `npm run dev`

## Testing

### Run All Tests

```bash
npm test
```

### Run with Coverage

```bash
npm run test:coverage
```

### Run Specific Test Suite

```bash
npm run test:e2e
npm run test:unit
npm run test:integration
```

## Troubleshooting

### Docker Issues

```bash
# Check container status
docker-compose ps

# View logs for specific service
docker-compose logs -f <service-name>

# Restart service
docker-compose restart <service-name>

# Rebuild and restart
docker-compose up --build -d
```

### Node Issues

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## Contributing

1. Create a feature branch
2. Make changes
3. Run tests
4. Submit a pull request

## License

MIT License

## Support

For issues and questions, contact the QA team.
