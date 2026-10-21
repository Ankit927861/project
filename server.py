import asyncio

from mcp.server.mcpserver import MCPServer

from database import (
    add_task as db_add_task,
    get_tasks,
    complete_task,
)


app = MCPServer(
    name="StudyFlow",
    title="StudyFlow Student Assistant",
    description=(
        "An AI-powered student productivity assistant "
        "for planning, learning, and task management."
    ),
    version="1.0.0",
)


@app.tool()
async def add_task(
    task: str,
    subject: str,
    deadline: str = "",
) -> str:
    """Add a study task and save it permanently."""

    task_id = db_add_task(
        task=task,
        subject=subject,
        deadline=deadline,
    )

    if deadline:
        return (
            f"Task #{task_id} added successfully. "
            f"'{task}' for {subject}. "
            f"Deadline: {deadline}."
        )

    return (
        f"Task #{task_id} added successfully. "
        f"'{task}' for {subject}."
    )


@app.tool()
async def list_tasks() -> str:
    """Show all saved study tasks."""

    tasks = get_tasks()

    if not tasks:
        return "You currently have no study tasks."

    lines = []

    for item in tasks:
        status = "Completed" if item["completed"] else "Pending"
        deadline = item["deadline"] or "No deadline"

        lines.append(
            f"#{item['id']} | "
            f"{item['task']} | "
            f"{item['subject']} | "
            f"{deadline} | "
            f"{status}"
        )

    return "Your study tasks:\n" + "\n".join(lines)


@app.tool()
async def complete_study_task(task_id: int) -> str:
    """Mark a study task as completed."""

    success = complete_task(task_id)

    if success:
        return f"Task #{task_id} has been marked as completed."

    return f"I couldn't find task #{task_id}."


@app.tool()
async def create_study_plan(
    subjects: str,
    available_hours: float,
) -> str:
    """Create a simple study plan."""

    subject_list = [
        item.strip()
        for item in subjects.split(",")
        if item.strip()
    ]

    if not subject_list:
        return "Please provide at least one subject."

    if available_hours <= 0:
        return "Available hours must be greater than zero."

    hours_per_subject = available_hours / len(subject_list)

    plan = [
        f"- {subject}: {hours_per_subject:.1f} hours"
        for subject in subject_list
    ]

    return (
        f"Study plan for {available_hours} hours:\n"
        + "\n".join(plan)
    )


@app.tool()
async def explain_topic(
    topic: str,
    level: str = "beginner",
) -> str:
    """Prepare a learning explanation request."""

    return (
        f"Explain '{topic}' at {level} level. "
        "Start with the basic concept, give a simple example, "
        "and finish with a short practice question."
    )


@app.tool()
async def get_study_advice(subject: str) -> str:
    """Give basic study advice."""

    return (
        f"For {subject}, start with the fundamentals, "
        "study one concept at a time, solve examples, "
        "and finish with a short self-test."
    )


async def main():
    await app.run_streamable_http_async(
        host="127.0.0.1",
        port=8000,
    )


if __name__ == "__main__":
    asyncio.run(main())
