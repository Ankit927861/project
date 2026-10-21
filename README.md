# StudyFlow — AI Student Assistant

StudyFlow is a conversational student productivity assistant built for the Amazon Developer Hackathon 2026.

It helps students manage study tasks, create study plans, understand academic topics, and get study advice through a simple web interface powered by an MCP server.

## Features

- Add study tasks with subjects and deadlines
- View saved study tasks
- Mark saved tasks as completed
- Create simple study plans
- Explain academic topics
- Get subject-specific study advice
- Persistent SQLite database
- MCP tools over Streamable HTTP
- Browser-based student assistant interface

## MCP Tools

StudyFlow provides six MCP tools:

- `add_task`
- `list_tasks`
- `complete_study_task`
- `create_study_plan`
- `explain_topic`
- `get_study_advice`

MCP endpoint:

`http://127.0.0.1:8000/mcp`

## Architecture

```text
Web UI
  |
  v
web_app.py
  |
  v
assistant.py
  |
  | MCP Streamable HTTP
  v
server.py
  |
  v
SQLite Database
