import os
import tempfile
import uuid
from pathlib import Path

import pytest

TEST_DATABASE_PATH = Path(tempfile.gettempdir()) / f"todoapp-test-{uuid.uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE_PATH.as_posix()}"
os.environ.setdefault("SECRET_KEY", uuid.uuid4().hex)
os.environ["AUTH_COOKIE_SECURE"] = "false"
os.environ["CORS_ORIGINS"] = "http://localhost:5173"

from fastapi.testclient import TestClient

from TodoApp.main import app
from TodoApp.database import Base, engine


Base.metadata.create_all(bind=engine)
client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_auth_cookie():
    client.cookies.clear()
    yield
    client.cookies.clear()


def teardown_module():
    engine.dispose()
    TEST_DATABASE_PATH.unlink(missing_ok=True)


def unique_username(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def test_register_and_login_user():
    payload = {"username": unique_username("alice"), "password": "secret123"}

    register_response = client.post("/register", json=payload)
    assert register_response.status_code == 201, register_response.text
    register_data = register_response.json()
    assert register_data["username"] == payload["username"]
    assert "access_token" not in register_data

    login_response = client.post("/login", json=payload)
    assert login_response.status_code == 200, login_response.text
    assert login_response.json()["username"] == payload["username"]
    assert "access_token" not in login_response.json()
    set_cookie = login_response.headers["set-cookie"].lower()
    assert "httponly" in set_cookie
    assert "samesite=lax" in set_cookie
    assert client.get("/me").json()["username"] == payload["username"]

    logout_response = client.post("/logout", headers={"Origin": "http://localhost:5173"})
    assert logout_response.status_code == 200
    assert client.get("/me").status_code == 401


def test_user_can_create_todo_after_login():
    username = unique_username("bob")
    client.post("/register", json={"username": username, "password": "secret123"})
    client.post("/login", json={"username": username, "password": "secret123"})
    headers = {"Origin": "http://localhost:5173"}

    response = client.post("/todo", json={"task": "Study auth"}, headers=headers)
    assert response.status_code == 201, response.text
    assert response.json()["task"] == "Study auth"


def test_unauthenticated_user_cannot_access_todos_and_users_cannot_access_each_others_todos():
    user_one = unique_username("alice")
    user_two = unique_username("bob")

    client.post("/register", json={"username": user_one, "password": "secret123"})
    client.post("/register", json={"username": user_two, "password": "secret123"})

    origin = {"Origin": "http://localhost:5173"}
    user_one_login = client.post(
        "/login", json={"username": user_one, "password": "secret123"}, headers=origin
    )
    user_one_token = user_one_login.cookies.get("todo_access_token")
    user_two_login = client.post(
        "/login", json={"username": user_two, "password": "secret123"}, headers=origin
    )
    user_two_token = user_two_login.cookies.get("todo_access_token")

    client.cookies.clear()
    assert client.get("/").status_code == 401

    create_response = client.post(
        "/todo",
        json={"task": "User one todo"},
        headers={"Authorization": f"Bearer {user_one_token}", "Origin": "http://localhost:5173"},
    )
    assert create_response.status_code == 201, create_response.text
    todo_id = create_response.json()["id"]

    user_two_list_response = client.get("/", headers={"Authorization": f"Bearer {user_two_token}"})
    assert user_two_list_response.status_code == 200
    assert user_two_list_response.json() == []

    user_two_get_response = client.get(f"/todo/{todo_id}", headers={"Authorization": f"Bearer {user_two_token}"})
    assert user_two_get_response.status_code == 404

    user_two_update_response = client.put(
        f"/todo/{todo_id}",
        json={"task": "Hacked task", "completed": True},
        headers={"Authorization": f"Bearer {user_two_token}", "Origin": "http://localhost:5173"},
    )
    assert user_two_update_response.status_code == 404

    user_two_delete_response = client.delete(
        f"/todo/{todo_id}",
        headers={"Authorization": f"Bearer {user_two_token}", "Origin": "http://localhost:5173"},
    )
    assert user_two_delete_response.status_code == 404


def test_user_can_create_and_update_own_note():
    username = unique_username("notes-user")
    client.post("/register", json={"username": username, "password": "secret123"})
    origin = {"Origin": "http://localhost:5173"}
    login_response = client.post(
        "/login", json={"username": username, "password": "secret123"}, headers=origin
    )
    token = login_response.cookies.get("todo_access_token")

    create_response = client.post(
        "/notes",
        json={"title": "Planning", "content": "Finish the auth work."},
        headers={"Authorization": f"Bearer {token}", "Origin": "http://localhost:5173"},
    )
    assert create_response.status_code == 201, create_response.text
    note = create_response.json()
    assert note["title"] == "Planning"

    update_response = client.put(
        f"/notes/{note['id']}",
        json={"title": "Planning updated", "content": "Finish the auth and notes work."},
        headers={"Authorization": f"Bearer {token}", "Origin": "http://localhost:5173"},
    )
    assert update_response.status_code == 200, update_response.text
    assert update_response.json()["title"] == "Planning updated"

    list_response = client.get("/notes", headers={"Authorization": f"Bearer {token}"})
    assert list_response.status_code == 200, list_response.text
    assert len(list_response.json()) == 1

    other_user = unique_username("other-notes-user")
    client.post(
        "/register", json={"username": other_user, "password": "secret123"}, headers=origin
    )
    other_login = client.post(
        "/login", json={"username": other_user, "password": "secret123"}, headers=origin
    )
    other_token = other_login.cookies.get("todo_access_token")

    access_response = client.get(f"/notes/{note['id']}", headers={"Authorization": f"Bearer {other_token}"})
    assert access_response.status_code == 404


def test_cookie_authenticated_mutations_reject_untrusted_origins():
    username = unique_username("csrf-user")
    client.post("/register", json={"username": username, "password": "secret123"})
    client.post(
        "/login",
        json={"username": username, "password": "secret123"},
        headers={"Origin": "http://localhost:5173"},
    )

    response = client.post(
        "/todo",
        json={"task": "Blocked cross-origin write"},
        headers={"Origin": "https://attacker.example"},
    )
    assert response.status_code == 403
