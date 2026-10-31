import argparse
from pathlib import Path

from .graph_builder import (
    build_project_graph,
    build_timeline_graph,
    export_graphml,
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

    return parser


def main(
    argv: list[str] | None = None,
) -> None:
    parser = build_parser()

    args = parser.parse_args(argv)

    args.func(args)


if __name__ == "__main__":
    main()