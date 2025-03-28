from langgraph.graph import Graph, END
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
import random
from typing import Dict, List

# 1. 定义多个聊天参与者
participants = [
    {"name": "Alice", "role": "积极的技术爱好者", "response_prob": 0.7},
    {"name": "Bob", "role": "谨慎的风险分析师", "response_prob": 0.5},
    {"name": "Charlie", "role": "富有创造力的设计师", "response_prob": 0.6}
]

llm = ChatOpenAI(model="Qwen/QwQ-32B", base_url="https://api.siliconflow.cn/v1/chat/completions", api_key="sk-yncwzxixmvfkuoqtgwkaphzzwlkuvbdrkyszjgpewvtxkgjw")

response = llm.invoke("hello")

print(response)