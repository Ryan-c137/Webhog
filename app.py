from textual.app import App, ComposeResult
from textual.widgets import Footer, Header, Static
from textual.containers import Horizontal, Vertical
from system_info_display import SystemInfoDisplay
from ports_processes import PortsSockets
from ai_analyser import AIAnalyser


class WebHog(App):

    CSS_PATH = "gui.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        yield SystemInfoDisplay()
        with Horizontal(id='bottom-row'):
            yield PortsSockets()
            yield AIAnalyser()


if __name__ == "__main__":
    app = WebHog()
    app.run()
