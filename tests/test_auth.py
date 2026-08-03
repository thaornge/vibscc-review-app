from src.auth import _account_password, _active_users, _configured_login_count, _password_key


class FakeResponse:
    def __init__(self, data):
        self.data = data


class FakeUsersTable:
    def __init__(self, users):
        self.users = users

    def select(self, *_args, **_kwargs):
        return self

    def execute(self):
        return FakeResponse(self.users)


class FakeClient:
    def __init__(self, users):
        self.users = users

    def table(self, name):
        assert name == "users"
        return FakeUsersTable(self.users)


class FakeRepo:
    def __init__(self, users):
        self.client = FakeClient(users)


def test_password_key_uses_annotator_code():
    assert _password_key("ANN_01") == "APP_PASSWORD_ANN_01"
    assert _password_key("admin.phuc") == "APP_PASSWORD_ADMIN_PHUC"


def test_active_users_and_configured_passwords(monkeypatch):
    users = [
        {"annotator_code": "ANN_01", "role": "REVIEWER", "active": True},
        {"annotator_code": "ANN_02", "role": "REVIEWER", "active": False},
        {"annotator_code": "ADMIN_PHUC", "role": "ADMIN", "active": "TRUE"},
    ]
    monkeypatch.setenv("APP_PASSWORD_ANN_01", "one")
    monkeypatch.setenv("APP_PASSWORD_ADMIN_PHUC", "admin")

    active = _active_users(FakeRepo(users))

    assert [user["annotator_code"] for user in active] == ["ADMIN_PHUC", "ANN_01"]
    assert _configured_login_count(active) == 2
    assert _account_password("ANN_01") == "one"
