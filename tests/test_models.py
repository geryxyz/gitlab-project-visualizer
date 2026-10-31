from datetime import datetime, timezone

from gitlab_visualizer.models import Commit, Project, Student


def test_student_creation() -> None:
    student = Student(
        id=1,
        username="anna",
        name="Anna Smith",
    )

    assert student.id == 1
    assert student.username == "anna"
    assert student.name == "Anna Smith"


def test_project_creation() -> None:
    project = Project(
        id=100,
        name="Example Project",
        path_with_namespace="course/example-project",
        web_url="https://gitlab.example.com/course/example-project",
    )

    assert project.id == 100
    assert project.name == "Example Project"


def test_commit_creation() -> None:
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

    assert commit.project_id == 100
    assert commit.author_name == "Anna Smith"