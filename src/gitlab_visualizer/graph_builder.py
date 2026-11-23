from datetime import date, timedelta
from pathlib import Path

import networkx as nx

from .analysis import group_commits_by_week
from .models import Commit, Project, Student
from hashlib import sha256

def compact_label(text: str, max_length: int = 45) -> str:
    """Shorten text so graph labels remain readable."""
    cleaned = " ".join(text.split())

    if len(cleaned) <= max_length:
        return cleaned

    return cleaned[:max_length - 3].rstrip() + "..."

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

def build_real_project_graph(
    project: Project,
    members: list[Student],
    commits: list[Commit],
):
    graph = build_project_graph(
        project=project,
        students=[],
        commits=commits,
        commit_authors={},
    )

    project_node = f"project:{project.id}"

    # Give the project a concise, identifiable label.
    graph.nodes[project_node]["label"] = (
        f"Project\n{compact_label(project.name)}"
    )

    # Add GitLab accounts with project membership.
    for member in members:
        member_node = f"member:{member.id}"

        graph.add_node(
            member_node,
            label=(
                f"GitLab member\n"
                f"{compact_label(member.username)}"
            ),
            entity_type="gitlab_member",
        )

        graph.add_edge(
            member_node,
            project_node,
            relationship="member_of",
            label="member_of",
        )

    # Add recorded Git authors without claiming that
    # they match particular GitLab member accounts.
    for commit in commits:
        commit_node = f"commit:{commit.id}"

        graph.nodes[commit_node]["label"] = (
            f"Commit {commit.short_id}\n"
            f"{compact_label(commit.title)}"
        )

        name = commit.author_name.strip()
        email = commit.author_email.strip().casefold()

        if email:
            author_key = f"{name.casefold()}\0{email}"
        else:
            author_key = f"unknown:{commit.id}"

        author_hash = sha256(
            author_key.encode("utf-8")
        ).hexdigest()

        author_node = f"git-author:{author_hash}"

        if author_node not in graph:
            graph.add_node(
                author_node,
                label=(
                    "Git author (unverified)\n"
                    f"{compact_label(name or 'Unknown')}"
                ),
                entity_type="git_author",
                identity_status="unverified",
            )

        graph.add_edge(
            author_node,
            commit_node,
            relationship="declared_author",
            label="declared_author",
        )

        # Do not retain raw author emails in the
        # exported commit node attributes.
        graph.nodes[commit_node].pop(
            "author_email", None
        )

    # Metadata describing what this graph represents.
    graph.graph["graph_kind"] = "relationship"
    graph.graph["author_identity"] = "unverified"
    graph.graph["commit_scope"] = "default_branch"

    return graph

def build_timeline_graph(
    project: Project,
    students: list[Student],
    commits: list[Commit],
    commit_authors: dict[str, int],
    course_start: date,
) -> nx.DiGraph:
    graph = nx.DiGraph()

    project_node = f"project:{project.id}"

    graph.add_node(
        project_node,
        type="project",
        label=project.name,
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
            label="member of",
        )

    activity = group_commits_by_week(
        commits=commits,
        commit_authors=commit_authors,
        course_start=course_start,
    )

    previous_week_node = None

    for week_number in sorted(activity):
        week_start = course_start + timedelta(
            weeks=week_number - 1
        )

        week_end = week_start + timedelta(days=6)

        total_commits = sum(
            activity[week_number].values()
        )

        week_node = f"week:{week_number}"

        graph.add_node(
            week_node,
            type="week",
            label=(
                f"Week {week_number}\n"
                f"{week_start:%d %b} - {week_end:%d %b}\n"
                f"{total_commits} commits"
            ),
            week=week_number,
            total_commits=total_commits,
        )

        if previous_week_node is not None:
            graph.add_edge(
                previous_week_node,
                week_node,
                relationship="next",
                label="next",
            )

        previous_week_node = week_node

        for student_id, commit_count in activity[
            week_number
        ].items():
            if student_id not in student_ids:
                continue

            student_node = f"student:{student_id}"

            if commit_count == 1:
                edge_label = "1 commit"
            else:
                edge_label = f"{commit_count} commits"

            graph.add_edge(
                student_node,
                week_node,
                relationship="contributed",
                label=edge_label,
                commit_count=commit_count,
            )

    return graph

def export_graphml(
    graph: nx.DiGraph,
    output_path: str | Path,
) -> None:
    nx.write_graphml(graph, output_path)


