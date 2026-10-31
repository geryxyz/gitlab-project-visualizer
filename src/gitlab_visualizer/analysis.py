from datetime import date

from .models import Commit


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