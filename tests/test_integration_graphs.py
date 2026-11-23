
from datetime import date

import networkx as nx
import pytest

from gitlab_visualizer import gitlab_client
from gitlab_visualizer.analysis import build_real_timeline_graph
from gitlab_visualizer.gitlab_client import (
    GitLabConfig,
    GitLabRestClient,
)
from gitlab_visualizer.graph_builder import (
    build_real_project_graph,
    export_graphml,
)


@pytest.fixture
def client_with_fake_gitlab(monkeypatch):
    monkeypatch.setenv("GITLAB_TOKEN", "fake-test-token")

    base = "https://gitlab.example.com/api/v4/projects/100"

    responses = {
        base: {
            "id": 100,
            "name": "Example Project",
            "path_with_namespace": "course/example",
            "web_url": "https://gitlab.example.com/course/example",
        },
        f"{base}/members/all": [
            {
                "id": 42,
                "username": "anna123",
                "name": "Anna Smith",
            },
        ],
        f"{base}/repository/commits": [
            {
                "id": "abc123",
                "short_id": "abc123",
                "title": "Initial implementation",
                "author_name": "Anna Smith",
                "author_email": "anna@example.com",
                "authored_date": "2026-10-02T10:00:00Z",
                "committed_date": "2026-10-02T10:05:00Z",
            },
            {
                "id": "def456",
                "short_id": "def456",
                "title": "Improve validation",
                "author_name": "Anna Smith",
                "author_email": "anna@example.com",
                "authored_date": "2026-10-17T10:00:00Z",
                "committed_date": "2026-10-17T10:05:00Z",
            },
        ],
    }

    class FakeResponse:
        headers = {"X-Next-Page": ""}

        def __init__(self, data):
            self.data = data

        def raise_for_status(self):
            pass

        def json(self):
            return self.data

    def fake_get(url, headers, timeout, params=None):
        assert headers["PRIVATE-TOKEN"] == "fake-test-token"
        assert timeout == 15

        if params is not None:
            assert params["page"] == 1

        assert url in responses

        return FakeResponse(responses[url])

    monkeypatch.setattr(
        gitlab_client.requests,
        "get",
        fake_get,
    )

    return GitLabRestClient(
        GitLabConfig("https://gitlab.example.com")
    )


def test_relationship_graphml_integration(
    client_with_fake_gitlab,
    tmp_path,
):
    client = client_with_fake_gitlab

    project = client.get_project(100)
    members = client.get_members(100)
    commits = client.get_commits(100)

    graph = build_real_project_graph(
        project=project,
        members=members,
        commits=commits,
    )

    output = tmp_path / "relationships.graphml"
    export_graphml(graph, output)

    assert output.exists()

    restored = nx.read_graphml(output)

    assert restored.graph["graph_kind"] == "relationship"

    assert restored.has_node("project:100")
    assert restored.has_node("member:42")
    assert restored.has_node("commit:abc123")
    assert restored.has_node("commit:def456")

    assert restored.has_edge(
        "member:42", "project:100"
    )

    author_nodes = [
        node
        for node, attrs in restored.nodes(data=True)
        if attrs.get("entity_type") == "git_author"
    ]

    assert len(author_nodes) == 1

    assert restored.has_edge(
        author_nodes[0], "commit:abc123"
    )

    assert restored.has_edge(
        author_nodes[0], "commit:def456"
    )

    # An account with the same name is not automatically
    # treated as the verified author.
    assert not restored.has_edge(
        "member:42", "commit:abc123"
    )

    assert (
        "Initial implementation"
        in restored.nodes["commit:abc123"]["label"]
    )

    # The raw email should not appear in this export.
    assert "anna@example.com" not in output.read_text(
        encoding="utf-8"
    )


def test_timeline_graphml_integration(
    client_with_fake_gitlab,
    tmp_path,
):
    client = client_with_fake_gitlab

    project = client.get_project(100)
    commits = client.get_commits(100)

    graph = build_real_timeline_graph(
        project=project,
        commits=commits,
        course_start=date(2026, 10, 1),
        course_end=date(2026, 10, 21),
    )

    output = tmp_path / "timeline.graphml"
    export_graphml(graph, output)

    restored = nx.read_graphml(output)

    assert restored.graph["graph_kind"] == "weekly_timeline"
    assert restored.graph["date_basis"] == "authored_date_utc"

    assert restored.nodes["week:100:1"]["commit_count"] == 1
    assert restored.nodes["week:100:2"]["commit_count"] == 0
    assert restored.nodes["week:100:3"]["commit_count"] == 1

    assert restored.has_edge(
        "week:100:1", "week:100:2"
    )

    assert restored.has_edge(
        "week:100:2", "week:100:3"
    )
