import os
from dataclasses import dataclass
from typing import Any

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


class GitLabGraphQLClient:
    def __init__(self, config: GitLabConfig) -> None:
        self.config = config


class GitLabClient:
    def __init__(self, config: GitLabConfig) -> None:
        self.rest = GitLabRestClient(config)
        self.graphql = GitLabGraphQLClient(config)