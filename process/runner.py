from rich.console import Console
from multiprocessing.dummy import Pool as Threadpool
from utility.request_openai import openai_request

class RunnerForTranscript:
    def __init__(self):
        self.console = Console()

    def batch_process(self, batches: list) -> list:
        """Processes transcript batches in parallel using threading."""
        item_list = []
        self.console.rule("[bold green] Processing Transcript Batches")

        pool = Threadpool(len(batches))
        batches_output = pool.map(self.extract_info_from_transcript, batches)
        pool.close()
        pool.join()

        for batch_output in batches_output:
            item = {"summary": batch_output}
            item_list.append(item)

        return item_list

    def extract_info_from_transcript(self, transcript: str) -> list:
        """Extracts key information from a given transcript using OpenAI."""
        prompt = """
        I want you to act as a smart meeting notes extractor that extracts information from meeting transcripts. From the below transcript of a conversation or speech, generate the following output for the tasks given:\n\n

        Task - "Summary" - generate a concise summary in bullet points of the main points discussed. The summary should capture the key themes, ideas, and arguments presented in the transcript. Your task is to provide a clear and accurate summary that captures the essence of the transcript and allows the reader to quickly understand the main points without having to read the transcript.\n\n

        Important rules to keep the format in mind:\n
        Task - Summary - A concise summary in bullet points discussed in the transcript.\n
        Transcript:\n
        """

        final_prompt = prompt + transcript + "\n"
        with openai_request(final_prompt, temperature=0.1, max_tokens=1000, frequency_penalty=0, presence_penalty=0) as resp:
            response = resp

        output = response.choices[0].text
        return self.output_batching(output)

    def output_batching(self, input_text: str) -> list:
        """Processes and cleans OpenAI response output."""
        output = (
            input_text.split("Task 2 - Key Insights")[0]
            .strip()
            .replace('Task 1 - Summary', '')
            .replace('Task 1 Summary', '')
            .replace('Summary:', '')
            .strip()
            .replace('-', '')
            .replace('*', '')
            .split('\n')
        )

        return list(set(output))  # Remove duplicates
