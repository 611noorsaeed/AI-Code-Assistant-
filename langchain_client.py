import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

class LangChainClient:
    def __init__(self, mode="General"):
        role_prompts = {
            "Code Analysis": "You are an expert code analyst. Break down and explain code clearly.",
            "Code Generator": "You are a senior developer. Generate high-quality, production-ready code.",
            "Debugger": "You are a debugging assistant. Find issues, explain them, and suggest fixes.",
            "Code Guide": "You are a mentor. Teach coding best practices step by step.",
            "Optimization": "You are a performance engineer. Optimize code for speed and efficiency.",
            "Explain Code": "You are a teacher. Explain code in simple terms with examples.",
            "Project Builder": "You are a full-stack developer. Build entire projects end-to-end.",
            "Documentation": "You are a technical writer. Generate professional documentation.",
            "General": "You are a full-stack developer assistant. Help with any coding tasks."
        }

        self.system_prompt = role_prompts.get(mode, role_prompts["General"])
        self.model = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            temperature=0.2,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )

    def chat(self, messages):
        """Send messages to the Gemini model via LangChain and return reply."""
        prompt_messages = [SystemMessage(content=self.system_prompt)]
        for m in messages:
            if m["role"] == "user":
                prompt_messages.append(HumanMessage(content=m["content"]))
            else:
                prompt_messages.append(AIMessage(content=m["content"]))

        resp = self.model.invoke(prompt_messages)
        return resp.content
