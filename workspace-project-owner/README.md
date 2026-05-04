# Employee CRUD Application

Internal application for managing employee data with search, pagination, create, edit, and delete functionality.

## Tech Stack

- **Frontend**: React 18
- **Backend**: Node.js + Express
- **Database**: MongoDB
- **Containerization**: Docker

## Quick Start

### Prerequisites

- Docker and Docker Compose installed

### Run Locally

```bash
docker-compose up --build
```

This will start:
- Frontend on http://localhost:3000
- Backend API on http://localhost:5000
- MongoDB on localhost:27017

### Environment Variables

Copy `.env.example` to `.env` and configure as needed:

```bash
cp .env.example .env
```

| Variable | Description | Default |
|----------|-------------|---------|
| MONGODB_URI | MongoDB connection string | mongodb://localhost:27017/employee_crud |
| PORT | Backend port | 5000 |
| NODE_ENV | Environment mode | development |
| REACT_APP_API_URL | Frontend API endpoint | http://localhost:5000/api |

## Project Structure

```
.
├── backend/          # Express API server
│   ├── Dockerfile    # Backend Docker configuration
│   └── package.json  # Backend dependencies
├── frontend/         # React application
│   ├── Dockerfile    # Frontend Docker configuration
│   ├── package.json  # Frontend dependencies
│   └── nginx.conf    # Nginx configuration for serving
├── docker-compose.yml # Docker Compose configuration
├── .env.example      # Environment variables template
└── README.md         # This file
```

## Development

### Backend

```bash
cd backend
npm install
npm run dev    # Development with nodemon
npm start      # Production
```

### Frontend

```bash
cd frontend
npm install
npm start      # Development
npm run build  # Production build
```

## API Endpoints

- `GET /api/employees` - List all employees (with pagination and search)
- `GET /api/employees/:id` - Get single employee
- `POST /api/employees` - Create new employee
- `PUT /api/employees/:id` - Update employee
- `DELETE /api/employees/:id` - Delete employee
