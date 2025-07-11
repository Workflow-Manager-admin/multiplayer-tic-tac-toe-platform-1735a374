import requests
import random
import time

BASE_URL = "http://localhost:8000"

SESS_FILE_USER1 = "cookies_user1.txt"
SESS_FILE_USER2 = "cookies_user2.txt"

def clear_cookies(file):
    with open(file, "w") as f:
        f.write("")

def signup_and_login(username, email, password, sess_file):
    # Signup
    r = requests.post(f"{BASE_URL}/auth/signup", json={
        "username": username,
        "email": email,
        "password": password
    })
    if r.status_code not in (200, 400):  # 400 means already registered, skip
        print(f"Signup ({username}):", r.status_code, r.text)

    # Login
    r = requests.post(f"{BASE_URL}/auth/login", json={"username": username, "password": password}, allow_redirects=False)
    if r.status_code != 200:
        print(f"Login ({username}):", r.status_code, r.text)
        return None, None

    # Get cookies (user_id session mainly used)
    session_cookies = r.cookies
    # Optionally write for curl etc.
    with open(sess_file, "w") as f:
        for k in session_cookies.keys():
            f.write(f"{k}={session_cookies[k]};")
    user = r.json()
    return user, session_cookies

def create_game(session_cookies):
    r = requests.post(f"{BASE_URL}/games/create", cookies=session_cookies, json={})
    assert r.status_code == 200, f"Create game failed: {r.text}"
    return r.json()

def join_game(session_cookies, game_id):
    r = requests.post(f"{BASE_URL}/games/join", cookies=session_cookies, json={"game_id": game_id})
    assert r.status_code == 200, f"Join game failed: {r.text}"
    return r.json()

def play_move(session_cookies, game_id, position):
    r = requests.post(f"{BASE_URL}/games/play", cookies=session_cookies, json={"game_id": game_id, "position": position})
    if r.status_code != 200:
        print("Error making move:", r.status_code, r.text)
        return None
    return r.json()

def fetch_game(game_id):
    r = requests.get(f"{BASE_URL}/games/{game_id}")
    assert r.status_code == 200, f"Fetch game failed for {game_id}: {r.text}"
    return r.json()

def fetch_leaderboard():
    r = requests.get(f"{BASE_URL}/leaderboard/")
    assert r.status_code == 200, f"Fetch leaderboard failed: {r.text}"
    return r.json()

def run_e2e():
    clear_cookies(SESS_FILE_USER1)
    clear_cookies(SESS_FILE_USER2)
    un1 = f"alice_{random.randint(10,9999)}"
    un2 = f"bob_{random.randint(10,9999)}"
    user1, c1 = signup_and_login(un1, f"{un1}@test.com", "secret", SESS_FILE_USER1)
    user2, c2 = signup_and_login(un2, f"{un2}@test.com", "secret", SESS_FILE_USER2)
    print("Registered/logged in:", user1 and user1.get("username"), user2 and user2.get("username"))

    # User 1 creates game
    g = create_game(c1)
    print("Game created by user1:", g["id"])
    gid = g["id"]

    # User 2 joins
    g2 = join_game(c2, gid)
    print("User2 joined game. Players:", [p["username"] for p in g2["players"]])

    # Play round-robin until game ends (draw or winner)
    board = list(g2["board_state"])
    player_ids = [p["id"] for p in g2["players"]]
    u1_turn = True
    current_game = g2
    positions_played = set()
    print("Initial board:", ''.join(board))
    for turn in range(9):
        user = user1 if u1_turn else user2
        cookies = c1 if u1_turn else c2
        board = list(current_game["board_state"])
        avail = [i for i, x in enumerate(board) if x == "_"]
        if not avail:
            print("Board full!")
            break
        move_pos = random.choice(avail)
        print(f"{user['username']} plays at {move_pos}…", end="")
        result = play_move(cookies, gid, move_pos)
        if not result:
            print("Move failed. Game may be finished.")
            break
        current_game = result
        print("done. Board:", result["board_state"])
        if result.get("winner_id"):
            winner_name = [p["username"] for p in result["players"] if p["id"] == result["winner_id"]][0]
            print(f"Winner detected: {winner_name}")
            break
        elif "_" not in result["board_state"]:
            print("Draw detected!")
            break
        u1_turn = not u1_turn
        time.sleep(0.05)

    # View leaderboard
    lb = fetch_leaderboard()
    print("Leaderboard snapshot:", lb)
    assert "leaderboard" in lb
    # View match in history (from game endpoint)
    gstat = fetch_game(gid)
    assert gstat["id"] == gid
    print("Match verified in backend. Final board:", gstat["board_state"], "Status:", gstat["status"])

if __name__ == "__main__":
    run_e2e()
    print("E2E integration test completed.")

