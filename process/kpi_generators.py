import time
import re
from utility.request_openai import openai_request
from rich.console import Console
from loguru import logger

class SummaryProcessor:
    def __init__(self):
        self.console = Console()
    
    def summary_l2_generator(self, SUMMARY_BULLETS: str) -> str:
        self.console.rule('[bold red] Summary L2 Processing')
        start_time = time.time()
        BASIC_PROMPT = f"""
        Summary ### 
        {SUMMARY_BULLETS}
        I want you to act as a smart meeting notes extractor that extracts summary from meeting notes.
        Task: Create a short summary of the long summary that captures the most important information in no more than a few sentences.
        Rule: A summary should be in a paragraph.
        Provide the summary in no more than a few sentences.
        """

        with openai_request(BASIC_PROMPT, temperature=0.5, max_tokens=1000) as resp:
            response = resp
        output = response.choices[0].text.strip()
        end_time = time.time()
        logger.warning(f'Summary L2 took {str(round(end_time - start_time, 2))} seconds')
        self.console.rule('[bold red], Summary L2 Completed')
        return output

    def detailed_summary_generator(self, SUMMARY_BULLETS: str):
        self.console.rule('[bold red] Detailed Summary Processing')
        start_time = time.time()
        DETAIL_PROMPT = f"""
        Given a list of summary points, Act as a smart summary extractor to generate a detailed summary only in 2-3 maximum paragraphs.
        Rules:
        The Format of the output:
        {{Paragraph 1
        Paragraph 2
        Paragraph 3 ...}}
        {SUMMARY_BULLETS}
        """

        with openai_request(DETAIL_PROMPT, temperature=0.4, max_tokens=1000) as resp:
            response = resp
        output = response.choices[0].text.strip()
        end_time = time.time()
        logger.warning(f'Detailed Summary Processing took {str(round(end_time - start_time, 2))} seconds')
        self.console.rule('[bold red], Detailed Summary Processing Completed')
        return output
    
    def action_items_generator(self, SUMMARY_BULLETS):
        self.console.rule('[bold red] Action Item Processing')
        start_time = time.time()
        ACTION_PROMPT = f"""
        Given a summary of a transcript from a meeting, generate action items and their respective assignees. (Assignees should be in parentheses and mark it as None if the assignee name is not found.)
        Note: Limit the number of action items to 5-7 points only.
        Summary -
        {SUMMARY_BULLETS}
        """
        
        with openai_request(ACTION_PROMPT, temperature=0.4, max_tokens=1000) as resp:
            response = resp
        output = response.choices[0].text.strip()
        end_time = time.time()
        logger.warning(f'Action Items Processing took {str(round(end_time - start_time, 2))} seconds')
        self.console.rule('[bold red], Action Items Processing Completed')
        
        return [re.sub(r'^[\d+\.\s*]*', "", line).strip() for line in output.split('\n') if line]
    
    def key_insights_generator(self, SUMMARY_BULLETS):
        self.console.rule('[bold red] KI Processing')
        start_time = time.time()
        KI_PROMPT = f"""
        Please generate a summary of:
        {SUMMARY_BULLETS}
        using 5-7 bullet points to highlight key insights and takeaways.
        """
        
        with openai_request(KI_PROMPT, temperature=0.4, max_tokens=1000) as resp:
            response = resp
        output = response.choices[0].text.strip()
        end_time = time.time()
        logger.warning(f'KI Processing took {str(round(end_time - start_time, 2))} seconds')
        self.console.rule('[bold red], KI Processing Completed')
        
        return [line.strip() for line in output.split('*') if line.strip()]
    
    def quotes_generator(self, SUMMARY_BULLETS):
        self.console.rule('[bold red] QUOTES Processing')
        start_time = time.time()
        # QUOTES_PROMPT = f"""
        # Please extract the most significant quotes from the given transcript, limiting your response to 3-5 interesting quotes in bullet points.
        # Note: Generate only 3-5 quotes in the below format:
        # "Quotes": "context for each quote, that explains what was being discussed"
        # Summary -
        # {SUMMARY_BULLETS}
        # """
        QUOTES_PROMPT = f"""
        Extract the **most important** quotes from the meeting transcript.
        - **Limit:** 3-5 quotes only.
        - **Format:**  
        - "**Quote**" - (Brief context explaining its significance)

        **Transcript Summary**:
        {SUMMARY_BULLETS}
        """

        
        with openai_request(QUOTES_PROMPT, temperature=0.4, max_tokens=1000) as resp:
            response = resp
        output = response.choices[0].text.strip()
        end_time = time.time()
        logger.warning(f'QUOTES Processing took {str(round(end_time - start_time, 2))} seconds')
        self.console.rule('[bold red], QUOTES Processing Completed')
        
        return [quote.strip() for quote in re.split(r'\n?\d+\.\s+', output.strip()) if quote]
    
    def metrics_generator(self, SUMMARY_BULLETS):
        self.console.rule('[bold red] METRICS Processing')
        start_time = time.time()
        METRICS_PROMPT = f"""
        Extract key metrics from a summary of a call transcript using natural language processing. Provide a list of only 5-10 most important metrics discussed during the call, along with their corresponding values.
        Use advanced machine learning techniques to identify and extract these metrics from the transcript, and present the results in a clear and concise manner.
        Summary -
        {SUMMARY_BULLETS}
        """
        
        with openai_request(METRICS_PROMPT, temperature=0.4, max_tokens=1000) as resp:
            response = resp
        output = response.choices[0].text.strip()
        end_time = time.time()
        logger.warning(f'METRICS Processing took {str(round(end_time - start_time, 2))} seconds')
        self.console.rule('[bold red], METRICS Processing Completed')
        
        return [line.strip() for line in output.split('\n') if line.strip()]
