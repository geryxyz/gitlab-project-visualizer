import os
from datetime import datetime
from dataclasses import dataclass
from typing import Any
from .models import Project
from .models import Commit, Student
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

    def _get_paginated(
        self,
        resource: str,
        extra_params: dict | None = None,
    ) -> list[dict]:
        token = os.getenv("GITLAB_TOKEN")

        if not token:
            raise RuntimeError(
                "GITLAB_TOKEN environment variable is missing."
            )

        url = f"{self.config.rest_url}/{resource}"

        headers = {
            "PRIVATE-TOKEN": token,
            "Accept": "application/json",
        }

        all_items = []
        page = 1

        for _ in range(100):
            params = {
                "page": page,
                "per_page": 20,
            }

            if extra_params:
                params.update(extra_params)

            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=15,
            )

            response.raise_for_status()

            data = response.json()

            if not isinstance(data, list) or any(
                not isinstance(item, dict) for item in data
            ):
                raise ValueError(
                    "Unexpected GitLab API response."
                )

            all_items.extend(data)

            next_page = response.headers.get(
                "X-Next-Page", ""
            )

            if not next_page:
                return all_items

            try:
                next_page_number = int(next_page)
            except ValueError as error:
                raise ValueError(
                    "Invalid GitLab pagination header."
                ) from error

            if next_page_number <= page:
                raise ValueError(
                    "Invalid GitLab pagination sequence."
                )

            page = next_page_number

        raise RuntimeError(
            "Pagination exceeded 100 pages."
        )

    def get_projects(self) -> list[Project]:
        data = self._get_paginated(
            resource="projects",
            extra_params={"membership": "true"},
        )

        projects = []

        for item in data:
            project = Project(
                id=item["id"],
                name=item["name"],
                path_with_namespace=item["path_with_namespace"],
                web_url=item["web_url"],
            )

            projects.append(project)
        return projects


    def get_project(self, project_id: int) -> Project:
        if project_id <= 0:
            raise ValueError("Project ID must be positive.")

        token = os.getenv("GITLAB_TOKEN")

        if not token:
            raise RuntimeError(
                "GITLAB_TOKEN environment variable is missing."
            )

        response = requests.get(
            f"{self.config.rest_url}/projects/{project_id}",
            headers={
                "PRIVATE-TOKEN": token,
                "Accept": "application/json",
            },
            timeout=15,
        )

        response.raise_for_status()
        data = response.json()

        if not isinstance(data, dict):
            raise ValueError("Unexpected project response.")

        return Project(
            id=data["id"],
            name=data["name"],
            path_with_namespace=data["path_with_namespace"],
            web_url=data["web_url"],
        )


    def _get_project_items(
        self,
        project_id: int,
        resource: str,
    ) -> list[dict]:
        if project_id <= 0:
            raise ValueError(
                "Project ID must be positive."
            )

        return self._get_paginated(
            resource=f"projects/{project_id}/{resource}"
        )

        return data
    
    def get_members(
        self,
        project_id: int,
    ) -> list[Student]:
        data = self._get_project_items(
            project_id,
            "members/all",
        )

        return [
            Student(
                id=item["id"],
                username=item["username"],
                name=item["name"],
            )
            for item in data
        ]
    
    def get_commits(
        self,
        project_id: int,
    ) -> list[Commit]:
        data = self._get_project_items(
            project_id,
            "repository/commits",
        )

        commits = []

        for item in data:
            commit = Commit(
                id=item["id"],
                short_id=item["short_id"],
                title=item["title"],
                author_name=item["author_name"],
                author_email=item["author_email"],
                authored_date=datetime.fromisoformat(
                    item["authored_date"].replace("Z", "+00:00")
                ),
                committed_date=datetime.fromisoformat(
                    item["committed_date"].replace("Z", "+00:00")
                ),
                project_id=project_id,
            )

            commits.append(commit)

        return commits


class GitLabGraphQLClient:
    def __init__(self, config: GitLabConfig) -> None:
        self.config = config

    def execute(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        token = os.getenv("GITLAB_TOKEN")

        if not token:
            raise RuntimeError(
                "GITLAB_TOKEN environment variable is missing."
            )

        payload = {"query": query}

        if variables is not None:
            payload["variables"] = variables

        response = requests.post(
            self.config.graphql_url,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
        )

        response.raise_for_status()

        result = response.json()

        if not isinstance(result, dict):
            raise ValueError(
                "Unexpected GitLab GraphQL response."
            )

        if result.get("errors"):
            raise ValueError(
                f"GitLab GraphQL error: {result['errors'][0].get('message', 'Unknown error')}"
            )

        data = result.get("data")

        if not isinstance(data, dict):
            raise ValueError(
                "Missing data in GraphQL response."
            )

        return data

    def get_current_user(self) -> dict[str, Any]:
        query = """
        query {
            currentUser {
                username
                name
            }
        }
        """

        data = self.execute(query)

        user = data.get("currentUser")

        if not isinstance(user, dict):
            raise ValueError(
                "Could not retrieve current GitLab user."
            )

        return user



class GitLabClient:
    def __init__(self, config: GitLabConfig) -> None:
        self.rest = GitLabRestClient(config)
        self.graphql = GitLabGraphQLClient(config)