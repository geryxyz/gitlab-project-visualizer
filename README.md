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