from mcp.server.fastmcp import FastMCP

# StudyFlow - Alexa+ Hackathon Project
# A student productivity assistant exposed through MCP.

mcp = FastMCP(
    "StudyFlow",
    stateless_http=True,
    json_response=True
)


@mcp.tool()
def add_task(task: str, subject: str, deadline: str = "") -> str:
    """
    Add a study task for the student.

    Args:
        task: Name of the task.
        subject: Subject the task belongs to.
        deadline: Optional deadline.
    """
    if deadline:
        return (
            f"Task added successfully: '{task}' "
            f"for {subject}. Deadline: {deadline}."
        )

    return f"Task added successfully: '{task}' for {subject}."


@mcp.tool()
def create_study_plan(
    subjects: str,
    available_hours: float
) -> str:
    """
    Create a simple study plan.

    Args:
        subjects: Comma-separated list of subjects.
        available_hours: Number of hours available.
    """

    subject_list = [
        subject.strip()
        for subject in subjects.split(",")
        if subject.strip()
    ]

    if not subject_list:
        return "Please provide at least one subject."

    hours_per_subject = available_hours / len(subject_list)

    plan = []

    for subject in subject_list:
        plan.append(
            f"{subject}: {hours_per_subject:.1f} hours"
        )

    return (
        f"Study plan for {available_hours} available hours:\n"
        + "\n".join(plan)
    )


@mcp.tool()
def explain_topic(topic: str, level: str = "beginner") -> str:
    """
    Prepare a learning request for a topic.

    Args:
        topic: Topic the student wants to learn.
        level: beginner, intermediate, or advanced.
    """

    return (
        f"StudyFlow received a request to explain '{topic}' "
        f"at {level} level. "
        "The student should receive a simple explanation, "
        "examples, and a short practice question."
    )


@mcp.tool()
def get_study_advice(subject: str) -> str:
    """
    Give basic study advice for a subject.
    """

    return (
        f"For {subject}, start with the fundamentals, "
        "study one concept at a time, solve a few examples, "
        "and finish with a short self-test."
    )


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http"
    )
