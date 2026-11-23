from datetime import date, timedelta, timezone

from .models import Commit, Project

import networkx as nx

def group_commits_by_week(
    commits: list[Commit],
    commit_authors: dict[str, int],
    course_start: date,
) -> dict[int, dict[int, int]]:
    activity: dict[int, dict[int, int]] = {}

    for commit in commits:
        author_id = commit_authors.get(commit.id)

        if author_id is None:
            continue

        days_from_start = (
            commit.authored_date.date() - course_start
        ).days

        if days_from_start < 0:
            continue

        week_number = days_from_start // 7 + 1

        if week_number not in activity:
            activity[week_number] = {}

        activity[week_number][author_id] = (
            activity[week_number].get(author_id, 0) + 1
        )

    return activity


def build_real_timeline_graph(
    project: Project,
    commits: list[Commit],
    course_start: date,
    course_end: date | None = None,
) -> nx.DiGraph:
    """
    Build a weekly project activity timeline.

    Weeks are seven-day periods starting at course_start.
    Counts use commit authored dates normalized to UTC.
    No student identities are inferred.
    """
    if course_end is not None and course_end < course_start:
        raise ValueError(
            "Course end date cannot be before start date."
        )

    commit_dates = []

    for commit in commits:
        if commit.project_id != project.id:
            raise ValueError(
                "Commit belongs to a different project."
            )

        authored_at = commit.authored_date

        if (
            authored_at.tzinfo is None
            or authored_at.utcoffset() is None
        ):
            raise ValueError(
                "Commit authored date must include a timezone."
            )

        # Use one consistent timezone for week boundaries.
        commit_day = authored_at.astimezone(
            timezone.utc
        ).date()

        if commit_day < course_start:
            continue

        if course_end is not None and commit_day > course_end:
            continue

        commit_dates.append(commit_day)

    # If the course end is not specified, end at the
    # most recent included commit, or at course_start
    # if there are no qualifying commits.
    last_day = (
        course_end
        if course_end is not None
        else max(commit_dates, default=course_start)
    )

    week_count = (
        (last_day - course_start).days // 7
    ) + 1

    # Safety limit for our semester-scale visualization.
    if week_count > 60:
        raise ValueError(
            "Timeline exceeds 60 weeks."
        )

    weekly_counts = [0] * week_count

    for commit_day in commit_dates:
        week_index = (
            (commit_day - course_start).days // 7
        )
        weekly_counts[week_index] += 1

    graph = nx.DiGraph()

    graph.graph["date_basis"] = "authored_date_utc"
    graph.graph["scope"] = "default_branch_commits"

    project_node = f"project:{project.id}"

    graph.add_node(
        project_node,
        label=f"Project: {project.name}",
        entity_type="project",
    )

    previous_week_node = None

    for index, count in enumerate(weekly_counts):
        week_number = index + 1

        week_start = course_start + timedelta(
            days=index * 7
        )

        week_end = min(
            week_start + timedelta(days=6),
            last_day,
        )

        week_node = (
            f"week:{project.id}:{week_number}"
        )

        graph.add_node(
            week_node,
            label=(
                f"Week {week_number}\n"
                f"{week_start.isoformat()} to "
                f"{week_end.isoformat()}\n"
                f"{count} commits"
            ),
            entity_type="activity_week",
            week_number=week_number,
            week_start=week_start.isoformat(),
            week_end=week_end.isoformat(),
            commit_count=count,
        )

        if previous_week_node is None:
            graph.add_edge(
                project_node,
                week_node,
                relationship="timeline_start",
                label="timeline_start",
            )
        else:
            graph.add_edge(
                previous_week_node,
                week_node,
                relationship="next_week",
                label="next_week",
            )

        previous_week_node = week_node

    return graph
