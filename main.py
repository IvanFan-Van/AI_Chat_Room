from typing import Annotated, TypedDict
from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv
import os
import json
from datetime import datetime
import time
import re

load_dotenv(find_dotenv()) # 加载环境变量, 使用langsmith监控

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
    # TODO 添加心理活动、日程安排等属性
    thoughts = []
    
    def __init__(self, name, mbti):
        self.name = name
        self.mbti = mbti
        self.background = '你是' + self.name + '。'
        self.generate_personality()
        self.thoughts = []
        
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
            "\n\n每一次活动请按照以下格式回复\n"
            "使用 <think></think> 包裹你的内心活动或是思考过程\n"
            "使用 <response></response> 包裹你的回答\n"
        )

    def add_thought(self, thought):
        self.thoughts.append({
            "thought": thought,
            "timestamp": datetime.now().isoformat()
        })


# =====定义聊天室类=====  
class ChatRoom():
    '''聊天室类:包括角色列表，当前对话记录'''
    num_charactors = 0
    charactors = []
    chat_record:list[Message] = []
    full_record:list[Message] = [] # 完整的记录, 包含内心活动部分
    # 修改背景设定为在一个大学学生群中的对话
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
    
    def __init__(self):
        # 创建一个唯一的会话ID，基于时间戳
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 创建日志文件夹
        os.makedirs(f"log/{self.session_id}", exist_ok=True)

    def add_charactor(self, charactor):
        self.num_charactors += 1
        self.charactors.append(charactor)

    def format_chat_history(self):
        """Format the chat history for the prompt."""
        history = ""
        for message in self.chat_record:
            history += f"{message['sender']}: {message['content']}\n"
        return history
    
    def extract_think_response(self, message_content):
        """从消息内容中提取思考和回应部分"""
        # 提取思考部分
        think_match = re.search(r'<think>(.*?)</think>', message_content, re.DOTALL)
        thought = think_match.group(1).strip() if think_match else ""
        
        # 提取回应部分
        response_match = re.search(r'<response>(.*?)</response>', message_content, re.DOTALL)
        response = response_match.group(1).strip() if response_match else message_content
        
        return thought, response

    def save_chat_history(self, incremental=False):
        """将聊天历史保存到文件中
        
        Args:
            incremental: 如果为True，表示这是增量更新而不是完整保存
        """
        file_path = os.path.join(f"log/{self.session_id}", f"chat_{self.session_id}.json")
        
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
                user_message = {"role": "user", "content": f"目前聊天内容如下\n---\n{history}\n---\n请以{charactor.name}的身份继续对话。"}
                messages.append(user_message)
    
                """获取回复"""
                response = llm.invoke(messages)
                response_content = response.content

                thought, chat_response = self.extract_think_response(response_content)

                """更新对话历史，添加时间戳"""
                timestamp = datetime.now().isoformat()

                self.chat_record.append({"sender": charactor.name, "content": chat_response, "timestamp": timestamp})
                self.full_record.append({"sender": charactor.name, "content": chat_response, "timestamp": timestamp, "thought": thought})

                print(f"{charactor.name}: ")
                if thought:
                    print(f"  💭 {thought}")  # 使用思考气泡表示内心想法
                print(f"  🗣️ {chat_response}")  # 使用说话图标表示实际回应
                
                # 每次角色回复后立即更新聊天记录
                self.save_chat_history(incremental=True)
        
        # 聊天结束后，执行最终保存并显示提示信息
        self.save_chat_history(incremental=False)

       
if __name__ == "__main__":
    chat_room = ChatRoom()
    # 增加更多角色信息
    chat_room.add_charactor(charactor('Alice', [0.7, 0.6, 0.8, 0.4]))
    chat_room.add_charactor(charactor('Bob', [0.3, 0.4, 0.3, 0.7]))

    chat_room.start_chat(3)