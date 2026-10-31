from gitlab_visualizer.gitlab_client import (
    GitLabClient,
    GitLabConfig,
    GitLabGraphQLClient,
    GitLabRestClient,
)


def test_gitlab_config_urls() -> None:
    config = GitLabConfig(
        base_url="https://gitlab.example.com"
    )

    assert config.rest_url == (
        "https://gitlab.example.com/api/v4"
    )

    assert config.graphql_url == (
        "https://gitlab.example.com/api/graphql"
    )


def test_gitlab_config_removes_trailing_slash() -> None:
    config = GitLabConfig(
        base_url="https://gitlab.example.com/"
    )

    assert config.rest_url == (
        "https://gitlab.example.com/api/v4"
    )

    assert config.graphql_url == (
        "https://gitlab.example.com/api/graphql"
    )


def test_gitlab_client_contains_both_api_clients() -> None:
    config = GitLabConfig(
        base_url="https://gitlab.example.com"
    )

    client = GitLabClient(config)

    assert isinstance(
        client.rest,
        GitLabRestClient,
    )

    assert isinstance(
        client.graphql,
        GitLabGraphQLClient,
    )