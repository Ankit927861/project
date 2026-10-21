import asyncio
import re

from database import add_task, get_tasks, complete_task


# ============================================================
# MCP CONFIGURATION
# ============================================================

MCP_URL = "http://127.0.0.1:8000/mcp"


async def call_mcp_tool(tool_name, arguments):
    """
    Call a StudyFlow MCP tool through Streamable HTTP.
    """

    try:
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client

        async with streamable_http_client(
            MCP_URL
        ) as streams:

            # MCP 2.x in this environment returns 2 streams
            read_stream, write_stream = streams

            async with ClientSession(
                read_stream,
                write_stream,
            ) as session:

                await session.initialize()

                result = await session.call_tool(
                    tool_name,
                    arguments,
                )

                if not result.content:
                    return None

                texts = []

                for item in result.content:
                    if hasattr(item, "text"):
                        texts.append(item.text)
                    else:
                        texts.append(str(item))

                return "\n".join(texts)

    except Exception as error:
        print(
            f"MCP unavailable: "
            f"{type(error).__name__}: {error}"
        )
        return None


def run_mcp_tool(tool_name, arguments):
    """
    Synchronous wrapper for the MCP client.
    """

    try:
        return asyncio.run(
            call_mcp_tool(
                tool_name,
                arguments,
            )
        )

    except Exception as error:
        print(
            f"MCP call failed: "
            f"{type(error).__name__}: {error}"
        )
        return None


# ============================================================
# TASK MANAGEMENT
# ============================================================

def add_task_from_message(message):

    match = re.search(
        r"(?:add|create|remember)\s+"
        r"(?:a\s+)?task[:\s]+(.+)",
        message,
        re.IGNORECASE,
    )

    if not match:
        return None

    task_text = match.group(1).strip()

    subject = "General"
    deadline = ""

    deadline_match = re.search(
        r"\b(?:by|due|deadline)\s+(.+)$",
        task_text,
        re.IGNORECASE,
    )

    if deadline_match:

        deadline = deadline_match.group(1).strip()

        task_text = task_text[
            :deadline_match.start()
        ].strip()

    subject_keywords = {

        "daa": "DAA",
        "dsa": "DSA",
        "dbms": "DBMS",

        "operating system":
            "Operating Systems",

        "operating systems":
            "Operating Systems",

        "os":
            "Operating Systems",

        "computer networks":
            "Computer Networks",

        "cn":
            "Computer Networks",

        "accounts":
            "Accounting",

        "accounting":
            "Accounting",

        "economics":
            "Economics",

        "business studies":
            "Business Studies",

        "finance":
            "Finance",

        "statistics":
            "Statistics",

        "physics":
            "Physics",

        "chemistry":
            "Chemistry",

        "biology":
            "Biology",

        "maths":
            "Mathematics",

        "mathematics":
            "Mathematics",
    }

    lower_task = task_text.lower()

    for keyword, subject_name in subject_keywords.items():

        if keyword in lower_task:

            subject = subject_name
            break

    # MCP first
    mcp_result = run_mcp_tool(
        "add_task",
        {
            "task": task_text.strip(" .,"),
            "subject": subject,
            "deadline": deadline,
        },
    )

    if mcp_result:
        return mcp_result

    # Database fallback
    task_id = add_task(
        task=task_text.strip(" .,"),
        subject=subject,
        deadline=deadline,
    )

    response = (
        f"Done! I added task #{task_id}: "
        f"{task_text.strip(' .,')}."
    )

    if subject != "General":
        response += (
            f" Subject: {subject}."
        )

    if deadline:
        response += (
            f" Deadline: {deadline}."
        )

    return response


def show_tasks():

    # MCP first
    mcp_result = run_mcp_tool(
        "list_tasks",
        {},
    )

    if mcp_result:
        return mcp_result

    # Database fallback
    tasks = get_tasks()

    if not tasks:
        return (
            "You currently have no study tasks."
        )

    response = "Your study tasks:\n\n"

    for task in tasks:

        status = (
            "Completed"
            if task["completed"]
            else "Pending"
        )

        deadline = (
            task["deadline"]
            if task["deadline"]
            else "No deadline"
        )

        response += (
            f"#{task['id']} — "
            f"{task['task']}\n"
            f"Subject: {task['subject']}\n"
            f"Deadline: {deadline}\n"
            f"Status: {status}\n\n"
        )

    return response.strip()


def complete_task_from_message(message):

    match = re.search(
        r"(?:complete|finish|done|finished|mark)\s+"
        r"(?:task\s*)?#?(\d+)",
        message,
        re.IGNORECASE,
    )

    if not match:
        return None

    task_id = int(match.group(1))

    # MCP first
    mcp_result = run_mcp_tool(
        "complete_study_task",
        {
            "task_id": task_id,
        },
    )

    if mcp_result:
        return mcp_result

    # Database fallback
    if complete_task(task_id):

        return (
            f"Great! Task #{task_id} "
            f"is now completed."
        )

    return (
        f"I couldn't find task #{task_id}."
    )


# ============================================================
# STUDY PLANNER
# ============================================================

def create_study_plan(message):

    hour_match = re.search(
        r"(\d+(?:\.\d+)?)\s*"
        r"(?:hours?|hrs?)",
        message.lower(),
    )

    hours = (
        float(hour_match.group(1))
        if hour_match
        else 3
    )

    known_subjects = [

        "DAA",
        "DSA",
        "DBMS",
        "Accounts",
        "Accounting",
        "Economics",
        "Business Studies",
        "Finance",
        "Statistics",
        "Physics",
        "Chemistry",
        "Biology",
        "Mathematics",
    ]

    subjects = []

    lower_message = message.lower()

    for subject in known_subjects:

        if subject.lower() in lower_message:

            subjects.append(subject)

    if not subjects:

        subjects = [
            "Main subject",
            "Revision",
        ]

    # MCP first
    mcp_result = run_mcp_tool(
        "create_study_plan",
        {
            "subjects": ", ".join(subjects),
            "available_hours": hours,
        },
    )

    if mcp_result:
        return mcp_result

    # Local fallback
    time_each = hours / len(subjects)

    response = (
        f"Here is your {hours:g}-hour "
        f"study plan:\n\n"
    )

    for index, subject in enumerate(
        subjects,
        start=1,
    ):

        response += (
            f"{index}. {subject} — "
            f"{time_each:.1f} hours\n"
        )

    response += (
        "\nFinish with 10–15 minutes of "
        "quick revision and self-testing."
    )

    return response


# ============================================================
# OFFLINE KNOWLEDGE BASE
# ============================================================

TOPICS = {

    "recursion": (

        "Recursion is a technique where a "
        "function calls itself to solve a "
        "smaller version of the same problem.\n\n"

        "It has two important parts:\n"
        "1. Base case — stops the recursion.\n"
        "2. Recursive case — solves a smaller problem.\n\n"

        "Example:\n"
        "5! = 5 × 4 × 3 × 2 × 1 = 120.\n\n"

        "Practice: What is 4!?"
    ),

    "stack": (

        "A stack follows LIFO: Last In, First Out.\n\n"

        "Think of a stack of plates. "
        "The last plate placed on top "
        "is removed first.\n\n"

        "Main operations:\n"
        "• Push\n"
        "• Pop\n"
        "• Peek\n\n"

        "Practice: If A, B and C are pushed "
        "in that order, which one is popped first?"
    ),

    "queue": (

        "A queue follows FIFO: First In, First Out.\n\n"

        "Think of people standing in a line.\n\n"

        "Enqueue adds an element.\n"
        "Dequeue removes an element."
    ),

    "binary search": (

        "Binary search finds an element in "
        "sorted data by repeatedly checking "
        "the middle element and eliminating "
        "half of the remaining search space.\n\n"

        "Time complexity: O(log n).\n\n"

        "The data must be sorted."
    ),

    "linked list": (

        "A linked list is made of nodes.\n\n"

        "Each node contains data and a link "
        "to another node.\n\n"

        "Example:\n"
        "Node → Node → Node → NULL"
    ),

    "depreciation": (

        "Depreciation is the systematic allocation "
        "of the cost of a fixed asset over its useful life.\n\n"

        "Example:\n"
        "A machine costs ₹100,000 and has a useful "
        "life of 5 years with no residual value.\n\n"

        "Straight-line depreciation:\n"
        "₹100,000 ÷ 5 = ₹20,000 per year."
    ),

    "opportunity cost": (

        "Opportunity cost is the value of the "
        "next best alternative that you give up "
        "when making a choice.\n\n"

        "Example:\n"
        "If you spend two hours studying instead "
        "of working at a paid job, the income you "
        "could have earned is an opportunity cost."
    ),

    "demand": (

        "Demand is the quantity of a good or "
        "service that consumers are willing "
        "and able to buy at different prices.\n\n"

        "Generally, when price increases, "
        "quantity demanded decreases, assuming "
        "other factors remain unchanged."
    ),

    "supply": (

        "Supply is the quantity of a good or "
        "service that producers are willing "
        "and able to sell at different prices."
    ),

    "compound interest": (

        "Compound interest means interest is "
        "calculated on both the original principal "
        "and previously accumulated interest.\n\n"

        "Formula:\n"
        "A = P(1 + r/n)^(nt)"
    ),

    "mean": (

        "The arithmetic mean is the average "
        "of a set of numbers.\n\n"

        "Formula:\n"
        "Mean = Sum of observations / "
        "Number of observations\n\n"

        "Example:\n"
        "For 2, 4 and 6:\n"
        "Mean = 12/3 = 4."
    ),

    "probability": (

        "Probability measures how likely an "
        "event is to happen.\n\n"

        "For equally likely outcomes:\n"
        "Probability = Favourable outcomes / "
        "Total outcomes\n\n"

        "Its value lies between 0 and 1."
    ),

    "photosynthesis": (

        "Photosynthesis is the process by which "
        "green plants use light energy to convert "
        "carbon dioxide and water into glucose "
        "and oxygen.\n\n"

        "Chlorophyll plays an important role "
        "in capturing light energy."
    ),

    "newton's laws": (

        "Newton's laws describe the relationship "
        "between force and motion.\n\n"

        "First law: An object maintains its state "
        "of motion unless acted on by an external "
        "net force.\n\n"

        "Second law: F = ma.\n\n"

        "Third law: Forces occur in equal and "
        "opposite pairs."
    ),
}


def explain_topic(topic):

    topic = topic.strip()

    lower = topic.lower()

    # Local knowledge
    if lower in TOPICS:

        return TOPICS[lower]

    for key, explanation in TOPICS.items():

        if key in lower or lower in key:

            return explanation

    # Unknown topic → MCP
    mcp_result = run_mcp_tool(
        "explain_topic",
        {
            "topic": topic,
            "level": "beginner",
        },
    )

    if mcp_result:

        return mcp_result

    return (

        f"Here's a structured way to learn "
        f"'{topic}':\n\n"

        f"1. Definition — understand what "
        f"{topic} means.\n"

        f"2. Core idea — identify its "
        f"main principle.\n"

        f"3. Example — connect it to a "
        f"real situation.\n"

        f"4. Application — see where it is used.\n"

        f"5. Practice — solve one basic question."
    )


# ============================================================
# MAIN ASSISTANT
# ============================================================

def get_assistant_response(message):

    message = message.strip()

    if not message:

        return (
            "How can I help you with your studies?"
        )

    lower = message.lower()

    # Add task
    result = add_task_from_message(message)

    if result:

        return result

    # Complete task
    result = complete_task_from_message(message)

    if result:

        return result

    # Show tasks
    if (

        "show my task" in lower
        or "show tasks" in lower
        or "list tasks" in lower
        or "my assignments" in lower
        or "pending task" in lower

    ):

        return show_tasks()

    # Study plan
    if (

        "study plan" in lower
        or "study schedule" in lower

    ):

        return create_study_plan(message)

    # Explain
    explain_match = re.search(

        r"^\s*(?:please\s+)?"
        r"explain\s+(.+)",

        message,

        re.IGNORECASE,
    )

    if explain_match:

        return explain_topic(
            explain_match.group(1)
        )

    # What is / define
    define_match = re.search(

        r"^\s*(?:what is|what are|define)\s+"
        r"(.+?)[?.]?$",

        message,

        re.IGNORECASE,
    )

    if define_match:

        return explain_topic(
            define_match.group(1)
        )

    # Direct topic
    for topic in TOPICS:

        if topic in lower:

            return explain_topic(topic)

    # Help
    if (

        "help" in lower
        or "what can you do" in lower

    ):

        return (

            "I'm StudyFlow, your AI student assistant.\n\n"

            "I can:\n"
            "• Manage study tasks\n"
            "• Create study plans\n"
            "• Complete tasks\n"
            "• Explain academic topics\n"
            "• Help with CSE, Commerce, Science and Maths\n\n"

            "Try:\n"
            "• Explain depreciation\n"
            "• Explain recursion\n"
            "• Show my tasks\n"
            "• Complete task 2\n"
            "• Make a 3 hour study plan "
            "for Accounts and Economics"
        )

    # Default
    return (

        "I can help you with studies, "
        "tasks and study planning.\n\n"

        "Try:\n"
        "• Explain depreciation\n"
        "• Explain recursion\n"
        "• Show my tasks\n"
        "• Complete task 2\n"
        "• Make a 3 hour study plan "
        "for Accounts and Economics"
    )
