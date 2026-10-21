from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
import json

from database import add_task, get_tasks, complete_task
from assistant import get_assistant_response

HOST = "127.0.0.1"
PORT = 8080


class StudyFlowHandler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        response = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()

        self.wfile.write(response)
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):

        if self.path == "/api/tasks":
            tasks = get_tasks()
            self.send_json(tasks)
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):

        if self.path == "/api/tasks":
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            try:
                data = json.loads(body.decode("utf-8"))

                task = data.get("task", "").strip()
                subject = data.get("subject", "").strip()
                deadline = data.get("deadline", "").strip()

                if not task or not subject:
                    self.send_json(
                        {"error": "Task and subject are required."},
                        400,
                    )
                    return

                task_id = add_task(
                    task=task,
                    subject=subject,
                    deadline=deadline,
                )

                self.send_json(
                    {
                        "message": "Task added successfully.",
                        "id": task_id,
                    },
                    201,
                )

            except Exception as error:
                self.send_json(
                    {"error": str(error)},
                    400,
                )

            return
        if self.path == "/api/assistant":
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            try:
                data = json.loads(body.decode("utf-8"))
                message = data.get("message", "").strip()

                if not message:
                    self.send_json(
                        {"error": "Message is required."},
                        400,
                    )
                    return

                response = get_assistant_response(message)

                self.send_json(
                    {"response": response}
                )

            except Exception as error:
                self.send_json(
                    {"error": str(error)},
                    400,
                )

            return
        if self.path == "/api/tasks/complete":
            content_length = int(
                self.headers.get("Content-Length", 0)
            )

            body = self.rfile.read(content_length)

            try:
                data = json.loads(body.decode("utf-8"))
                task_id = int(data.get("task_id"))

                success = complete_task(task_id)

                if success:
                    self.send_json(
                        {
                            "message": "Task completed successfully."
                        }
                    )
                else:
                    self.send_json(
                        {"error": "Task not found."},
                        404,
                    )

            except Exception as error:
                self.send_json(
                    {"error": str(error)},
                    400,
                )

            return

        self.send_response(404)
        self.end_headers()


def main():
    server = HTTPServer(
        (HOST, PORT),
        StudyFlowHandler,
    )

    print(
        f"StudyFlow web API running at "
        f"http://{HOST}:{PORT}"
    )

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStudyFlow web API stopped.")
        server.server_close()


if __name__ == "__main__":
    main()
