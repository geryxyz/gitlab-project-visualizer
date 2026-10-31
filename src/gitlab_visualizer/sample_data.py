from datetime import date, datetime, timezone

from .models import Commit, Project, Student


def create_sample_data() -> tuple[
    Project,
    list[Student],
    list[Commit],
    dict[str, int],
    date,
]:
    project = Project(
        id=100,
        name="Example Student Project",
        path_with_namespace="course/example-project",
        web_url="https://gitlab.example.com/course/example-project",
    )

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

    commit1 = Commit(
        id="commit0001",
        short_id="0001",
        title="Create project structure",
        author_name="Anna Smith",
        author_email="anna@example.com",
        authored_date=datetime(
            2026, 10, 2, 12, 0, tzinfo=timezone.utc
        ),
        committed_date=datetime(
            2026, 10, 2, 12, 0, tzinfo=timezone.utc
        ),
        project_id=project.id,
    )

    commit2 = Commit(
        id="commit0002",
        short_id="0002",
        title="Implement user interface",
        author_name="Anna Smith",
        author_email="anna@example.com",
        authored_date=datetime(
            2026, 10, 8, 12, 0, tzinfo=timezone.utc
        ),
        committed_date=datetime(
            2026, 10, 8, 12, 0, tzinfo=timezone.utc
        ),
        project_id=project.id,
    )

    commit3 = Commit(
        id="commit0003",
        short_id="0003",
        title="Add validation",
        author_name="Peter Jones",
        author_email="peter@example.com",
        authored_date=datetime(
            2026, 10, 14, 12, 0, tzinfo=timezone.utc
        ),
        committed_date=datetime(
            2026, 10, 14, 12, 0, tzinfo=timezone.utc
        ),
        project_id=project.id,
    )

    commit4 = Commit(
        id="commit0004",
        short_id="0004",
        title="Fix validation bug",
        author_name="Peter Jones",
        author_email="peter@example.com",
        authored_date=datetime(
            2026, 10, 20, 12, 0, tzinfo=timezone.utc
        ),
        committed_date=datetime(
            2026, 10, 20, 12, 0, tzinfo=timezone.utc
        ),
        project_id=project.id,
    )

    students = [anna, peter]

    commits = [
        commit1,
        commit2,
        commit3,
        commit4,
    ]

    commit_authors = {
        commit1.id: anna.id,
        commit2.id: anna.id,
        commit3.id: peter.id,
        commit4.id: peter.id,
    }

    course_start = date(2026, 10, 1)

    return (
        project,
        students,
        commits,
        commit_authors,
        course_start,
    )