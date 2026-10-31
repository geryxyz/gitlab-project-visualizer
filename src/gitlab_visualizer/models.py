from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Student:
    id: int
    username: str
    name: str


@dataclass(frozen=True)
class Project:
    id: int
    name: str
    path_with_namespace: str
    web_url: str


@dataclass(frozen=True)
class Commit:
    id: str
    short_id: str
    title: str
    author_name: str
    author_email: str
    authored_date: datetime
    committed_date: datetime
    project_id: int