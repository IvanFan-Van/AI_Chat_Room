from typing import Annotated, TypedDict
from dotenv import load_dotenv, find_dotenv
import os
import json
from datetime import datetime
import re
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

    你们是大学同学, 你们在学校的教学楼里聊天.
'''
    session_id = ""

    def __init__(self, initial_message=None):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs(f"log/{self.session_id}", exist_ok=True)
        self.chat_record = []
        self.full_record = []
        self.participants = []
        self.initial_message = initial_message if initial_message else {
            "sender": "David",
            "content": "好可怕, 刚刚教学楼爆炸了",
            "timestamp": datetime.now().isoformat()
        }

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
        for message in self.chat_record[-20:]:
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
        initial_message = self.initial_message.copy()
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
