# Student Test Helper

A web application for creating and taking tests organized by discipline. Built with Flask (backend) and vanilla JavaScript (frontend), running in a dev container.

## Features

### Teacher Interface
- Create and manage academic disciplines
- Create tests grouped by discipline
- Add multiple-choice questions with explanations
- Manage existing tests and questions

### Student Interface
- Browse available tests by discipline
- Take tests with multiple-choice questions
- Get instant feedback with scores
- View correct answers and explanations for failed questions

## Getting Started

### Prerequisites
- Docker and Docker Compose (for dev container)
- Python 3.11+ (for local development)

### Running with Dev Container

1. Open the project in VS Code
2. Install the "Dev Containers" extension
3. Click "Reopen in Container" when prompted
4. The application will automatically set up and be ready to use

### Running Locally

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Initialize the database:
```bash
python init_db.py
```

3. Run the application:
```bash
python app.py
```

4. Open your browser to `http://localhost:5000`

## Project Structure

```
student-test-helper/
├── .devcontainer/          # Dev container configuration
│   ├── devcontainer.json
│   ├── docker-compose.yml
│   └── Dockerfile
├── .github/
│   └── workflows/
│       └── ci.yml          # CI/CD pipeline
├── static/                 # Static assets (CSS, JS)
│   ├── style.css
│   ├── teacher.js
│   └── student.js
├── templates/              # HTML templates
│   ├── index.html
│   ├── teacher.html
│   └── student.html
├── tests/                  # Test files
│   └── test_app.py
├── app.py                  # Main Flask application
├── models.py               # Database models
├── init_db.py             # Database initialization
└── requirements.txt        # Python dependencies
```

## API Endpoints

### Disciplines
- `GET /api/disciplines` - List all disciplines
- `POST /api/disciplines` - Create a new discipline
- `GET /api/disciplines/<id>` - Get discipline details
- `DELETE /api/disciplines/<id>` - Delete a discipline

### Tests
- `GET /api/tests` - List all tests
- `POST /api/tests` - Create a new test
- `GET /api/tests/<id>` - Get test details
- `DELETE /api/tests/<id>` - Delete a test
- `GET /api/tests/<id>/take` - Get test for taking (without answers)
- `POST /api/tests/<id>/submit` - Submit test answers

### Questions
- `POST /api/tests/<id>/questions` - Add a question to a test
- `DELETE /api/questions/<id>` - Delete a question

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

## CI/CD

The project includes a GitHub Actions workflow that:
- Runs linting (flake8)
- Initializes the database
- Runs the test suite
- Builds the Docker container
- Tests the container

## License

This project is open source and available under the MIT License.
