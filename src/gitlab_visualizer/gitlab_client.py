import os
from dataclasses import dataclass
from typing import Any
from .models import Project
import requests


@dataclass(frozen=True)
class GitLabConfig:
    base_url: str

    @property
    def rest_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/api/v4"

    @property
    def graphql_url(self) -> str:
        return f"{self.base_url.rstrip('/')}/api/graphql"


class GitLabRestClient:
    def __init__(self, config: GitLabConfig) -> None:
        self.config = config

    def get_current_user(self) -> dict[str, Any]:
        token = os.getenv("GITLAB_TOKEN")

        if not token:
            raise RuntimeError(
                "GITLAB_TOKEN environment variable is missing."
            )

        url = f"{self.config.rest_url}/user"

        headers = {
            "PRIVATE-TOKEN": token,
            "Accept": "application/json",
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15,
        )

        response.raise_for_status()

        user_data = response.json()

        if not isinstance(user_data, dict) or "username" not in user_data:
            raise ValueError(
                "Unexpected GitLab response. Check GITLAB_URL."
            )

        return user_data

    def get_projects(self) -> list[Project]:
        token = os.getenv("GITLAB_TOKEN")

        if not token:
            raise RuntimeError(
                "GITLAB_TOKEN environment variable is missing."
            )

        url = f"{self.config.rest_url}/projects"

        headers = {
            "PRIVATE-TOKEN": token,
            "Accept": "application/json",
        }

        params = {
            "membership": "true",
            "per_page": 20,
            "page": 1,
        }

        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15,
        )

        response.raise_for_status()

        project_data = response.json()

        if not isinstance(project_data, list):
            raise ValueError(
                "Unexpected GitLab projects response."
            )

        projects = []

        for item in project_data:
            if not isinstance(item, dict):
                raise ValueError("Invalid project data.")

            project = Project(
                id=item["id"],
                name=item["name"],
                path_with_namespace=item["path_with_namespace"],
                web_url=item["web_url"],
            )

            projects.append(project)

        return projects

class GitLabGraphQLClient:
    def __init__(self, config: GitLabConfig) -> None:
        self.config = config


class GitLabClient:
    def __init__(self, config: GitLabConfig) -> None:
        self.rest = GitLabRestClient(config)
        self.graphql = GitLabGraphQLClient(config)