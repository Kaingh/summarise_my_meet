from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import JSONResponse
from make_md_file import create_md_file_object
from loguru import logger
from process.process import TranscriptProcessor
import uvicorn

app = FastAPI(
    title="Meeting Summarizer",
    description="This would summarize all your meeting points",
    version=0.1
)

@app.get('/testing')
def testing():
    logger.info("testing...")
    return "Ping Done"

@app.post('/summarize')
async def summarise_the_file(file: UploadFile = File(default=None)):
    file_content = await file.read()
    file_content = str(file_content.decode('utf-8'))
    try:
        processor = TranscriptProcessor()

        # Call the get_transcript method with file content
        output_data = processor.get_transcript(file_content)
        md_content = create_md_file_object(output_data)
    except Exception as e:
        logger.error(f'Error: {str(e)}')
    return {"contents": output_data, "md_content":md_content}


if __name__=="__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)