import pytest
from gitlab_visualizer.gitlab_client import (
    GitLabClient,
    GitLabConfig,
    GitLabGraphQLClient,
    GitLabRestClient,
)
from gitlab_visualizer.models import Project

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
def test_get_projects(monkeypatch) -> None:
    from gitlab_visualizer import gitlab_client

    monkeypatch.setenv("GITLAB_TOKEN", "fake-token")

    class FakeResponse:
        headers = {}

        def raise_for_status(self):
            pass

        def json(self):
            return [
                {
                    "id": 101,
                    "name": "Example Project",
                    "path_with_namespace": "course/example",
                    "web_url": "https://gitlab.example.com/course/example",
                }
            ]

    def fake_get(url, headers, params, timeout):
        assert url == "https://gitlab.example.com/api/v4/projects"
        assert headers["PRIVATE-TOKEN"] == "fake-token"
        assert params["membership"] == "true"
        assert params["per_page"] == 20
        assert params["page"] == 1
        assert timeout == 15

        return FakeResponse()

    monkeypatch.setattr(
        gitlab_client.requests,
        "get",
        fake_get,
    )

    config = GitLabConfig("https://gitlab.example.com")
    client = GitLabRestClient(config)

    projects = client.get_projects()

    assert len(projects) == 1
    assert isinstance(projects[0], Project)
    assert projects[0].id == 101
    assert projects[0].name == "Example Project"


def test_get_projects_without_token(monkeypatch) -> None:
    monkeypatch.delenv("GITLAB_TOKEN", raising=False)

    config = GitLabConfig("https://gitlab.example.com")
    client = GitLabRestClient(config)

    with pytest.raises(RuntimeError, match="GITLAB_TOKEN"):
        client.get_projects()
def test_get_members(monkeypatch) -> None:
    config = GitLabConfig("https://gitlab.example.com")
    client = GitLabRestClient(config)

    def fake_items(project_id, resource):
        assert project_id == 100
        assert resource == "members/all"

        return [
            {
                "id": 1,
                "username": "anna",
                "name": "Anna Smith",
            }
        ]

    monkeypatch.setattr(client, "_get_project_items", fake_items)

    members = client.get_members(100)

    assert len(members) == 1
    assert members[0].username == "anna"
    assert members[0].id == 1


def test_get_commits(monkeypatch) -> None:
    config = GitLabConfig("https://gitlab.example.com")
    client = GitLabRestClient(config)

    def fake_items(project_id, resource):
        assert project_id == 100
        assert resource == "repository/commits"

        return [
            {
                "id": "abcdef123456",
                "short_id": "abcdef12",
                "title": "Initial commit",
                "author_name": "Anna Smith",
                "author_email": "anna@example.com",
                "authored_date": "2026-10-12T10:00:00Z",
                "committed_date": "2026-10-12T10:05:00Z",
            }
        ]

    monkeypatch.setattr(client, "_get_project_items", fake_items)

    commits = client.get_commits(100)

    assert len(commits) == 1
    assert commits[0].project_id == 100
    assert commits[0].author_name == "Anna Smith"
    assert commits[0].authored_date.year == 2026
    assert commits[0].committed_date.minute == 5


def test_get_projects_multiple_pages(monkeypatch) -> None:
    from gitlab_visualizer import gitlab_client

    monkeypatch.setenv(
        "GITLAB_TOKEN",
        "fake-test-token",
    )

    requested_pages = []

    class FakeResponse:
        def __init__(self, page):
            self.page = page

            if page == 1:
                self.headers = {"X-Next-Page": "2"}
            else:
                self.headers = {"X-Next-Page": ""}

        def raise_for_status(self):
            pass

        def json(self):
            return [
                {
                    "id": self.page,
                    "name": f"Project {self.page}",
                    "path_with_namespace": (
                        f"course/project-{self.page}"
                    ),
                    "web_url": (
                        f"https://gitlab.example.com/"
                        f"course/project-{self.page}"
                    ),
                }
            ]

    def fake_get(url, headers, params, timeout):
        requested_pages.append(params["page"])

        return FakeResponse(params["page"])

    monkeypatch.setattr(
        gitlab_client.requests,
        "get",
        fake_get,
    )

    client = GitLabRestClient(
        GitLabConfig("https://gitlab.example.com")
    )

    projects = client.get_projects()

    assert len(projects) == 2
    assert projects[0].id == 1
    assert projects[1].id == 2

    assert requested_pages == [1, 2]


def test_graphql_current_user(monkeypatch) -> None:
    from gitlab_visualizer import gitlab_client

    monkeypatch.setenv("GITLAB_TOKEN", "fake-token")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "data": {
                    "currentUser": {
                        "username": "anna",
                        "name": "Anna Smith",
                    }
                }
            }

    def fake_post(url, headers, json, timeout):
        assert url == "https://gitlab.example.com/api/graphql"
        assert headers["Authorization"] == "Bearer fake-token"
        assert "currentUser" in json["query"]
        assert timeout == 15

        return FakeResponse()

    monkeypatch.setattr(
        gitlab_client.requests,
        "post",
        fake_post,
    )

    client = GitLabGraphQLClient(
        GitLabConfig("https://gitlab.example.com")
    )

    user = client.get_current_user()

    assert user["username"] == "anna"
    assert user["name"] == "Anna Smith"


def test_graphql_without_token(monkeypatch) -> None:
    monkeypatch.delenv("GITLAB_TOKEN", raising=False)

    client = GitLabGraphQLClient(
        GitLabConfig("https://gitlab.example.com")
    )

    with pytest.raises(RuntimeError, match="GITLAB_TOKEN"):
        client.get_current_user()


def test_graphql_error_response(monkeypatch) -> None:
    from gitlab_visualizer import gitlab_client

    monkeypatch.setenv("GITLAB_TOKEN", "fake-token")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "errors": [
                    {"message": "Invalid query"}
                ]
            }

    def fake_post(url, headers, json, timeout):
        return FakeResponse()

    monkeypatch.setattr(
        gitlab_client.requests,
        "post",
        fake_post,
    )

    client = GitLabGraphQLClient(
        GitLabConfig("https://gitlab.example.com")
    )

    with pytest.raises(ValueError, match="Invalid query"):
        client.get_current_user()


def test_get_single_project(monkeypatch):
    from gitlab_visualizer import gitlab_client

    monkeypatch.setenv("GITLAB_TOKEN", "fake-token")

    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "id": 100,
                "name": "Test Project",
                "path_with_namespace": "course/test",
                "web_url": "https://gitlab.example.com/course/test",
            }

    def fake_get(url, headers, timeout):
        assert url == (
            "https://gitlab.example.com/api/v4/projects/100"
        )
        assert headers["PRIVATE-TOKEN"] == "fake-token"
        return FakeResponse()

    monkeypatch.setattr(
        gitlab_client.requests,
        "get",
        fake_get,
    )

    client = GitLabRestClient(
        GitLabConfig("https://gitlab.example.com")
    )

    project = client.get_project(100)

    assert project.id == 100
    assert project.name == "Test Project"
