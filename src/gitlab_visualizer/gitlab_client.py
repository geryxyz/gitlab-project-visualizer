from dataclasses import dataclass


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


class GitLabGraphQLClient:
    def __init__(self, config: GitLabConfig) -> None:
        self.config = config


class GitLabClient:
    def __init__(self, config: GitLabConfig) -> None:
        self.rest = GitLabRestClient(config)
        self.graphql = GitLabGraphQLClient(config)