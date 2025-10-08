# Golf Fantasy League - Backend

FastAPI backend for the Golf Fantasy League application.

## Setup

### 1. Create Virtual Environment

```bash
cd backend
python -m venv venv

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the **project root** (not in backend folder):

```env
# Golf API
GOLF_API_KEY=your_actual_api_key_here
GOLF_API_BASE_URL=https://api.freewebapi.com

# Database
DATABASE_URL=postgresql://golf_user:golf_password@localhost:5432/golf_league_db
POSTGRES_USER=golf_user
POSTGRES_PASSWORD=golf_password
POSTGRES_DB=golf_league_db

# JWT Secret (generate with command below)
SECRET_KEY=your_generated_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# Frontend URL
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 4. Start Database

```bash
# From project root
docker-compose up -d postgres
```

### 5. Run Migrations

```bash
# Make sure you're in backend/ directory with venv activated
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 6. Start Development Server

```bash
uvicorn app.main:app --reload
```

API will be available at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Database Models

- **User**: User accounts with approval workflow
- **Tournament**: PGA Tour tournaments
- **Player**: PGA Tour golfers
- **PlayerScore**: Tournament scores by round
- **League**: Fantasy leagues
- **Team**: User teams in leagues
- **TeamPlayer**: Player selections for teams

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `GET /api/auth/admin/users` - List all users (admin)
- `PATCH /api/auth/admin/users/{id}` - Approve/modify users (admin)

More endpoints will be added in subsequent phases.

## Testing

```bash
# Test the API
curl http://localhost:8000/health

# View interactive docs
open http://localhost:8000/docs
```

## First Admin User

After running migrations and signing up, manually set yourself as admin:

```sql
-- Connect to database
psql -U golf_user -d golf_league_db

-- Set first user as admin
UPDATE users SET is_approved = TRUE, is_admin = TRUE WHERE email = 'your@email.com';
```

## Project Structure

```
backend/
β"œβ"€β"€ app/
β"‚   β"œβ"€β"€ main.py              # FastAPI app
β"‚   β"œβ"€β"€ config.py            # Settings
β"‚   β"œβ"€β"€ database.py          # DB connection
β"‚   β"œβ"€β"€ models/              # SQLAlchemy models
β"‚   β"œβ"€β"€ routes/              # API endpoints
β"‚   β"œβ"€β"€ schemas/             # Pydantic models
β"‚   β"œβ"€β"€ services/            # Business logic
β"‚   └── utils/               # Helpers
β"œβ"€β"€ alembic/                 # Migrations
β"œβ"€β"€ requirements.txt
└── Dockerfile
```

