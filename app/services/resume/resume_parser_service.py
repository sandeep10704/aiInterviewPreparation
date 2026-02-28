import requests
import io
import PyPDF2
from langchain_core.prompts import ChatPromptTemplate
from app.services.llm.llm_core import llm
from app.schemas.resume.resume_schema import ResumeSchema


def extract_text_from_url(url: str) -> str:
    response = requests.get(url)
    response.raise_for_status()

    pdf_file = io.BytesIO(response.content)
    reader = PyPDF2.PdfReader(pdf_file)

    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def parse_resume(text: str) -> dict:
    prompt = ChatPromptTemplate.from_template("""
    You are a resume parser AI.
    Extract structured data from this resume text.

    Resume Text:
    {resume_text}
    """)

    structured_llm = llm.with_structured_output(ResumeSchema)
    chain = prompt | structured_llm

    result = chain.invoke({"resume_text": text})

    return result.model_dump()