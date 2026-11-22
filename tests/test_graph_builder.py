from datetime import date, datetime, timezone

from gitlab_visualizer.models import Commit, Project, Student
from gitlab_visualizer.graph_builder import (
    build_project_graph,
    build_timeline_graph,
    export_graphml,
    build_real_project_graph,
)

def test_build_project_graph() -> None:
    student = Student(
        id=1,
        username="anna",
        name="Anna Smith",
    )

    project = Project(
        id=100,
        name="Example Project",
        path_with_namespace="course/example-project",
        web_url="https://gitlab.example.com/course/example-project",
    )

    commit_time = datetime(
        2026,
        10,
        20,
        12,
        30,
        tzinfo=timezone.utc,
    )

    commit = Commit(
        id="abcdef123456",
        short_id="abcdef12",
        title="Implement first feature",
        author_name="Anna Smith",
        author_email="anna@example.com",
        authored_date=commit_time,
        committed_date=commit_time,
        project_id=100,
    )

    graph = build_project_graph(
        project=project,
        students=[student],
        commits=[commit],
        commit_authors={
            commit.id: student.id,
        },
    )

    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 3

    assert graph.has_node("student:1")
    assert graph.has_node("project:100")
    assert graph.has_node("commit:abcdef123456")

    assert graph.has_edge(
        "student:1",
        "project:100",
    )

    assert graph.has_edge(
        "student:1",
        "commit:abcdef123456",
    )

    assert graph.has_edge(
        "commit:abcdef123456",
        "project:100",
    )
    assert (
        graph.edges["student:1", "commit:abcdef123456"]["relationship"]
        == "authored"
    )

    assert (
        graph.edges["commit:abcdef123456", "project:100"]["relationship"]
        == "belongs_to"
    )

def test_export_graphml(tmp_path) -> None:
    student = Student(
        id=1,
        username="anna",
        name="Anna Smith",
    )

    project = Project(
        id=100,
        name="Example Project",
        path_with_namespace="course/example-project",
        web_url="https://gitlab.example.com/course/example-project",
    )

    commit_time = datetime(
        2026,
        10,
        20,
        12,
        30,
        tzinfo=timezone.utc,
    )

    commit = Commit(
        id="abcdef123456",
        short_id="abcdef12",
        title="Implement first feature",
        author_name="Anna Smith",
        author_email="anna@example.com",
        authored_date=commit_time,
        committed_date=commit_time,
        project_id=100,
    )

    graph = build_project_graph(
        project=project,
        students=[student],
        commits=[commit],
        commit_authors={
            commit.id: student.id,
        },
    )

    output_file = tmp_path / "graph.graphml"

    export_graphml(
        graph,
        output_file,
    )

    assert output_file.exists()

def test_build_timeline_graph() -> None:
    anna = Student(
        id=1,
        username="anna",
        name="Anna Smith",
    )

    peter = Student(
        id=2,
        username="peter",
        name="Peter Jones",
    )

    project = Project(
        id=100,
        name="Example Project",
        path_with_namespace="course/example-project",
        web_url="https://gitlab.example.com/course/example-project",
    )

    commit1 = Commit(
        id="commit1",
        short_id="0001",
        title="First commit",
        author_name="Anna Smith",
        author_email="anna@example.com",
        authored_date=datetime(
            2026, 10, 2, 12, 0, tzinfo=timezone.utc
        ),
        committed_date=datetime(
            2026, 10, 2, 12, 0, tzinfo=timezone.utc
        ),
        project_id=100,
    )

    commit2 = Commit(
        id="commit2",
        short_id="0002",
        title="Second commit",
        author_name="Peter Jones",
        author_email="peter@example.com",
        authored_date=datetime(
            2026, 10, 10, 12, 0, tzinfo=timezone.utc
        ),
        committed_date=datetime(
            2026, 10, 10, 12, 0, tzinfo=timezone.utc
        ),
        project_id=100,
    )

    graph = build_timeline_graph(
        project=project,
        students=[anna, peter],
        commits=[commit1, commit2],
        commit_authors={
            commit1.id: anna.id,
            commit2.id: peter.id,
        },
        course_start=date(2026, 10, 1),
    )

    assert graph.has_node("week:1")
    assert graph.has_node("week:2")

    assert graph.has_edge(
        "student:1",
        "week:1",
    )

    assert graph.has_edge(
        "student:2",
        "week:2",
    )

    assert graph.has_edge(
        "week:1",
        "week:2",
    )

def test_real_project_graph_without_author_guessing():
    project = Project(
        id=100,
        name="Test Project",
        path_with_namespace="course/test",
        web_url="https://gitlab.example.com/course/test",
    )

    member = Student(
        id=42,
        username="anna",
        name="Anna",
    )

    graph = build_real_project_graph(
        project=project,
        members=[member],
        commits=[],
    )

    assert "project:100" in graph
    assert "member:42" in graph
    assert graph.has_edge("member:42", "project:100")

    assert graph.nodes["member:42"]["entity_type"] == (
        "gitlab_member"
    )

    assert graph.edges[
        "member:42", "project:100"
    ]["relationship"] == "member_of"

def test_real_graph_groups_same_git_author():
    project = Project(
        id=100,
        name="Test Project",
        path_with_namespace="course/test",
        web_url="https://gitlab.example.com/course/test",
    )

    member = Student(
        id=42,
        username="anna123",
        name="Anna Smith",
    )

    timestamp = datetime(
        2026, 10, 12, 10, 0,
        tzinfo=timezone.utc,
    )

    commits = [
        Commit(
            id="abc123",
            short_id="abc123",
            title="First commit",
            author_name="Anna Smith",
            author_email="anna@example.com",
            authored_date=timestamp,
            committed_date=timestamp,
            project_id=100,
        ),
        Commit(
            id="def456",
            short_id="def456",
            title="Second commit",
            author_name="Anna Smith",
            author_email="anna@example.com",
            authored_date=timestamp,
            committed_date=timestamp,
            project_id=100,
        ),
    ]

    graph = build_real_project_graph(
        project=project,
        members=[member],
        commits=commits,
    )

    author_nodes = [
        node
        for node, data in graph.nodes(data=True)
        if data.get("entity_type") == "git_author"
    ]

    # Both commits share one recorded author signature.
    assert len(author_nodes) == 1

    author_node = author_nodes[0]

    assert graph.has_edge(author_node, "commit:abc123")
    assert graph.has_edge(author_node, "commit:def456")

    assert graph.edges[
        author_node, "commit:abc123"
    ]["relationship"] == "declared_author"

    # The GitLab account remains separate.
    assert graph.has_edge("member:42", "project:100")
    assert not graph.has_edge(
        "member:42", "commit:abc123"
    )

    assert graph.nodes[author_node][
        "identity_status"
    ] == "unverified"


def test_same_name_different_emails_are_separate():
    project = Project(
        id=100,
        name="Test Project",
        path_with_namespace="course/test",
        web_url="https://gitlab.example.com/course/test",
    )

    timestamp = datetime(
        2026, 10, 12, 10, 0,
        tzinfo=timezone.utc,
    )

    commits = []

    for commit_id, email in [
        ("abc123", "anna@example.com"),
        ("def456", "anna@university.example"),
    ]:
        commits.append(
            Commit(
                id=commit_id,
                short_id=commit_id,
                title="Example commit",
                author_name="Anna Smith",
                author_email=email,
                authored_date=timestamp,
                committed_date=timestamp,
                project_id=100,
            )
        )

    graph = build_real_project_graph(
        project=project,
        members=[],
        commits=commits,
    )

    author_nodes = [
        node
        for node, data in graph.nodes(data=True)
        if data.get("entity_type") == "git_author"
    ]

    # Same name, different recorded author signatures.
    assert len(author_nodes) == 2
