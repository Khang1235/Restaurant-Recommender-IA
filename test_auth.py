import os, sqlite3, tempfile, sys
sys.path.insert(0, os.path.dirname(__file__))
import pytest
import auth


@pytest.fixture
def conn():
    path = tempfile.mktemp(suffix=".db")
    c = sqlite3.connect(path)
    c.row_factory = sqlite3.Row
    auth.create_user_tables(c)
    yield c
    c.close(); os.remove(path)


def test_register_then_authenticate(conn):
    ok, _ = auth.register(conn, "karasu", "correcthorse", "correcthorse")
    assert ok
    ok, _, user_id = auth.authenticate(conn, "karasu", "correcthorse")
    assert ok and user_id == 1


def test_duplicate_username_rejected(conn):
    auth.register(conn, "karasu", "correcthorse", "correcthorse")
    ok, msg = auth.register(conn, "karasu", "different123", "different123")
    assert not ok and "taken" in msg


def test_password_below_minimum_rejected(conn):
    ok, _ = auth.register(conn, "bob", "a" * (auth.MIN_PASSWORD_LENGTH - 1),
                          "a" * (auth.MIN_PASSWORD_LENGTH - 1))
    assert not ok


def test_password_at_minimum_accepted(conn):
    ok, _ = auth.register(conn, "bob", "a" * auth.MIN_PASSWORD_LENGTH,
                          "a" * auth.MIN_PASSWORD_LENGTH)
    assert ok


def test_mismatched_confirmation_rejected(conn):
    ok, msg = auth.register(conn, "bob", "correcthorse", "correcthorsf")
    assert not ok and "match" in msg


def test_wrong_password_and_unknown_user_give_same_message(conn):
    auth.register(conn, "karasu", "correcthorse", "correcthorse")
    _, wrong_pw, _ = auth.authenticate(conn, "karasu", "notmypassword")
    _, no_user, _ = auth.authenticate(conn, "ghost", "notmypassword")
    assert wrong_pw == no_user


def test_password_is_not_stored_in_plaintext(conn):
    auth.register(conn, "karasu", "correcthorse", "correcthorse")
    row = conn.execute("SELECT password_hash, salt FROM users").fetchone()
    assert b"correcthorse" not in row["password_hash"]
    assert len(row["salt"]) == 16


def test_same_password_produces_different_hashes(conn):
    auth.register(conn, "a", "correcthorse", "correcthorse")
    auth.register(conn, "b", "correcthorse", "correcthorse")
    rows = conn.execute("SELECT password_hash FROM users ORDER BY id").fetchall()
    assert rows[0]["password_hash"] != rows[1]["password_hash"]
