# Multiplayer Tic Tac Toe Platform Backend

This backend powers the multiplayer Tic Tac Toe experience. It manages user registration, authentication, persistent game logic, and leaderboard tracking using FastAPI and a SQLite database.

---

## Features

- **User Management**: Signup, login, logout, and session validation.
- **Secure Game Actions**: Only authenticated users can create or join games.
- **Multiple Matches**: Supports concurrent games, game state persistence, and player move tracking.
- **Leaderboard**: Tracks player performance (wins, draws, losses) across sessions.
- **RESTful API**: All features are accessible over documented endpoints.
- **OpenAPI Spec**: Full auto-generated OpenAPI (Swagger) JSON at `tic_tac_toe_backend/interfaces/openapi.json`.

---

## Setup & Installation

### Prerequisites

- Python 3.8+
- [pip](https://pip.pypa.io/en/stable/)
- (Optional) [virtualenv](https://virtualenv.pypa.io/) for isolated environments

### Install Steps

1. Clone the repo and enter the backend workspace:
    ```bash
    cd multiplayer-tic-tac-toe-platform-1735a374/tic_tac_toe_backend
    ```

2. (Recommended) Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run database migration/initialization (auto on API start).

### Running the API Server

- Start the dev API (default port 8000):
    ```bash
    uvicorn src.api.main:app --reload
    ```

- Visit [http://localhost:8000/docs](http://localhost:8000/docs) for interactive Swagger UI.

---

## Usage

- Use HTTP requests (from the frontend, curl, or Postman) to create users, start/join games, play turns, or query the leaderboard.
- You must login (`/auth/login`) before using game or leaderboard endpoints.

**Example flow:**
1. Signup (`POST /auth/signup`)
2. Login and obtain session cookie (`POST /auth/login`)
3. Create or join a game (`POST /games/create`, `POST /games/join`)
4. Make moves (`POST /games/play`)
5. View leaderboard (`GET /leaderboard/`)
6. Fetch game state (`GET /games/{game_id}`)

---

## API Reference

- See [`tic_tac_toe_backend/kavia-docs/backend_api_reference.md`](tic_tac_toe_backend/kavia-docs/backend_api_reference.md) for a comprehensive listing of endpoints, methods, data schemas, security, and sample requests.
- OpenAPI JSON schema: [`tic_tac_toe_backend/interfaces/openapi.json`](tic_tac_toe_backend/interfaces/openapi.json)

---

## Developer & Testing Notes

- All main endpoints are in `src/api/` (`auth_router.py`, `game_router.py`, `leaderboard_router.py`).
- End-to-End integration test: see `e2e_backend_integration_test.py` for simulating sign-up, login, game actions, and leaderboard verification.
- Game state and user sessions persist via SQLite (`tic_tac_toe.sqlite3`). To reset, simply delete the `.sqlite3` file and restart the API.
- Code uses FastAPI best practices for modularity and dependency injection.

### Running Tests

- (Dev) You can run the e2e integration test:
    ```bash
    python e2e_backend_integration_test.py
    ```
  This test will exercise a full game flow with signup, login, game creation, play, and leaderboard checks.

---

## Known Issues / Limitations

- Passwords are hashed but demo-only (SHA-256, not best for production—use `bcrypt` or `passlib` in a real app).
- No email verification, password reset, or rate limiting is implemented.
- Only supports two concurrent players per game.
- No JWT. Session is via HTTP-only cookie.
- Designed for demo/small team use; SQLite not recommended for heavy concurrent production loads.

---

## Contributing

- PRs and issues are welcome! See `src/api/` for logic and schema details.

---