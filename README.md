# GitLab Project Visualizer

A Python command-line application for visualizing student software
project activity retrieved from GitLab.

The goal of the project is to transform GitLab development data into
graph-based visualizations that are easy for instructors to understand
when supervising student projects.

## Current Architecture

The application is divided into several components:

- `models.py` defines the internal data model.
- `gitlab_client.py` defines the planned REST and GraphQL access layers.
- `analysis.py` performs transformations such as grouping activity by week.
- `graph_builder.py` creates NetworkX graph representations.
- `cli.py` provides the command-line interface.
- `sample_data.py` contains temporary development data used before real
  GitLab integration.

The current data flow is:

GitLab REST / GraphQL
→ Python data models
→ NetworkX
→ graph transformation
→ GraphML
→ yEd

The application currently supports two graph representations:

1. A detailed relationship graph containing students, commits and projects.
2. A weekly timeline graph that groups commit activity in order to reduce
   visual complexity.

## Installation

Create and activate a Python 3.14 virtual environment, then install the
project:

```powershell
pip install -e ".[dev]"


## GitLab API Integration

The application supports read-only communication with GitLab through
both the REST API and GraphQL API.

### Implemented Features

- Authentication using a GitLab personal access token.
- Retrieval of the authenticated GitLab user.
- Retrieval of projects associated with the authenticated account.
- Retrieval of project members, including inherited memberships.
- Retrieval of repository commits and their metadata.
- Pagination for project, member, and commit retrieval.
- Basic handling of authentication, HTTP, and API response errors.
- GraphQL queries through a separate client.
- Automated API tests using simulated HTTP responses.

### GitLab Configuration

Set the GitLab server URL and personal access token using
environment variables.

Example for Windows PowerShell:

```powershell
$env:GITLAB_URL = "https://git-okt.sed.inf.szte.hu"

$secureToken = Read-Host "Enter GitLab token" -AsSecureString
$env:GITLAB_TOKEN = [System.Net.NetworkCredential]::new("", $secureToken).Password
Remove-Variable secureToken
```

Use a token with the minimum permissions necessary, such as
`read_api`, where supported.

Never commit access tokens or private student data to the repository.

### CLI Commands

Test REST API authentication:

```powershell
gitlab-visualizer whoami
```

Test GraphQL API authentication:

```powershell
gitlab-visualizer graphql-whoami
```

List projects where the authenticated account is a member:

```powershell
gitlab-visualizer projects
```

Retrieve members and commits for a selected project:

```powershell
gitlab-visualizer inspect-project 123
```

Replace `123` with the actual GitLab project ID.

The existing demonstration commands remain available:

```powershell
gitlab-visualizer demo-graph
gitlab-visualizer demo-timeline
```

### Implementation Notes

GitLab API responses are converted into Python dataclasses.
Project, member, and commit data are kept in memory rather than
stored in a database.

The REST client supports paginated requests. The GraphQL client
currently provides an authenticated user query and a reusable
query execution method.

Repository commit retrieval currently uses the default branch.
Git commit author names and emails are not automatically treated
as verified GitLab user identities.

Graph generation from real GitLab data is planned for Weeks 7–8.

### Testing

Run the automated test suite:

```powershell
pytest
```

The API tests use simulated responses and do not require access
to a live GitLab server.
