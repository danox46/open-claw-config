# Employee Management System

A RESTful API for managing employee records with full CRUD (Create, Read, Update, Delete) operations.

## 📋 Project Description

This project provides a comprehensive API for managing employee data within an organization. It enables team administrators to perform essential operations such as creating new employee profiles, retrieving employee information, updating employee details, and removing records from the system.

### Key Features

- **Employee Registration**: Create new employee profiles with personal and professional information
- **Employee Lookup**: Retrieve employee data by ID or search by name/email
- **Profile Updates**: Modify employee information including contact details, role, and status
- **Record Management**: Archive or remove employee records as needed
- **Data Validation**: Built-in validation to ensure data integrity

## 🚀 Setup Instructions

### Prerequisites

- Node.js (v18 or higher)
- npm or yarn
- PostgreSQL (v14 or higher)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd employee-management-system
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

4. **Set up the database**
   ```bash
   npm run db:migrate
   ```

5. **Start the development server**
   ```bash
   npm run dev
   ```

### Build for Production

```bash
npm run build
npm start
```

## 🔌 API Endpoints

### Base URL
```
http://localhost:3000/api/employees
```

### Authentication
Most endpoints require an authentication token in the `Authorization` header:
```
Authorization: Bearer <your-token>
```

### Employee Operations

#### 1. Create Employee
```http
POST /api/employees
Content-Type: application/json
Authorization: Bearer <token>

{
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@company.com",
  "phone": "+1-555-123-4567",
  "department": "Engineering",
  "position": "Software Developer",
  "startDate": "2024-01-15"
}
```

**Response:**
```json
{
  "id": "emp_12345",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@company.com",
  "department": "Engineering",
  "createdAt": "2024-01-15T10:30:00Z"
}
```

#### 2. Get All Employees
```http
GET /api/employees
Authorization: Bearer <token>
```

**Query Parameters:**
- `?page=1&limit=20` - Pagination
- `?department=Engineering` - Filter by department
- `?search=john` - Search by name/email

**Response:**
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "totalPages": 8
  }
}
```

#### 3. Get Single Employee
```http
GET /api/employees/:id
Authorization: Bearer <token>
```

**Response:**
```json
{
  "id": "emp_12345",
  "firstName": "John",
  "lastName": "Doe",
  "email": "john.doe@company.com",
  "phone": "+1-555-123-4567",
  "department": "Engineering",
  "position": "Software Developer",
  "role": "Full Stack Developer",
  "startDate": "2024-01-15",
  "status": "active",
  "profileImage": "https://...",
  "emergencyContact": {
    "name": "Jane Doe",
    "phone": "+1-555-987-6543",
    "relation": "Spouse"
  }
}
```

#### 4. Update Employee
```http
PUT /api/employees/:id
Content-Type: application/json
Authorization: Bearer <token>

{
  "email": "new.email@company.com",
  "phone": "+1-555-999-8888",
  "position": "Senior Software Developer",
  "status": "active"
}
```

**Response:**
```json
{
  "id": "emp_12345",
  "firstName": "John",
  "lastName": "Doe",
  "email": "new.email@company.com",
  "phone": "+1-555-999-8888",
  "position": "Senior Software Developer",
  "updatedAt": "2024-01-16T14:20:00Z"
}
```

#### 5. Delete Employee
```http
DELETE /api/employees/:id
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Employee emp_12345 has been archived successfully",
  "id": "emp_12345"
}
```

#### 6. Archive Employee (Soft Delete)
```http
POST /api/employees/:id/archive
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Employee emp_12345 has been archived",
  "id": "emp_12345",
  "archivedAt": "2024-01-16T15:00:00Z"
}
```

#### 7. Reactivate Employee
```http
POST /api/employees/:id/reactivate
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Employee emp_12345 has been reactivated",
  "id": "emp_12345"
}
```

## 🧪 Testing

### Run All Tests
```bash
npm test
```

### Test with API Documentation
```bash
npm run test:api
```

## 📁 Project Structure

```
employee-management-system/
├── src/
│   ├── api/
│   │   └── index.js
│   ├── models/
│   │   └── Employee.js
│   ├── routes/
│   │   └── employees.js
│   └── middleware/
├── tests/
│   └── employees.spec.js
├── config/
│   └── default
├── .env.example
├── package.json
├── README.md
└── docker-compose.yml
```

## 🔒 Security

- JWT-based authentication for all operations
- Input validation using Joi
- Rate limiting to prevent abuse
- SQL injection protection via parameterized queries
- CORS configuration for frontend integration

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details.

## 👥 Support

For issues, questions, or contributions:
- **GitHub Issues**: https://github.com/your-org/employee-management-system/issues
- **Email**: support@yourcompany.com
- **Slack**: #employee-api channel

## 📞 Team Contact

- **API Owner**: api@yourcompany.com
- **Documentation**: docs@yourcompany.com
- **Emergency**: on-call@yourcompany.com

---

**Version**: 1.0.0  
**Last Updated**: January 2024  
**Maintained by**: Your Organization Team
