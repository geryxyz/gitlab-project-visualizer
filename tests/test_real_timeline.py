
from datetime import date, datetime, timezone

import pytest

from gitlab_visualizer.analysis import (
    build_real_timeline_graph,
)
from gitlab_visualizer.models import Commit, Project


def make_project() -> Project:
    return Project(
        id=100,
        name="Example Project",
        path_with_namespace="course/example",
        web_url="https://gitlab.example.com/course/example",
    )


def make_commit(
    commit_id: str,
    authored_at: datetime,
) -> Commit:
    return Commit(
        id=commit_id,
        short_id=commit_id[:7],
        title="Test commit",
        author_name="Example Author",
        author_email="author@example.com",
        authored_date=authored_at,
        committed_date=authored_at,
        project_id=100,
    )


def test_real_timeline_includes_inactive_weeks():
    project = make_project()

    commits = [
        make_commit(
            "abc123",
            datetime(
                2026, 10, 2, 10, 0,
                tzinfo=timezone.utc,
            ),
        ),
        make_commit(
            "def456",
            datetime(
                2026, 10, 17, 10, 0,
                tzinfo=timezone.utc,
            ),
        ),
    ]

    graph = build_real_timeline_graph(
        project=project,
        commits=commits,
        course_start=date(2026, 10, 1),
        course_end=date(2026, 10, 21),
    )

    assert graph.number_of_nodes() == 4
    assert graph.number_of_edges() == 3

    assert graph.nodes["week:100:1"][
        "commit_count"
    ] == 1

    assert graph.nodes["week:100:2"][
        "commit_count"
    ] == 0

    assert graph.nodes["week:100:3"][
        "commit_count"
    ] == 1

    assert graph.has_edge(
        "week:100:1", "week:100:2"
    )

    assert graph.has_edge(
        "week:100:2", "week:100:3"
    )


def test_real_timeline_excludes_older_commits():
    project = make_project()

    commits = [
        make_commit(
            "old123",
            datetime(
                2026, 9, 30, 10, 0,
                tzinfo=timezone.utc,
            ),
        ),
        make_commit(
            "new456",
            datetime(
                2026, 10, 3, 10, 0,
                tzinfo=timezone.utc,
            ),
        ),
    ]

    graph = build_real_timeline_graph(
        project=project,
        commits=commits,
        course_start=date(2026, 10, 1),
        course_end=date(2026, 10, 7),
    )

    assert graph.nodes["week:100:1"][
        "commit_count"
    ] == 1


def test_real_timeline_rejects_invalid_dates():
    project = make_project()

    with pytest.raises(
        ValueError,
        match="Course end date",
    ):
        build_real_timeline_graph(
            project=project,
            commits=[],
            course_start=date(2026, 10, 15),
            course_end=date(2026, 10, 1),
        )


def test_real_timeline_with_no_commits():
    graph = build_real_timeline_graph(
        project=make_project(),
        commits=[],
        course_start=date(2026, 10, 1),
        course_end=date(2026, 10, 14),
    )

    assert graph.nodes["week:100:1"][
        "commit_count"
    ] == 0

    assert graph.nodes["week:100:2"][
        "commit_count"
    ] == 0
