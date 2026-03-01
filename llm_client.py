import json, re
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

class LLMClient:
    def __init__(self, model: str, base_url: str, temperature: float, options: dict, format_json: bool = False):
        kwargs = dict(model=model, base_url=base_url, temperature=temperature, options=options)
        if format_json:
            kwargs["format"] = "json"
        self.llm = ChatOllama(**kwargs)

    def ask_json(self, system_prompt: str, user_prompt: str) -> dict:
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
        out = self.llm.invoke(messages).content.strip()

        # tenta extrair o maior bloco JSON
        m = re.search(r"\{.*\}", out, flags=re.S)
        if not m:
            raise ValueError(f"LLM did not return JSON. Raw:\n{out}")
        raw = m.group(0)

        # correções comuns (trailing comma)
        raw = re.sub(r",\s*}", "}", raw)
        raw = re.sub(r",\s*]", "]", raw)

        return json.loads(raw)