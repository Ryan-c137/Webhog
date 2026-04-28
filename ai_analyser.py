from textual.app import App, ComposeResult
from textual.widgets import ProgressBar, Static
from textual.containers import Horizontal, Vertical

class AIAnalyser(Vertical):
    CSS_PATH = 'gui.tcss'

    def compose(self) -> ComposeResult:
        with Vertical(classes='panel ai') as ai:
            ai.border_title = 'AI Predictions'
            yield Static('[ your AiDisplay widget goes here ]')