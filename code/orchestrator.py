from agents.supervisor import run as supervisor_run


class Orchestrator:
    def __init__(self):
        self.last_result = None
        self.last_submission = None

    def run(self, submission: dict, progress_callback=None) -> dict:
        self.last_submission = submission
        self.last_result = supervisor_run(submission, progress_callback=progress_callback)
        return self.last_result


orchestrator = Orchestrator()
