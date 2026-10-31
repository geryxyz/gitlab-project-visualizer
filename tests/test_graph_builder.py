from datetime import datetime, timezone

from gitlab_visualizer.graph_builder import build_project_graph
from gitlab_visualizer.models import Commit, Project, Student
from gitlab_visualizer.graph_builder import (
    build_project_graph,
    export_graphml,
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