from langchain_openai import ChatOpenAI
from app.core.config import settings

class LLMCore:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            api_key=settings.OPENAI_API_KEY,
            base_url=settings.OPENAI_API_BASE,
        )

    def chat(self, messages):
        return self.llm.invoke(messages)

    def with_structured_output(self, schema):
        return self.llm.with_structured_output(schema)

llm = LLMCore()