import time, re, openai, tiktoken
from rich.console import Console
from loguru import logger
from multiprocessing.dummy import Pool as Threadpool
from utility.request_openai import openai_request
from dotenv import load_dotenv
load_dotenv()

console = Console()

def get_transcript(script:str):
    start_time = time.time()
    pattern_1 = r'\d{2}:\d{2}:\d{2}'
    scentence = []
    if len(script.split("\n"))>5:
        for line in script.split("\n"):
            if "-->" in line or ("/" in line and "-" in line):
                continue
            else:
                line = re.sub(pattern_1, "", line)
                line = line.replace('</v>','')
                line = line.split('>')[-1]
                scentence.append(line.strip())
            transcript = " ".join(scentence).replace(" "," ")
    else:
        transcript=script
    batches = get_batches(transcript)
    console.rule()
    logger.info(f'{len(batches)} BATCHES DIVIDED FOR THE TRANSCRIPT.')

    data = batch_process(batches)
    formatted_data = format_data(data)
    end_time = time.time()
    logger.info("Total time taken to generate notes from the transcript: ",{str(round(end_time-start_time))})
    console.rule()
    return formatted_data


def string_token_count(string: str) -> int:
    encoding = tiktoken.get_encoding("gpt2")
    num_token = len(encoding.encode(string))
    return num_token

def get_batches(transcript:str):
    """
    Input -> Transcript String
    Output -> List of strings- where each steing is less than or equal to 2000 characters
    """
    batches = []
    final_text = ""
    for line in transcript.split(". "):
        line+= ". "
        if string_token_count(final_text)<=2000:
            final_text += line
        else:
            batches.append(final_text)
            final_text = line
    if final_text not in batches:
        batches.append(final_text)
    return batches

def output_batching(input:str):
    output = input.split("Task 2 - Key Insights")[0].strip().replace('Task 1 - Summary','').replace('Task 1 Summary','').replace('Summary:','').strip().replace('-','').replace('*','').split('\n')
    result = list(set(output))
    return result

def extract_info_from_transcript(transcript)-> str:
    PROMPT = """
        I want you to act as a smart meeting notes extractor that extracts information from meeting transcripts. From the below transcript of a conversation or speech, generate the following output for the tasks fiven-\n\n

        Task - "Summary" - generate a concise summary in the bullet points of the main points discussed. The summary should capture the key themes, ideas, and arguments presented in the transcript. Your task is to provide a clear and accurate summary that captures the essence of the transcript and allows the reader to quickly understand the main points without having to read the transcript.\n\n

        Important rules to keep the format in mind\n
        Task - Summary - A concise summary in byllet points discussed in the transcript.\n
        Transcript:\n
    """

    FINAL_PROMPT = PROMPT+transcript+"\n"
    with openai_request(FINAL_PROMPT, temperature=0.1, max_tokens=1000, frequency_penalty=0, presence_penalty=0) as resp:
        response =resp
    output = response.choices[0].text
    output = output_batching(output)
    return output

def batch_process(batches:list):
    item_list = []
    console.rule()
    pool = Threadpool(len(batches))
    batches_output = pool.map(extract_info_from_transcript, batches)
    pool.close()
    pool.join()

    for batch_output in batches_output:
        item ={}
        item["summary"] = batch_output
        item_list.append(item)
    return item_list


def format_data(data_list: list):
    summary = []
    item = {}
    for output in data_list:
        for i in output['summary']: summary.append(i)
    temp = []
    for i in summary:
        temp.append("*"+i+"/n")
    console.rule('[bold red!] Bullet Points Summary')
    SUMMARY_BULLETS = "".join(temp)
    console.rule()

    l2_summary = summary_l2_generator(SUMMARY_BULLETS)
    detailed_output = detailed_summary_generator(SUMMARY_BULLETS)
    action_points = action_items_generator(SUMMARY_BULLETS)
    key_insights = key_insights_generator(SUMMARY_BULLETS)
    quotes = quotes_generator(SUMMARY_BULLETS)
    kpi_matrices = matrics_generator(SUMMARY_BULLETS)

    item["l2_summary"]          = l2_summary
    item["detailed_output"]     = detailed_output
    item["action_points"]       = action_points
    item["key_insights"]        = key_insights
    item["quotes"]              = quotes
    item["kpi_matrices"]        = kpi_matrices

    return item

def summary_l2_generator(SUMMARY_BULLETS:str)-> str:
    console.rule('[bold red] Summary L2 Processing')
    start_time = time.time()
    BASIC_PROMPT = "Summary ### \n" + SUMMARY_BULLETS + "\n" + """
    I want you to act as a smart meeting notes etractor that extracts summary from meeting notes.\n
    Task: Create a short summary of the long summary that captures the most important information in no more than a few scentences. \n
    Rule: A summary should be in a paragraph. \n
    Povide the summary in no more than few scentences-\n
    """

    with openai_request(BASIC_PROMPT, temperature=0.5, max_tokens=1000) as resp:
        response = resp
    output = response.choices[0].text.strip()
    end_time = time.time()
    logger.warning(f'Summary L2 took {str(round(end_time-start_time,2))} seconds')
    console.rule('[bold red], Summary L2 Completed')
    return output


def detailed_summary_generator(SUMMARY_BULLETS:str):

    console.rule('[bold red] Detailed Summary Processing')
    start_time = time.time()
    DETAIL_PROMPT = """
    Given a list of summary points, Act as a smart summary extractor to generate detailed summary only in 2-3 maximum paragraphs.\n
    Rules:\n
    The Format of the output-\n
    {Paragraph 1\n
    Paragraph 2\n
    Paragraph 3 ...}\n
    """

    DETAIL_PROMPT = DETAIL_PROMPT+ SUMMARY_BULLETS + "\n"
    with openai_request(DETAIL_PROMPT, temperature=0.4, max_tokens=1000) as resp:
        response = resp
    output = response.choices[0].text.strip()
    end_time = time.time()
    logger.warning(f'Detailed Summary Processing took {str(round(end_time-start_time,2))} seconds')
    console.rule('[bold red], Detailed Summary Processing Completed')
    return output

def action_items_generator(SUMMARY_BULLETS):
    console.rule('[bold red] Action Item Processing')
    start_time = time.time()
    ACTION_PROMPT = """" 
    Given a summary of a transcript from a meeting, Generate action items and their respective assignees. (Asignees should be in paranthesis and mark it as None, if the assignee name is not found.)\n
    Note: Limit the number of action items in 5-7 points only.\n
    Summary -\n
    """
    ACTION_PROMPT = ACTION_PROMPT + SUMMARY_BULLETS + "\n"
    with openai_request(ACTION_PROMPT, temperature=0.4, max_tokens=1000) as resp:
        response = resp
    output = response.choices[0].text.strip()
    end_time = time.time()
    logger.warning(f'Action Items Processing took {str(round(end_time-start_time,2))} seconds')
    console.rule('[bold red], Action Items Processing Completed')
    action_points = []
    bullet_pattern = r'^[\d+\.\s*]*'
    if "Action Items:" in output:
        splitter = output.split('\n')[1:]
    else:
        splitter = output.split('\n')
    for t in splitter:
        if len(t) >1:
            action_points.append(re.sub(bullet_pattern, "", t, flags=re.MULTILINE).strip())
    
    return action_points

def key_insights_generator(SUMMARY_BULLETS):
    console.rule('[bold red] KI Processing')
    start_time = time.time()
    KI_PROMPT = f"""" 
    Please generate a summary of -\n
    {SUMMARY_BULLETS}\n 
    using <5-7 bullet points> to highlight key insights and takeaways.\n
    """

    with openai_request(KI_PROMPT, temperature=0.4, max_tokens=1000) as resp:
        response = resp
    output = response.choices[0].text.strip()
    end_time = time.time()
    logger.warning(f'KI Processing took {str(round(end_time-start_time,2))} seconds')
    console.rule('[bold red], KI Processing Completed')
    text = output.strip().replace('Key Insights/Takeways:',"").strip()
    key_insights = []
    for t in text.split('-')[1:]:
        key_insights.append(t.strip())
    return key_insights

def quotes_generator(SUMMARY_BULLETS):
    console.rule('[bold red] QUOTES Processing')
    start_time = time.time()
    QUOTES_PROMPT = """"
    Please extract the most significant quotes from the given transcript, limiting your response to 3-5 interesting quotes in bullet points
    Note: Generate only 3-5 quotes in the below format-\n
    "Quotes": "context for each quote, that explains what was being discussed"\n
    Summary - \n
    """
    QUOTES_PROMPT = QUOTES_PROMPT + SUMMARY_BULLETS + "\n"
    with openai_request(QUOTES_PROMPT, temperature=0.4, max_tokens=1000) as resp:
        response = resp
    output = response.choices[0].text.strip()
    end_time = time.time()
    logger.warning(f'QUOTES Processing took {str(round(end_time-start_time,2))} seconds')
    console.rule('[bold red], QUOTES Processing Completed')
    entries = re.split(r'\n?\d+\.\s+', output.strip())
    entries = [e for e in entries if e]
    
    return entries

def matrics_generator(SUMMARY_BULLETS):
    console.rule('[bold red] METRICES Processing')
    start_time = time.time()
    METRICS_PROMPT = """
    Extract key metrics from a summary of a call transcript using natural language processing. Provide a list of only 5-10 most important metrics discussed during the call, along with their corresponding values. \n\n
    Use advanced nachine learning techniques to identify and extract these metrics from the transcript, and present the results in a clear and consice manner.\n\n
    Summary -\n
    """

    METRICS_PROMPT = METRICS_PROMPT + SUMMARY_BULLETS + '\n'
    with openai_request(METRICS_PROMPT, temperature=0.4, max_tokens=1000) as resp:
        response = resp
    output = response.choices[0].text.strip()
    end_time = time.time()
    logger.warning(f'METRICS Processing took {str(round(end_time-start_time,2))} seconds')
    console.rule('[bold red], METRICS Processing Completed')

    metrics = []
    bullet_pattern = r'^\d+[\.\s]*|.\s*'
    if 'Metrics:' in output:
        splitter = output.split('\n')
    else:
        splitter = output.split('\n')
    
    for t in splitter:
        if len(t) > 1:
            metrics.append(t.strip())
    
    return metrics