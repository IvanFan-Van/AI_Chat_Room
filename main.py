from typing import Annotated, TypedDict
from dotenv import load_dotenv, find_dotenv
import os
import json
from datetime import datetime
import time
import re
import threading
load_dotenv(find_dotenv())

# =====初始化LLM=====
from langchain_deepseek import ChatDeepSeek
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key="sk-34442cc84ebb4894b2eb884b3a6cd7f1"  # 替换实际密钥
)

# =====定义消息类型=====
class Message(TypedDict):
    sender: str
    content: str
    timestamp: str
    thought: str

# =====定义角色类=====
class charactor(threading.Thread):
    '''角色类:包括名字，mbti，所在聊天室，背景故事，心理活动，日程安排'''
    name = 'undefined'
    mbti = [0.5, 0.5, 0.5, 0.5]
    chatroom = None
    background = 'undefined'
    thoughts = []
    schedule = {}

    def __init__(self, name, mbti, chatroom):
        threading.Thread.__init__(self)
        self.name = name
        self.mbti = mbti
        self.chatroom = chatroom
        self.background = '你是' + self.name + '。'
        self.generate_personality()
        self.thoughts = []
        self.schedule = {}

    def run(self):
        print("【线程开始】", self.name)
        self.chat_multi()
        print("【线程结束】", self.name)

    def __del__(self):
        pass

    def generate_personality(self):
        """根据MBTI生成性格描述"""
        description = ""
        if self.mbti[0] > 0.5:
            description += "你较为外向：你在与他人互动时能快速充电，乐观开朗，擅长在社交场合中表达自我。\n"
        else:
            description += "你较为内向：你倾向于从独处和内省中恢复能量，注重深入思考，显得沉着稳重。\n"
        if self.mbti[1] > 0.5:
            description += "你偏好直觉：你善于捕捉未来趋势和抽象概念，喜欢探索可能性，富有创意和远见。\n"
        else:
            description += "你偏好实感：你注重细节和现实经验，依靠切实的信息做出决策，务实且实际。\n"
        if self.mbti[2] > 0.5:
            description += "你更倾向情感：你在决策时重视情感和人际关系，容易共情，追求和谐与共鸣。\n"
        else:
            description += "你更倾向理性：你依赖分析与逻辑做出判断，擅长客观解决问题，强调事实与效率。\n"
        if self.mbti[3] > 0.5:
            description += "你偏好判断：你喜欢结构化和计划性的生活，注重秩序与明确性，擅长提前规划。\n"
        else:
            description += "你偏好知觉：你灵活自如，乐于接受变化与新鲜事物，倾向于保持选择的开放性。\n"
        basic_info = self.background.split("\n\n")[0]
        self.background = basic_info + "\n\n你的MBTI性格描述：\n" + description + "\n你的思考和言行将会受上述性格特质影响。"

    def generate_schedule(self):
        """生成日程安排，仅存储在 agent 内部和 chatroom.participants 中"""
        system_content = (
            self.background + "\n\n"
            "你是一名香港大学的学生，根据你的MBTI性格特点和兴趣，生成你今天的合理日程安排，要包含你的兴趣。\n"
            "要求：\n"
            "1. 使用24小时制（如 08:00-09:00），时间段不得重叠。\n"
            "2. 每个活动描述控制在20字以内，符合你的性格特点。\n"
            "3. 至少安排3项活动，覆盖上午、下午和晚上。\n"
            "仅返回 JSON 格式结果，不添加任何额外说明，例如：\n"
            "{\n"
            "  \"08:00-09:00\": \"晨跑锻炼\",\n"
            "  \"14:00-16:00\": \"上数学课\",\n"
            "  \"19:00-20:00\": \"晚餐聚会\"\n"
            "}"
        )
        system_message = {"role": "system", "content": system_content}
        messages = [system_message]

        response = llm.invoke(messages)
        response_content = response.content.strip()
        try:
            self.schedule = json.loads(response_content)
        except json.JSONDecodeError:
            print(f"警告：{self.name} 的日程生成失败，使用默认日程")
            self.schedule = {
                "08:00-09:00": "起床和早餐",
                "10:00-12:00": "上课",
                "14:00-16:00": "自习",
                "18:00-19:00": "晚餐"
            }
        print(f"{self.name} 的日程：{json.dumps(self.schedule, ensure_ascii=False, indent=2)}")
        # 将日程存储到 chatroom.participants 中
        for participant in self.chatroom.participants:
            if participant["name"] == self.name:
                participant["schedule"] = self.schedule
                break

    def add_thought(self, thought):
        self.thoughts.append({
            "thought": thought,
            "timestamp": datetime.now().isoformat()
        })

    def chat_multi(self):
        while self.chatroom.chat_round > 0:
            system_content = self.background + "\n" + self.chatroom.chat_background
            system_message = {"role": "system", "content": system_content}
            messages = [system_message]
            history = self.chatroom.format_chat_history()
            user_message = {
                "role": "user",
                "content": (
                    f"目前聊天内容如下\n---\n{history}\n---\n"
                    f"你是{self.name}，你的日程安排如下：\n{json.dumps(self.schedule, ensure_ascii=False)}\n"
                    f"你的思考和言行受MBTI性格特质和日程安排影响。可选择是否回应当前话题。\n"
                    f"请按以下格式回复：\n"
                    f"<decision>yes/no</decision>\n"
                    f"<think>你的思考</think>\n"
                    f"<response>你的回应</response>（不参与则留空）\n"
                    f"回应为中文，40字以内，符合大学生日常语言风格。"
                )
            }
            messages.append(user_message)
            response = llm.invoke(messages)
            response_content = response.content
            decision, thought, chat_response = self.chatroom.extract_response_parts(response_content)

            if self.chatroom.chat_round <= 0:
                break
            self.chatroom.chat_round -= 1

            timestamp = datetime.now().isoformat()
            if decision == "yes" and chat_response.strip():
                self.chatroom.chat_record.append({
                    "sender": self.name,
                    "content": chat_response,
                    "timestamp": timestamp
                })
            full_message = {
                "sender": self.name,
                "content": chat_response if decision == "yes" else "",
                "timestamp": timestamp,
                "thought": thought,
                "decision": decision
            }
            self.chatroom.full_record.append(full_message)

            print()
            print(f"{self.name}: ")
            print(f"  🤔 决定{'参与' if decision == 'yes' else '不参与'}发言")
            if thought:
                print(f"  💭 {thought}")
            if decision == "yes" and chat_response.strip():
                print(f"  🗣️ {chat_response}")

            self.chatroom.save_chat_history(incremental=True)
            time.sleep(1)

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

if __name__ == "__main__":
    chat_room = ChatRoom()
    chat_room.add_charactor(charactor('David', [0.7, 0.6, 0.8, 0.7], chat_room))  # ENFJ
    chat_room.add_charactor(charactor('Emily', [0.6, 0.3, 0.2, 0.8], chat_room))  # ESTJ
    chat_room.add_charactor(charactor('George', [0.2, 0.4, 0.3, 0.3], chat_room)) # ISTP
    chat_room.add_charactor(charactor('Helen', [0.3, 0.2, 0.7, 0.6], chat_room))  # ISFJ
    chat_room.add_charactor(charactor('Ivy', [0.4, 0.8, 0.9, 0.4], chat_room))    # INFP
    chat_room.add_charactor(charactor('Jack', [0.8, 0.4, 0.7, 0.3], chat_room))   # ESFP
    chat_room.add_charactor(charactor('Kelly', [0.9, 0.7, 0.3, 0.2], chat_room))  # ENTP
    chat_room.add_charactor(charactor('Lucy', [0.1, 0.9, 0.2, 0.8], chat_room))   # INTJ
    chat_room.add_charactor(charactor('Alice', [0.8, 0.7, 0.8, 0.4], chat_room))  # ENFP
    chat_room.add_charactor(charactor('Bob', [0.3, 0.4, 0.3, 0.7], chat_room))    # ISTJ
    chat_room.add_charactor(charactor('Charlie', [0.7, 0.3, 0.4, 0.2], chat_room))# ESTP
    chat_room.add_charactor(charactor('Diana', [0.2, 0.8, 0.9, 0.8], chat_room))  # INFJ
    chat_room.add_charactor(charactor('Eve', [0.6, 0.2, 0.8, 0.7], chat_room))    # ESFJ
    chat_room.add_charactor(charactor('Frank', [0.4, 0.6, 0.2, 0.3], chat_room))  # INTP
    chat_room.add_charactor(charactor('Grace', [0.9, 0.9, 0.4, 0.6], chat_room))  # ENTJ
    chat_room.add_charactor(charactor('Henry', [0.1, 0.1, 0.6, 0.1], chat_room))  # ISFP
    chat_room.start_chat(100)