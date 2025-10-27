from services.lang_graph_service import app


class UtilityService:
    def __init__(self) -> None:
        pass

    def format_time(self, seconds: int) -> str:
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f"{m}:{s:02d}"

    def generate_summary(self, path, prompt= ''):
        summary = 'summary not available'
        inputs = {"video_path": path, "prompt": prompt}
        state = app.invoke(inputs)  # type:ignore
        if 'summary' in state:
            summary = state['summary']
        return summary
