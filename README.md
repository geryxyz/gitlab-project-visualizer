# GitLab Project Visualizer

A Python command-line application for visualizing student software project activity retrieved from GitLab.

The goal of the project is to transform GitLab development data into clear, graph-based visualizations that help instructors understand and monitor student project progress.

The application focuses on visualizing relationships and activity over time rather than automatically evaluating or grading students.

## Current Architecture

The application is divided into several components:

- `models.py` defines the internal data models using Python dataclasses.
- `gitlab_client.py` implements GitLab REST and GraphQL API communication.
- `analysis.py` performs activity analysis and builds weekly timeline graphs.
- `graph_builder.py` creates NetworkX relationship graphs and exports GraphML files.
- `cli.py` provides the command-line interface.
- `sample_data.py` contains demonstration data for testing graph generation.

The main data flow is:

```text
GitLab REST / GraphQL API
          |
          v
    Python data models
          |
          v
 Data transformation
          |
          v
    NetworkX graphs
          |
          v
     GraphML export
          |
          v
   yEd Graph Editor
```

The application currently supports two main graph representations:

1. **Relationship graphs** containing projects, GitLab members, commits, recorded Git authors, and their relationships.
2. **Weekly timeline graphs** showing project activity over consecutive weeks, including periods without recorded commits.

Data is processed in memory without requiring a database.

## Requirements

- Python 3.14
- Git
- Network access to an authorized GitLab instance
- A GitLab personal access token with appropriate read permissions
- yEd Graph Editor for viewing exported GraphML files

The main Python libraries used are:

- `requests` for HTTP communication with GitLab.
- `networkx` for graph construction and GraphML export.
- `matplotlib` for visualization-related functionality and experimentation.
- `pytest` for automated testing.

## Installation

Clone the repository and navigate to the project directory.

Create a Python 3.14 virtual environment:

```powershell
py -3.14 -m venv .venv
```

Activate the virtual environment in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the project and its development dependencies:

```powershell
pip install -e ".[dev]"
```

Verify the installation:

```powershell
gitlab-visualizer --version
```

Display the available commands:

```powershell
gitlab-visualizer --help
```

## GitLab API Integration

The application supports read-only communication with GitLab using both the REST API and GraphQL API.

### Implemented Features

- Authentication using a GitLab personal access token.
- Retrieval of authenticated GitLab user information.
- Retrieval of projects associated with the authenticated account.
- Retrieval of individual project information.
- Retrieval of project members, including inherited memberships.
- Retrieval of repository commits and their metadata.
- Pagination for project, member, and commit retrieval.
- Basic handling of authentication, HTTP, and API response errors.
- Execution of authenticated GraphQL queries.
- Automated tests using simulated API responses.

REST is currently used for retrieving project, member, and commit data.

GraphQL is implemented as a separate client with a reusable query execution method and an authenticated user query. Further GraphQL queries can be added when useful for retrieving project relationships.

### GitLab Configuration

Set the GitLab server URL and personal access token using environment variables.

For the University of Szeged's GitLab instance, use the following commands in Windows PowerShell:

```powershell
$env:GITLAB_URL = "https://git-okt.sed.inf.szte.hu"
```

Enter the personal access token securely:

```powershell
$secureToken = Read-Host "Enter GitLab token" -AsSecureString
$env:GITLAB_TOKEN = [System.Net.NetworkCredential]::new("", $secureToken).Password
Remove-Variable secureToken
```

Check whether the token is available without displaying it:

```powershell
-not [string]::IsNullOrWhiteSpace($env:GITLAB_TOKEN)
```

The expected result is `True`.

Use a token with the minimum permissions necessary, such as `read_api`, where supported.

Environment variables set this way are temporary and normally need to be configured again when opening a new PowerShell session.

**Never commit access tokens or private student data to the repository.**

## Command-Line Interface

### Test REST Authentication

```powershell
gitlab-visualizer whoami
```

Displays information about the authenticated GitLab user.

### Test GraphQL Authentication

```powershell
gitlab-visualizer graphql-whoami
```

Retrieves authenticated user information through the GraphQL API.

### List Projects

```powershell
gitlab-visualizer projects
```

Lists projects where the authenticated GitLab account has membership.

### Inspect a Project

```powershell
gitlab-visualizer inspect-project 123
```

Retrieves the members and commits of a selected project.

Replace `123` with an actual numeric GitLab project ID.

### Generate a Demonstration Relationship Graph

```powershell
gitlab-visualizer demo-graph
```

Creates a GraphML relationship graph using sample development data.

### Generate a Demonstration Timeline

```powershell
gitlab-visualizer demo-timeline
```

Creates a weekly activity timeline using sample development data.

### Generate a Real GitLab Relationship Graph

```powershell
gitlab-visualizer real-graph 123
```

Retrieves data from an accessible GitLab project and generates a relationship graph.

The command uses the latest commits returned by the API, displaying up to 10 commits by default.

Customize the number of displayed commits and the output filename:

```powershell
gitlab-visualizer real-graph 123 --max-commits 15 --output project.graphml
```

The maximum number of displayed commits is currently limited to 30.

The relationship graph includes:

- A project node.
- GitLab project member nodes.
- Commit nodes.
- Recorded Git author nodes.
- Project membership relationships.
- Commit-to-project relationships.
- Recorded authorship relationships.

Recorded Git authors are represented separately from GitLab member accounts.

Commit author names and email addresses do not necessarily establish the identity of a GitLab user. Therefore, Git author nodes are labeled as unverified, and the application does not automatically associate commits with project members.

Graph labels are shortened where necessary to improve readability.

### Generate a Real GitLab Weekly Timeline

```powershell
gitlab-visualizer real-timeline 123 --start-date 2026-10-01 --end-date 2026-11-22
```

Replace `123` with a real project ID and adjust the dates to the relevant course period.

The timeline graph:

- Divides the course period into consecutive seven-day weeks.
- Uses commit authored dates normalized to UTC.
- Counts commits within each weekly period.
- Includes weeks with zero recorded commits.
- Connects consecutive weeks chronologically.
- Stores week numbers, date ranges, and commit counts as graph attributes.

The start date determines the beginning of Week 1. Weeks do not necessarily follow calendar Monday-to-Sunday boundaries.

If the end date is omitted, the timeline ends during the week containing the latest qualifying commit, or during the first week if no qualifying commits exist.

The default output file is:

```text
real-timeline.graphml
```

A custom filename can be specified:

```powershell
gitlab-visualizer real-timeline 123 --start-date 2026-10-01 --end-date 2026-11-22 --output timeline.graphml
```

## Graph Visualization with yEd

Graphs are constructed using NetworkX and exported in GraphML format.

The generated files can be opened in yEd Graph Editor.

To inspect a graph:

1. Open yEd Graph Editor.
2. Open the generated `.graphml` file.
3. If node labels are not visible, use **Edit > Properties Mapper**.
4. Map the `label` attribute to the displayed node label.
5. Optionally map the `relationship` attribute to edge labels.
6. Apply **Layout > Hierarchical** to organize the nodes.

For timeline graphs, a left-to-right hierarchical layout is recommended to represent chronological progression.

The relationship graph and timeline graph are intended to provide complementary views of the same project.

## Implementation Notes and Limitations

### GitLab Data

The application currently retrieves repository commits from the project's default branch.

Commits that exist only on other branches might not be included.

The REST client uses pagination to retrieve multiple response pages, with a configured safety limit to prevent uncontrolled requests.

### Author Identification

Git commit author information is not automatically considered proof of GitLab account identity.

Recorded Git author signatures are grouped using their name and email information, but the resulting author nodes remain unverified.

Project members may also include instructors or other users who are not students.

### Activity Interpretation

The weekly timeline describes recorded Git commit activity.

A week without commits does not necessarily mean that no work took place. Students may have been planning, reviewing code, working locally, or contributing through other activities.

Similarly, commit counts should not be interpreted as direct measures of effort, code quality, or individual performance.

The application is intended to **support instructors in understanding project development, not to automate student grading**.

## Testing

The project includes automated unit and integration tests using `pytest`.

Run all tests:

```powershell
pytest -q
```

Run tests with detailed output:

```powershell
pytest -v
```

The test suite covers:

- Python data models.
- GitLab REST and GraphQL communication.
- API authentication and response handling.
- Pagination.
- Project and commit retrieval.
- Relationship graph construction.
- Git author identity separation.
- Weekly timeline generation.
- Inactive weeks and date validation.
- GraphML export and re-import.
- Integration of simulated GitLab responses with graph generation.

Tests use simulated GitLab HTTP responses and do not require continuous access to the university server.

Integration tests verify the process from API responses through internal Python models and NetworkX graphs to exported GraphML files.

## Data Privacy

Generated GraphML files may contain project names, commit metadata, Git author names, and other information related to student projects.

Only retrieve and analyze project information for which access and processing are authorized.

Do not commit or publicly share:

- GitLab personal access tokens.
- Private student information.
- Generated GraphML files containing real project data.
- Other confidential university project information.

Generated `.graphml` files are excluded from version control through `.gitignore`.

## Current Development Status

The following milestones have been completed:

- **Weeks 1–2:** Requirements analysis, preliminary research, and scope definition.
- **Weeks 3–4:** Python project structure, internal data models, initial NetworkX graphs, and CLI development.
- **Weeks 5–6:** GitLab REST and GraphQL integration, authentication, project and commit retrieval, pagination, and automated tests.
- **Weeks 7–8:** Real GitLab relationship graphs, recorded Git author identities, weekly activity timelines, improved graph readability, and GraphML integration tests.

### Planned Next Steps

The next development phase will focus on:

- Computing useful project activity summaries.
- Examining weekly contribution patterns and inactivity periods.
- Improving the visual presentation of project progress.
- Evaluating how the generated graphs can support instructor understanding of student project development.

The primary objective remains the generation of clear, understandable visualizations rather than automated student assessment.