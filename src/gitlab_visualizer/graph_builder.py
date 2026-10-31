from pathlib import Path

import networkx as nx

from .models import Commit, Project, Student


def build_project_graph(
    project: Project,
    students: list[Student],
    commits: list[Commit],
    commit_authors: dict[str, int],
) -> nx.DiGraph:
    graph = nx.DiGraph()

    project_node = f"project:{project.id}"

    graph.add_node(
        project_node,
        type="project",
        label=project.name,
        path=project.path_with_namespace,
        web_url=project.web_url,
    )

    student_ids = {student.id for student in students}

    for student in students:
        student_node = f"student:{student.id}"

        graph.add_node(
            student_node,
            type="student",
            label=student.name,
            username=student.username,
        )

        graph.add_edge(
            student_node,
            project_node,
            relationship="member_of",
        )

    for commit in commits:
        commit_node = f"commit:{commit.id}"

        graph.add_node(
            commit_node,
            type="commit",
            label=commit.short_id,
            title=commit.title,
            authored_date=commit.authored_date.isoformat(),
            committed_date=commit.committed_date.isoformat(),
        )

        graph.add_edge(
            commit_node,
            project_node,
            relationship="belongs_to",
        )

        author_id = commit_authors.get(commit.id)

        if author_id is not None and author_id in student_ids:
            student_node = f"student:{author_id}"

            graph.add_edge(
                student_node,
                commit_node,
                relationship="authored",
            )

    return graph


def export_graphml(
    graph: nx.DiGraph,
    output_path: str | Path,
) -> None:
    nx.write_graphml(graph, output_path)