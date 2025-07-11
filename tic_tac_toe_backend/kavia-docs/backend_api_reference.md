# Tic Tac Toe Backend API Reference

This document provides comprehensive reference for all REST API endpoints implemented in the Tic Tac Toe backend, including user authentication, game management, and leaderboard access. Endpoints are described in terms of their URL, method, purpose, authentication/session requirements, request/response schemas, and coding examples.

---

## Authentication & User Management

Endpoints under `/auth` handle signup, login, logout, and session inspection.

### 1. Signup

**POST** `/auth/signup`  
- Registers a new user account.
- **Request Body:**  
  ```json
  {
      "username": "string",
      "email": "user@example.com",
      "password": "string"
  }
  ```
- **Response:**  
  User info (JSON):
  ```json
  {
      "id": 1,
      "username": "string",
      "email": "user@example.com",
      "created_at": "2024-07-02T15:04:05.000Z"
  }
  ```

- **Errors:**  
  - 400 if username or email is already registered

#### Example (curl):
```bash
curl -X POST http://localhost:8000/auth/signup -H "Content-Type: application/json" \
  -d '{"username":"alice","email":"alice@example.com","password":"secret"}'
```

---

### 2. Login

**POST** `/auth/login`  
- Logs in the user with username and password.  
- Sets an HTTP-only `user_id` cookie for session authentication.
- **Request Body:**
  ```json
  {
      "username": "string",
      "password": "string"
  }
  ```
- **Response:**  
  User info (same as above)

- **Errors:**  
  - 401 if credentials are invalid

#### Example (curl):
```bash
curl -X POST http://localhost:8000/auth/login -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret"}' -c cookies.txt
```
(The `-c cookies.txt` saves cookies for subsequent authenticated requests.)

---

### 3. Logout

**POST** `/auth/logout`  
- Logs the user out by deleting the session cookie.
- **Authentication:** Session cookie required.
- **Response:**
  ```json
  {"message": "Logged out."}
  ```

#### Example (curl):
```bash
curl -X POST http://localhost:8000/auth/logout -b cookies.txt
```

---

### 4. Session Inspection

**GET** `/auth/session`  
- Checks if a user is logged in; returns current user info if so.
- **Authentication:** Session cookie required.
- **Response:**  
  User info (see above)
- **Errors:**  
  - 401 if session is missing or invalid

---

## Game Management

Endpoints under `/games` manage Tic Tac Toe matches. **All game endpoints require authentication via the session cookie.**

### 1. Create Game

**POST** `/games/create`  
- Starts a new game as the calling user (who becomes player 1).
- **Request Body:**  
  `{}` (no input required)
- **Response:**  
  Full game state:
  ```json
  {
    "id": 123,
    "created_at": "...",
    "status": "waiting",
    "turn": 1,
    "current_player_id": null,
    "winner_id": null,
    "board_state": "_________",
    "players": [
      {"id":1,"username":"alice","email":"alice@example.com","created_at":"..."}
    ],
    "moves": []
  }
  ```

---

### 2. Join Game

**POST** `/games/join`  
- Join a waiting game as player 2.
- **Request Body:**  
  ```json
  {"game_id": 123}
  ```
- **Response:**  
  Same as above, with both players included.

---

### 3. Leave Game

**POST** `/games/leave`  
- Remove self from a given game.
- **Request Body:**
  ```json
  {"game_id": 123}
  ```
- **Response:**
  ```json
  {"left": true}
  ```

---

### 4. Make a Move

**POST** `/games/play`  
- Make a move in an ongoing game (must be user's turn).
- **Request Body:**
  ```json
  {
    "game_id": 123,
    "position": 5
  }
  ```
  - `position` is an integer 0 through 8 (row-major, top-left=0 to bottom-right=8).

- **Response:**  
  Updated game state (see "Create Game" above).

- **Errors:**  
  - 404 if game not found  
  - 403 if not a player  
  - 400 if not user's turn or invalid move

---

### 5. Get Game State

**GET** `/games/{game_id}`  
- Retrieves the state of a specific game (does not require session cookie, but only players see updates in real time).
- **Response:**  
  Full game state

---

## Leaderboard

Endpoints under `/leaderboard`:

### Get Leaderboard

**GET** `/leaderboard/`

- Lists top players ordered by number of wins.
- **Response:**
  ```json
  {
    "leaderboard": [
      {"username": "alice", "wins": 3, "losses": 1, "draws": 2},
      {"username": "bob", "wins": 2, "losses": 3, "draws": 1}
    ]
  }
  ```

---

## Authentication and Session Details

All endpoints except `/auth/signup` and `/auth/login` require the session cookie `user_id` for authentication. This cookie is set upon login and should be included in all subsequent protected requests.

To use cookies with curl, use the `-b` and `-c` arguments.

---

## Data Schemas

Referenced in responses and requests (abridged):

- **UserRead**
  ```json
  {
    "id": 1,
    "username": "string",
    "email": "string",
    "created_at": "2024-07-02T15:04:05.000Z"
  }
  ```
- **GameRead**
  ```json
  {
    "id": 123,
    "created_at": "...",
    "status": "waiting",
    "turn": 1,
    "current_player_id": 1,
    "winner_id": null,
    "board_state": "_________",
    "players": [UserRead, UserRead],
    "moves": [
      {"user_id": 1, "position": 4, "symbol": "X", "created_at": "..."}
    ]
  }
  ```
- **LeaderboardEntry**
  ```json
  {
    "username": "string",
    "wins": 1,
    "losses": 2,
    "draws": 0
  }
  ```

---

## OpenAPI JSON

A machine-readable OpenAPI 3.1 schema is available at  
`tic_tac_toe_backend/interfaces/openapi.json`.

---

## Example Flow

1. `POST /auth/signup` – Create user
2. `POST /auth/login` – Log in (save cookies)
3. `POST /games/create` – Start game (use `-b cookies.txt`)
4. `POST /games/join` – Join existing game
5. `POST /games/play` – Submit moves
6. `GET /leaderboard/` – See leaderboard

---

## Security Notes

- Passwords are hashed before storage, but demo implementation (SHA-256) is for development only.
- Session authentication is via cookie, not a JWT.
- All protected endpoints return 401/403 for invalid or missing session.

---

## API Structure Diagram

```mermaid
flowchart TD
    A[Client] -->|signup/login| B["/auth/*"]
    B -->|login cookie| A
    A -->|create/join/leave/play|get| C["/games/*"]
    A -->|GET| D["/leaderboard/"]
    C -->|returns| A
    D -->|returns| A
    subgraph tic_tac_toe_backend
      B
      C
      D
    end
```

---
Task completed: This API reference comprehensively documents all implemented REST endpoints, schemas, authentication, and usage for backend tic_tac_toe_backend as of the latest code and OpenAPI spec.
