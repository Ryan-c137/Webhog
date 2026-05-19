from textual.app import App, ComposeResult
from textual.widgets import ProgressBar, Static
from textual.containers import Horizontal, Vertical
from data_collector import collector

class AIAnalyser(Vertical):
    CSS_PATH = 'gui.tcss'
    collector.start()

    def compose(self) -> ComposeResult:
        with Vertical(classes='panel ai') as ai:
            ai.border_title = 'AI Predictions'

            # Update by self.cache_size, collecting snapshots... 
            yield Static('Waiting for enough snapshots.', classes='collecting_stats')
            yield Static('Collecting data…', classes='collecting_stats')
            yield ProgressBar(total=100, id='collecting_bar', classes='bar collecting_stats', show_eta=False)

            yield Static('Getting respond from server... Needs time...', id='loading')

            # Displaying the score of risk
            yield Static('The Score of Risk:', id='score_label', classes='risk')
            yield Static('0', id='risk_score', classes='risk')
            yield ProgressBar(total=100, id='risk_score_bar', classes='bar risk', show_eta=False)
            yield Static('Reason for potential risks:', id='reason_label', classes='reason')
            yield Static('', id='risk_reason', classes='reason')


    async def on_mount(self):
        self.set_interval(0.5, self.update_info)
        await self.update_info()

    async def update_info(self):

        collecting_bar = self.query_one('#collecting_bar')
        collecting_bar.progress = int(collector.cache_size) * 5
        
        loading = self.query_one('#loading')
        loading.styles.display = 'none' if collector.cache_size < 20 else 'block'

        # Hide this static by checking cache_size
        if(int(collector.risk_score) > -1): 
            for widget in self.query('.collecting_stats'):
                widget.styles.display = 'none'
            # Show query widgets
            for widget in self.query('.risk'):
                widget.styles.display = 'block'

        risk_score = self.query_one('#risk_score')
        risk_score.update(str(collector.risk_score))
        risk_score_bar = self.query_one('#risk_score_bar')
        risk_score_bar.progress = int(collector.risk_score)
        risk_reason = self.query_one('#risk_reason')
        risk_reason.update(str(collector.reason))
        if(int(collector.risk_score) >= 60):
            for widget in self.query('.reason'):
                widget.toggle_class()
        



