from typing import Annotated, TypedDict
from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
import os
import json
from datetime import datetime
import time
import re

load_dotenv(find_dotenv()) # 加载环境变量, 使用langsmith监控

LOG_FOLDER = Path("./frontend/log") # 日志文件夹

#=====初始化LLM=====
from langchain_deepseek import ChatDeepSeek
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key="sk-34442cc84ebb4894b2eb884b3a6cd7f1"  # 替换实际密钥
)

# =====定义消息类型=====
class Message(TypedDict):
    sender: str
    content: str    # 实际对话内容（response部分）
    timestamp: str  # 添加时间戳
    thought: str    # 内心想法（think部分），对其他角色不可见

#=====定义角色类=====
class charactor():
    '''角色类:包括名字，mbti，背景故事，心理活动'''
    name = 'undefined'
    mbti = [0.5, 0.5, 0.5, 0.5] #1/0 1st: E/I, 2nd: N/S, 3rd: F/T, 4th: J/P
    background = 'undefined'
    
    def __init__(self, name, mbti):
        self.name = name
        self.mbti = mbti
        self.background = '你是' + self.name + '。'
        self.generate_personality()
        
    # TODO 添加更多属性, 丰富性格特征描述, 添加程度描述
    def generate_personality(self):
        """根据MBTI重新生成更加完整且符合实际的MBTI性格描述"""
        description = ""
        # Extraversion vs. Introversion
        if self.mbti[0] > 0.5:
            description += "你较为外向：你在与他人互动时能快速充电，乐观开朗，擅长在社交场合中表达自我。\n"
        else:
            description += "你较为内向：你倾向于从独处和内省中恢复能量，注重深入思考，显得沉着稳重。\n"
        # Sensing vs. Intuition
        if self.mbti[1] > 0.5:
            description += "你偏好直觉：你善于捕捉未来趋势和抽象概念，喜欢探索可能性，富有创意和远见。\n"
        else:
            description += "你偏好实感：你注重细节和现实经验，依靠切实的信息做出决策，务实且实际。\n"
        # Feeling vs. Thinking
        if self.mbti[2] > 0.5:
            description += "你更倾向情感：你在决策时重视情感和人际关系，容易共情，追求和谐与共鸣。\n"
        else:
            description += "你更倾向理性：你依赖分析与逻辑做出判断，擅长客观解决问题，强调事实与效率。\n"
        # Judging vs. Perceiving
        if self.mbti[3] > 0.5:
            description += "你偏好判断：你喜欢结构化和计划性的生活，注重秩序与明确性，擅长提前规划。\n"
        else:
            description += "你偏好知觉：你灵活自如，乐于接受变化与新鲜事物，倾向于保持选择的开放性。\n"
        
        # 更新背景信息中的性格描述部分
        basic_info = self.background.split("\n\n")[0]
        self.background = basic_info + "\n\n你的MBTI性格描述：\n" + description + "\n在对话中请体现上述性格特质。"
        self.background += (
            "\n\n你不必对每一个话题都做出回应。根据你的性格特点，评估当前话题是否值得你参与回应。"
            "\n每一次活动请按照以下格式回复："
            "\n1. 首先，决定你是否要对当前话题发表回应："
            "\n   - 使用 <decision>yes</decision> 表示你决定参与这个话题"
            "\n   - 使用 <decision>no</decision> 表示你决定不参与这个话题"
            "\n2. 然后，无论你决定是否参与，都需要解释你的决定理由："
            "\n   - 使用 <think>你的想法</think> 包裹你的内心活动或思考过程，说明你为何决定参与或不参与"
            "\n3. 如果你决定参与，请提供你的回应："
            "\n   - 使用 <response>你的回应</response> 包裹你要在群里说的话"
            "\n如果你决定不参与，则无需填写<response>部分"
        )


# =====定义聊天室类=====  
class ChatRoom():
    '''聊天室类:包括角色列表，当前对话记录'''
    num_charactors = 0
    charactors = []
    chat_record = [] # 公开的对话记录（其他角色可见的部分）
    full_record = [] # 完整的记录, 包含内心活动部分

    # 背景设定
    chat_background = '''
你是一名大学生，刚刚加入XXX大学的学生群。这个群聊中有来自不同专业、不同年级的同学。
聊天内容可能包括：课业学习、校园生活、社团活动、兴趣爱好、最近热门话题等。

在对话中请注意：
1. 使用符合当代大学生的日常语言风格，可以自然地使用一些网络用语
2. 使用中文交流，不要在回答前加名字和冒号
3. 不要重复之前已经说过的内容
4. 根据你的性格特点、心理状态和日程安排来回应
5. 每次回复不超过50字，保持对话流畅自然
'''
    session_id = ""
    
    def __init__(self, session_id=None):
        # 创建一个唯一的会话ID，基于时间戳
        if not session_id:
            self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        else:
            self.session_id = session_id
        
        # 创建日志文件夹
        log_folder = LOG_FOLDER / f"{self.session_id}"
        log_folder.mkdir(parents=True, exist_ok=True)

        # 初始化角色和对话记录
        self.chat_record = []
        self.full_record = []


    def add_charactor(self, charactor):
        self.num_charactors += 1
        self.charactors.append(charactor)

    def format_chat_history(self):
        """Format the chat history for the prompt."""
        history = ""
        for message in self.chat_record:
            history += f"{message['sender']}: {message['content']}\n"
        return history
    
    def extract_response_parts(self, message_content):
        """从消息内容中提取决策、思考和回应部分"""
        # 提取决策部分
        decision_match = re.search(r'<decision>(.*?)</decision>', message_content, re.DOTALL)
        decision = decision_match.group(1).strip().lower() if decision_match else "yes"  # 默认为参与
        
        # 提取思考部分
        think_match = re.search(r'<think>(.*?)</think>', message_content, re.DOTALL)
        thought = think_match.group(1).strip() if think_match else ""
        
        # 提取回应部分
        response_match = re.search(r'<response>(.*?)</response>', message_content, re.DOTALL)
        response = response_match.group(1).strip() if response_match else ""
        
        return decision, thought, response

    def save_chat_history(self, incremental=False):
        """将聊天历史保存到文件中
        
        Args:
            incremental: 如果为True，表示这是增量更新而不是完整保存
        """
        file_path = LOG_FOLDER / f"{self.session_id}" / f"chat_{self.session_id}.json"
        
        # 准备要保存的数据
        chat_data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "participants": [char.name for char in self.charactors],
            "background": self.chat_background,
            "messages": self.full_record
        }
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
        
        if not incremental:
            print(f"\n聊天记录已保存至: {file_path}")
        
        return file_path

    def start_chat(self, chat_length):
        initial_message = {
            "sender": "system",
            "content": "群公告: 欢迎来到XXX大学的学生群聊！请随意讨论任何话题，保持友好交流。希望大家在这里度过愉快的时光！请刚进群的同学自我介绍一下。",
            "timestamp": datetime.now().isoformat()
        }
        self.chat_record.append(initial_message)
        self.full_record.append(initial_message)

        for i in range(chat_length):
            print("[%d]" % (i+1))

            for charactor in self.charactors:
                """构建系统消息 (角色设定 + 聊天背景) """
                system_content = charactor.background + "\n" + self.chat_background
                system_message = {"role": "system", "content": system_content}

                """构建 message 列表"""
                messages = [system_message]

                """构建对话历史"""
                history = self.format_chat_history()

                """构建用户消息"""
                user_message = {
                    "role": "user", 
                    "content": (
                        f"目前聊天内容如下\n---\n{history}\n---\n"
                        f"你是{charactor.name}。请根据你的性格特质，自行判断是否要对当前话题做出回应。\n"
                        f"如果你认为当前话题值得你参与，请使用<decision>yes</decision>并在<response>中回应。\n"
                        f"如果你认为当前话题不适合你参与，请使用<decision>no</decision>，并在<think>中解释原因。\n"
                        f"每次回应都要真实反映你的MBTI性格特点。"
                    )
                }
                messages.append(user_message)
    
                """获取回复"""
                response = llm.invoke(messages)
                response_content = response.content

                """处理回复，提取决策、思考和回应部分"""
                decision, thought, chat_response = self.extract_response_parts(response_content)

                """更新对话历史，添加时间戳"""
                timestamp = datetime.now().isoformat()

                if decision == "yes" and chat_response.strip():
                    self.chat_record.append({
                        "sender": charactor.name, 
                        "content": chat_response, 
                        "timestamp": timestamp
                    })

                """添加完整记录（包括决策、思考和回应）"""
                full_message = {
                    "sender": charactor.name,
                    "content": chat_response if decision == "yes" else "",
                    "timestamp": timestamp,
                    "thought": thought,
                    "decision": decision
                }
                self.full_record.append(full_message)

                """打印输出，包括决策、思考和回应"""
                print(f"{charactor.name}: ")
                print(f"  🤔 决定{'参与' if decision == 'yes' else '不参与'}这个话题")
                if thought:
                    print(f"  💭 {thought}")  # 思考
                
                if decision == "yes" and chat_response.strip():
                    print(f"  🗣️ {chat_response}")  # 发言
                
                # 每次角色回复后立即更新聊天记录
                self.save_chat_history(incremental=True)
        
        # 聊天结束后，执行最终保存并显示提示信息
        self.save_chat_history(incremental=False)

       
if __name__ == "__main__":
    chat_room = ChatRoom()
    # 增加更多角色信息
    chat_room.add_charactor(charactor('Alice', [0.8, 0.7, 0.8, 0.4]))  # ENFP - 活泼外向，想象力丰富
    chat_room.add_charactor(charactor('Bob', [0.3, 0.4, 0.3, 0.7]))    # ISTJ - 内向严谨，逻辑性强
    chat_room.add_charactor(charactor('Charlie', [0.7, 0.3, 0.4, 0.2])) # ESTP - 外向但实际，喜欢冒险
    chat_room.add_charactor(charactor('Diana', [0.2, 0.8, 0.9, 0.8]))  # INFJ - 深思熟虑，理想主义者

    chat_room.start_chat(5)