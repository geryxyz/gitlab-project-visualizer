from datetime import date, datetime, timezone

from gitlab_visualizer.graph_builder import (
    build_project_graph,
    build_timeline_graph,
    export_graphml,
)
from gitlab_visualizer.models import Commit, Project, Student


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


def make_commit(
    commit_id: str,
    short_id: str,
    title: str,
    author_name: str,
    author_email: str,
    day: int,
) -> Commit:
    commit_time = datetime(
        2026,
        10,
        day,
        12,
        0,
        tzinfo=timezone.utc,
    )

    return Commit(
        id=commit_id,
        short_id=short_id,
        title=title,
        author_name=author_name,
        author_email=author_email,
        authored_date=commit_time,
        committed_date=commit_time,
        project_id=project.id,
    )


commit1 = make_commit(
    "commit0001",
    "0001",
    "Create project structure",
    "Anna Smith",
    "anna@example.com",
    2,
)

commit2 = make_commit(
    "commit0002",
    "0002",
    "Implement user interface",
    "Anna Smith",
    "anna@example.com",
    8,
)

commit3 = make_commit(
    "commit0003",
    "0003",
    "Add validation",
    "Peter Jones",
    "peter@example.com",
    14,
)

commit4 = make_commit(
    "commit0004",
    "0004",
    "Fix validation bug",
    "Peter Jones",
    "peter@example.com",
    20,
)


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


graph = build_project_graph(
    project=project,
    students=[anna, peter],
    commits=commits,
    commit_authors=commit_authors,
)

export_graphml(
    graph,
    "demo.graphml",
)

print(
    f"Created graph with "
    f"{graph.number_of_nodes()} nodes and "
    f"{graph.number_of_edges()} edges."
)
timeline_graph = build_timeline_graph(
    project=project,
    students=[anna, peter],
    commits=commits,
    commit_authors=commit_authors,
    course_start=date(2026, 10, 1),
)

export_graphml(
    timeline_graph,
    "timeline.graphml",
)

print(
    f"Created timeline graph with "
    f"{timeline_graph.number_of_nodes()} nodes and "
    f"{timeline_graph.number_of_edges()} edges."
)