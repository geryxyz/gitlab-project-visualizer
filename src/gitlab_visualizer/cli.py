import os

import requests 
from .gitlab_client import GitLabClient, GitLabConfig

import argparse
from pathlib import Path

from .graph_builder import (
    build_project_graph,
    build_timeline_graph,
    export_graphml,
    build_real_project_graph,
)
from .sample_data import create_sample_data


def run_demo_graph(args: argparse.Namespace) -> None:
    (
        project,
        students,
        commits,
        commit_authors,
        _,
    ) = create_sample_data()

    graph = build_project_graph(
        project=project,
        students=students,
        commits=commits,
        commit_authors=commit_authors,
    )

    export_graphml(
        graph,
        args.output,
    )

    print(
        f"Created relationship graph with "
        f"{graph.number_of_nodes()} nodes and "
        f"{graph.number_of_edges()} edges."
    )

    print(f"Saved to: {args.output}")


def run_demo_timeline(args: argparse.Namespace) -> None:
    (
        project,
        students,
        commits,
        commit_authors,
        course_start,
    ) = create_sample_data()

    graph = build_timeline_graph(
        project=project,
        students=students,
        commits=commits,
        commit_authors=commit_authors,
        course_start=course_start,
    )

    export_graphml(
        graph,
        args.output,
    )

    print(
        f"Created timeline graph with "
        f"{graph.number_of_nodes()} nodes and "
        f"{graph.number_of_edges()} edges."
    )

    print(f"Saved to: {args.output}")

def run_whoami(args: argparse.Namespace) -> None:
    base_url = os.getenv("GITLAB_URL")

    if not base_url:
        raise SystemExit(
            "GITLAB_URL environment variable is missing."
        )

    config = GitLabConfig(base_url)
    client = GitLabClient(config)

    try:
        user = client.rest.get_current_user()

    except (RuntimeError, ValueError, requests.exceptions.RequestException) as error:
        raise SystemExit(
            f"Could not connect to GitLab: {error}"
        ) from error

    print("Connected to GitLab successfully!")
    print(f"Username: {user['username']}")
    print(f"User ID: {user.get('id', 'unknown')}")

def run_projects(args: argparse.Namespace) -> None:
    base_url = os.getenv("GITLAB_URL")

    if not base_url:
        raise SystemExit(
            "GITLAB_URL environment variable is missing."
        )

    config = GitLabConfig(base_url)
    client = GitLabClient(config)

    try:
        projects = client.rest.get_projects()

    except (
        RuntimeError,
        ValueError,
        requests.exceptions.RequestException,
    ) as error:
        raise SystemExit(
            f"Could not retrieve projects: {error}"
        ) from error

    if not projects:
        print("No matching projects found.")
        return

    print(f"Found {len(projects)} projects:")

    for project in projects:
        print(
            f"[{project.id}] {project.path_with_namespace}"
        )

def run_inspect_project(args: argparse.Namespace) -> None:
    base_url = os.getenv("GITLAB_URL")

    if not base_url:
        raise SystemExit(
            "GITLAB_URL environment variable is missing."
        )

    client = GitLabClient(GitLabConfig(base_url))

    try:
        members = client.rest.get_members(args.project_id)
        commits = client.rest.get_commits(args.project_id)

    except (
        RuntimeError,
        ValueError,
        KeyError,
        requests.exceptions.RequestException,
    ) as error:
        raise SystemExit(
            f"Could not inspect project: {error}"
        ) from error

    print(f"Project ID: {args.project_id}")
    print(f"Members returned: {len(members)}")
    print(f"Commits returned: {len(commits)}")

    print("\nRecent commits:")

    for commit in commits[:5]:
        print(
            f"  {commit.short_id} | "
            f"{commit.authored_date:%Y-%m-%d}"
        )


def run_graphql_whoami(args: argparse.Namespace) -> None:
    base_url = os.getenv("GITLAB_URL")

    if not base_url:
        raise SystemExit(
            "GITLAB_URL environment variable is missing."
        )

    client = GitLabClient(GitLabConfig(base_url))

    try:
        user = client.graphql.get_current_user()

    except (
        RuntimeError,
        ValueError,
        requests.exceptions.RequestException,
    ) as error:
        raise SystemExit(
            f"GraphQL request failed: {error}"
        ) from error

    print("Connected to GitLab GraphQL successfully!")
    print(f"Username: {user['username']}")
    print(f"Name: {user['name']}")


def run_real_graph(args: argparse.Namespace) -> None:
    base_url = os.getenv("GITLAB_URL")

    if not base_url:
        raise SystemExit(
            "GITLAB_URL environment variable is missing."
        )

    client = GitLabClient(GitLabConfig(base_url))

    try:
        project = client.rest.get_project(args.project_id)
        members = client.rest.get_members(args.project_id)
        commits = client.rest.get_commits(args.project_id)

    except (
        RuntimeError,
        ValueError,
        KeyError,
        requests.exceptions.RequestException,
    ) as error:
        raise SystemExit(
            f"Could not retrieve project data: {error}"
        ) from error

    selected_commits = commits[:args.max_commits]

    graph = build_real_project_graph(
        project=project,
        members=members,
        commits=selected_commits,
    )

    export_graphml(graph, args.output)

    print("Real GitLab graph generated successfully!")
    print(f"Project ID: {project.id}")
    print(f"Members retrieved: {len(members)}")
    print(f"Commits retrieved: {len(commits)}")
    print(f"Commits displayed: {len(selected_commits)}")
    print(f"Graph nodes: {graph.number_of_nodes()}")
    print(f"Graph edges: {graph.number_of_edges()}")
    print(f"Saved to: {args.output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gitlab-visualizer",
        description=(
            "Visualize GitLab student project activity."
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version="gitlab-project-visualizer 0.1.0",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    graph_parser = subparsers.add_parser(
        "demo-graph",
        help="Generate a sample relationship graph.",
    )

    graph_parser.add_argument(
        "--output",
        type=Path,
        default=Path("demo.graphml"),
        help="Output GraphML file.",
    )

    graph_parser.set_defaults(
        func=run_demo_graph,
    )

    timeline_parser = subparsers.add_parser(
        "demo-timeline",
        help="Generate a sample timeline graph.",
    )

    timeline_parser.add_argument(
        "--output",
        type=Path,
        default=Path("timeline.graphml"),
        help="Output GraphML file.",
    )

    timeline_parser.set_defaults(
        func=run_demo_timeline,
    )

    whoami_parser = subparsers.add_parser(
        "whoami",
        help="Test GitLab API authentication.",
    )

    whoami_parser.set_defaults(
        func=run_whoami,
    )
    projects_parser = subparsers.add_parser(
        "projects",
        help="List GitLab projects.",
    )

    projects_parser.set_defaults(
        func=run_projects,
    )
    inspect_parser = subparsers.add_parser(
        "inspect-project",
        help="Retrieve GitLab project members and commits.",
    )

    inspect_parser.add_argument(
        "project_id",
        type=int,
        help="Numeric GitLab project ID.",
    )

    inspect_parser.set_defaults(
        func=run_inspect_project,
    )
    graphql_parser = subparsers.add_parser(
        "graphql-whoami",
        help="Test GitLab GraphQL authentication.",
    )

    graphql_parser.set_defaults(
        func=run_graphql_whoami,
    )

    real_parser = subparsers.add_parser(
        "real-graph",
        help="Create a GraphML graph from a real GitLab project.",
    )

    real_parser.add_argument(
        "project_id",
        type=int,
        help="Numeric GitLab project ID.",
    )

    real_parser.add_argument(
        "--output",
        type=Path,
        default=Path("real-project.graphml"),
        help="GraphML output file.",
    )

    real_parser.add_argument(
        "--max-commits",
        type=int,
        default=10,
        choices=range(1, 31),
        metavar="1..30",
        help="Number of commits to display (default: 10).",
    )

    real_parser.set_defaults(func=run_real_graph)

    return parser


def main(
    argv: list[str] | None = None,
) -> None:
    parser = build_parser()

    args = parser.parse_args(argv)

    args.func(args)


if __name__ == "__main__":
    main()