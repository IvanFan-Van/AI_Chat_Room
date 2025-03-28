import requests
import os
from enum import Enum

class Model(Enum):
    DeepSeekR1 = "deepseek-ai/DeepSeek-R1"
    DeepSeekV3 = "deepseek-ai/DeepSeek-V3"
    DistilDeepSeekR1 = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"


def response(model, messages):
    url = "https://api.siliconflow.cn/v1/chat/completions"

    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "stop": None,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "frequency_penalty": 0.5,
        "n": 1,
        "response_format": {"type": "text"},
    }
    headers = {
        "Authorization": f"Bearer sk-yncwzxixmvfkuoqtgwkaphzzwlkuvbdrkyszjgpewvtxkgjw",
        "Content-Type": "application/json"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    response = response.json()

    content = response["choices"][0]["message"]["content"]
    reasoning = response["choices"][0]["message"]["reasoning_content"]

    return content, reasoning


if __name__ == "__main__":
    content, reasoning = response(Model.DeepSeekR1.value, [{
        "role": "system",
        "content": "你是ENFT性格的角色, 你的特点是活泼外向，想象力丰富。你是一个大学生, 正在大学群里和其他同学聊天。请根据你的性格特点在群内发言"
    }, {
        "role": "user",
        "content": "这是当前的聊天记录\n---\n[1] 王五: 有人打GTA5嘛\n---\n当前你的情绪：较高, 剩余精力：0.8。如果精力低于0.3或情绪低落，你可能更倾向于不参与讨论。你是Alice。请根据你的性格特质，自行判断是否要对当前话题做出回应。如果你认为当前话题值得你参与，请使用<decision>yes</decision>并在<response>中回应。如果你认为当前话题不适合你参与，请使用<decision>no</decision>，并在<think>中解释原因。每次回应都要真实反映你的MBTI性格特点。"
    }])

    print("reasoning: ", reasoning)
    print(content)
    