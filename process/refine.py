import re
import tiktoken
from multiprocessing.dummy import Pool as Threadpool
from rich.console import Console

class RefineTranscript:
    def __init__(self):
        self.console = Console()
        self.token_encoder = tiktoken.get_encoding("gpt2")

    def clean_transcript(self, script: str) -> str:
        """Removes timestamps, unnecessary tags, and cleans transcript text."""
        pattern_1 = r'\d{2}:\d{2}:\d{2}'
        sentences = []

        if len(script.split("\n")) > 5:
            for line in script.split("\n"):
                if "-->" in line or ("/" in line and "-" in line):
                    continue
                else:
                    line = re.sub(pattern_1, "", line)
                    line = line.replace('</v>', '')
                    line = line.split('>')[-1]
                    sentences.append(line.strip())

            transcript = " ".join(sentences).replace("  ", " ")
        else:
            transcript = script
        return transcript

    def string_token_count(self, text: str) -> int:
        """Counts the number of tokens in a string using GPT-2 encoding."""
        return len(self.token_encoder.encode(text))

    def get_batches(self, transcript: str, max_tokens: int = 2000) -> list:
        """
        Splits the transcript into batches where each batch is ≤ max_tokens.
        Default batch size: 2000 tokens.
        """
        batches = []
        final_text = ""

        for line in transcript.split(". "):
            line += ". "  # Ensure proper sentence ending
            if self.string_token_count(final_text) <= max_tokens:
                final_text += line
            else:
                batches.append(final_text)
                final_text = line

        if final_text not in batches:
            batches.append(final_text)

        return batches
