from gitlab_visualizer.cli import main


def test_demo_graph_command(
    tmp_path,
    capsys,
) -> None:
    output_file = tmp_path / "demo.graphml"

    main(
        [
            "demo-graph",
            "--output",
            str(output_file),
        ]
    )

    assert output_file.exists()

    captured = capsys.readouterr()

    assert "Created relationship graph" in captured.out


def test_demo_timeline_command(
    tmp_path,
    capsys,
) -> None:
    output_file = tmp_path / "timeline.graphml"

    main(
        [
            "demo-timeline",
            "--output",
            str(output_file),
        ]
    )

    assert output_file.exists()

    captured = capsys.readouterr()

    assert "Created timeline graph" in captured.out