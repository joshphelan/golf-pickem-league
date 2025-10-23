# Golf Pickem League - Frontend

Next.js 14 frontend application for the Golf Pickem League fantasy golf platform.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Date Utilities**: date-fns

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Create `.env.local` file:
```
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

3. Run development server:
```bash
npm run dev
```

4. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
frontend/
├── app/                      # Next.js App Router pages
│   ├── page.tsx             # Landing page
│   ├── layout.tsx           # Root layout
│   ├── login/               # Login page
│   ├── signup/              # Signup page
│   ├── dashboard/           # User dashboard
│   ├── admin/
│   │   └── import/          # Admin tournament import
│   ├── leagues/
│   │   ├── create/          # Create league
│   │   ├── join/[code]/     # Join league via invite code
│   │   └── [id]/            # League details & standings
│   └── teams/
│       └── [id]/            # Team details & player draft
├── components/              # Reusable components
│   ├── Navbar.tsx
│   ├── LoadingSpinner.tsx
│   ├── ErrorMessage.tsx
│   └── ProtectedRoute.tsx
├── lib/                     # Utilities and API client
│   ├── api.ts              # Axios client & API methods
│   └── auth.ts             # Auth helpers
└── public/                  # Static assets
```

## Features

### Authentication
- **Signup**: Create account (requires admin approval)
- **Login**: JWT-based authentication
- **Protected Routes**: Automatic redirect to login for unauthenticated users

### User Dashboard
- View all tournaments
- See your leagues
- Create new league
- Join league via invite code
- Admin: Import tournaments

### League Management
- **Create League**: Select tournament, set draft deadline and team size
- **Join League**: Use 8-character invite code
- **View League**: See standings, member teams, and league details
- **Sync Scores**: Owner can manually sync tournament scores

### Team Management
- **Draft Players**: Search and draft available PGA Tour players
- **View Team**: See drafted players with round-by-round scores
- **Total Score**: Automatically calculated from player scores
- **Undraft**: Remove players before draft deadline

### Admin Features
- Import tournaments from Golf API
- Accessible via `/admin/import` route

## API Integration

The frontend communicates with the FastAPI backend at `http://localhost:8000/api`.

### Authentication
- JWT tokens stored in localStorage
- Auto-attached to all API requests via Axios interceptor
- Auto-logout on 401 responses

### Key Endpoints Used
- `POST /auth/signup` - Create account
- `POST /auth/login` - Login
- `GET /auth/me` - Get current user
- `GET /tournaments` - List tournaments
- `POST /tournaments/import` - Import tournament (admin)
- `POST /tournaments/{id}/sync-scores` - Sync scores (league owner)
- `POST /leagues` - Create league
- `GET /leagues/{id}` - Get league details
- `GET /leagues/{id}/standings` - Get league standings
- `POST /leagues/join/{code}` - Join league
- `GET /teams/{id}` - Get team details
- `POST /teams/{id}/draft` - Draft player
- `DELETE /teams/{id}/undraft/{player_id}` - Remove player
- `GET /tournaments/{id}/available-players` - Get available players for league

## Development

### Run Development Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
```

### Start Production Server
```bash
npm start
```

### Linting
```bash
npm run lint
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL | `http://localhost:8000/api` |

## User Flow

1. **New User**:
   - Sign up → Wait for admin approval → Login → Dashboard

2. **Create League**:
   - Dashboard → Create League → Select tournament → Set details → Get invite code

3. **Join League**:
   - Dashboard → Join League → Enter invite code → View league

4. **Draft Team**:
   - League page → Click team → Draft Player → Search → Select players

5. **View Standings**:
   - League page → See rankings updated after score sync

## Styling

Uses Tailwind CSS with utility classes. Color scheme:
- **Primary**: Blue (blue-600)
- **Success**: Green (green-600)
- **Warning**: Purple (purple-600)
- **Danger**: Red (red-600)

## Known Limitations

- Draft modal needs tournament_id fix for available players
- No real-time updates (manual page refresh required)
- No toast notification system (using browser alerts)
- Mobile UI could be further optimized

## Future Enhancements

- Add polling for automatic score updates
- Implement toast notifications
- Add user profile page
- League chat/comments
- Historical league results
- Player statistics and trends
- Mobile app version
