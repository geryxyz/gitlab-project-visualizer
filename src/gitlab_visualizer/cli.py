import argparse


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="gitlab-visualizer",
        description="Visualize GitLab student project activity.",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="gitlab-project-visualizer 0.1.0",
    )

    parser.parse_args()


if __name__ == "__main__":
    main()