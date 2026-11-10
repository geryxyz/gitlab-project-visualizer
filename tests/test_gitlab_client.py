import pytest
from gitlab_visualizer.gitlab_client import (
    GitLabClient,
    GitLabConfig,
    GitLabGraphQLClient,
    GitLabRestClient,
)

def test_get_current_user(monkeypatch) -> None:
    from gitlab_visualizer import gitlab_client

    monkeypatch.setenv("GITLAB_TOKEN", "fake-test-token")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "id": 123,
                "username": "test_student",
                "name": "Test Student",
            }

    def fake_get(url, headers, timeout):
        assert url == "https://gitlab.example.com/api/v4/user"
        assert headers["PRIVATE-TOKEN"] == "fake-test-token"
        assert timeout == 15

        return FakeResponse()

    monkeypatch.setattr(
        gitlab_client.requests,
        "get",
        fake_get,
    )

    config = GitLabConfig("https://gitlab.example.com")
    client = GitLabRestClient(config)

    user = client.get_current_user()

    assert user["id"] == 123
    assert user["username"] == "test_student"


def test_get_current_user_without_token(monkeypatch) -> None:
    monkeypatch.delenv("GITLAB_TOKEN", raising=False)

    config = GitLabConfig("https://gitlab.example.com")
    client = GitLabRestClient(config)

    with pytest.raises(RuntimeError, match="GITLAB_TOKEN"):
        client.get_current_user()
        
def test_gitlab_config_urls() -> None:
    config = GitLabConfig(
        base_url="https://gitlab.example.com"
    )

    assert config.rest_url == (
        "https://gitlab.example.com/api/v4"
    )

    assert config.graphql_url == (
        "https://gitlab.example.com/api/graphql"
    )


def test_gitlab_config_removes_trailing_slash() -> None:
    config = GitLabConfig(
        base_url="https://gitlab.example.com/"
    )

    assert config.rest_url == (
        "https://gitlab.example.com/api/v4"
    )

    assert config.graphql_url == (
        "https://gitlab.example.com/api/graphql"
    )


def test_gitlab_client_contains_both_api_clients() -> None:
    config = GitLabConfig(
        base_url="https://gitlab.example.com"
    )

    client = GitLabClient(config)

    assert isinstance(
        client.rest,
        GitLabRestClient,
    )

    assert isinstance(
        client.graphql,
        GitLabGraphQLClient,
    )