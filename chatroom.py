from typing import Annotated, TypedDict
from dotenv import load_dotenv, find_dotenv
import os
import json
from datetime import datetime
import time
import re
import threading
from character import charactor, llm
load_dotenv(find_dotenv())

# =====定义消息类型=====
class Message(TypedDict):
    sender: str
    content: str
    timestamp: str
    thought: str

# =====定义聊天室类=====
class ChatRoom():
    num_charactors = 0
    charactors = []
    participants = []  # 修改为存储更多信息的列表
    chat_round = 0
    chat_record = []
    full_record = []
    chat_background = '''
闲聊群, 随便聊天, 无主题限制.

请注意对话要求：
1. 使用中文交流，不要在回答前加名字和冒号，不要重复之前说过的内容。
2. 参考微信、QQ等社交媒体的聊天记录的发言回复篇幅长短，每次回复在40字以内，保持对话流畅自然和逻辑性。
3. 使用符合当代大学生的日常语言风格，可以自然地使用一些网络用语。
4. 根据你的性格特点、心理状态和日程安排来回应。
5. 敢于开启新话题，可以多个话题并行，随心所欲地聊天。
6. 不要把群聊聊成私聊，如果发现一直和某个人在聊天，请及时调整话题。
'''
    session_id = ""

    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(f"log/{self.session_id}", exist_ok=True)
        self.chat_record = []
        self.full_record = []
        self.participants = []

    def add_charactor(self, charactor):
        self.num_charactors += 1
        self.charactors.append(charactor)
        # 将角色信息（包括日程）添加到 participants
        self.participants.append({
            "name": charactor.name,
            "mbti": charactor.mbti,
            "schedule": {}  # 初始化为空，日程将在 generate_schedule 中填充
        })

    def format_chat_history(self):
        history = ""
        for message in self.chat_record:
            history += f"{message['sender']}: {message['content']}\n"
        return history

    def extract_response_parts(self, message_content):
        decision_match = re.search(r'<decision>(.*?)</decision>', message_content, re.DOTALL)
        decision = decision_match.group(1).strip().lower() if decision_match else "yes"
        think_match = re.search(r'<think>(.*?)</think>', message_content, re.DOTALL)
        thought = think_match.group(1).strip() if think_match else ""
        response_match = re.search(r'<response>(.*?)</response>', message_content, re.DOTALL)
        response = response_match.group(1).strip() if response_match else ""
        return decision, thought, response

    def save_chat_history(self, incremental=False):
        """将聊天历史保存到文件中，包括 participants 中的日程"""
        file_path = os.path.join(f"log/{self.session_id}", f"chat_{self.session_id}.json")
        chat_data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "participants": self.participants,  # 保存每个角色的信息，包括日程
            "background": self.chat_background,
            "messages": self.full_record
        }
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
        if not incremental:
            print(f"\n聊天记录已保存至: {file_path}")
        return file_path

    def start_chat(self, chat_length):
        print("=== 生成每日日程 ===")
        for charactor in self.charactors:
            charactor.generate_schedule()
        print("=== 开始聊天 ===")
        initial_message = {
            "sender": "system",
            "content": "群公告: 欢迎来到香港大学的学生群聊！请同学们畅所欲言，希望大家交到好朋友，度过愉快的时光！刚进群的同学可以自我介绍一下~",
            "timestamp": datetime.now().isoformat()
        }
        self.chat_record.append(initial_message)
        self.full_record.append(initial_message)

        self.chat_round = chat_length
        for charactor in self.charactors:
            charactor.start()
        for charactor in self.charactors:
            charactor.join()
        print("【聊天结束】")
        for charactor in self.charactors:
            charactor.__del__()
        self.save_chat_history(incremental=False)
