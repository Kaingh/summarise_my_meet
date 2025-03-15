import time
from rich.console import Console
from loguru import logger
from process.kpi_generators import SummaryProcessor
from process.refine import RefineTranscript
from process.runner import RunnerForTranscript
from dotenv import load_dotenv
load_dotenv()

console = Console()

class TranscriptProcessor:
    def __init__(self):
        self.console = console
    
    def get_transcript(self, script: str):
        start_time = time.time()
        refine = RefineTranscript()
        runner = RunnerForTranscript()

        # Clean transcript
        transcript = refine.clean_transcript(script)

        # Split transcript into batches
        batches = refine.get_batches(transcript)
        self.console.rule()
        logger.info(f'{len(batches)} BATCHES DIVIDED FOR THE TRANSCRIPT.')

        # Process batches in parallel
        data = runner.batch_process(batches)

        # Format processed data
        formatted_data = self.format_data(data)

        end_time = time.time()
        logger.info(f"Total time taken to generate notes from the transcript: {round(end_time - start_time)} seconds")
        self.console.rule()
        
        return formatted_data

    def format_data(self, data_list: list):
        summary = []
        item = {}

        for output in data_list:
            for i in output['summary']: 
                summary.append(i)
        
        temp = []
        for i in summary:
            temp.append("* " + i + "\n")

        self.console.rule('[bold red!] Bullet Points Summary')
        SUMMARY_BULLETS = "".join(temp)
        self.console.rule()

        gen = SummaryProcessor()
        item["l2_summary"] = gen.summary_l2_generator(SUMMARY_BULLETS)
        item["detailed_output"] = gen.detailed_summary_generator(SUMMARY_BULLETS)
        item["action_points"] = gen.action_items_generator(SUMMARY_BULLETS)
        item["key_insights"] = gen.key_insights_generator(SUMMARY_BULLETS)
        item["quotes"] = gen.quotes_generator(SUMMARY_BULLETS)
        item["kpi_matrices"] = gen.metrics_generator(SUMMARY_BULLETS)

        return item
