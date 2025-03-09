from typing import Annotated, TypedDict
from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv
import os
import json
from datetime import datetime
import time

load_dotenv(find_dotenv()) # 加载环境变量, 使用langsmith监控

#=====初始化LLM=====
from langchain_deepseek import ChatDeepSeek
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key="sk-34442cc84ebb4894b2eb884b3a6cd7f1"  # 替换实际密钥
)

#=====定义角色类=====
class charactor():
    '''角色类:包括名字，mbti，背景故事，心理活动'''
    name = 'undefined'
    mbti = [0.5, 0.5, 0.5, 0.5] #1/0 1st: E/I, 2nd: N/S, 3rd: F/T, 4th: J/P
    background = 'undefined'
    # 未来可以添加心理活动、日程安排等属性
    psychological_state = {}
    schedule = {}
    
    def __init__(self, name, mbti):
        self.name = name
        self.mbti = mbti
        self.background = '你是' + self.name + '。'
        self.gemerate_personality()

    def gemerate_personality(self):
        """根据MBTI值生成性格描述"""
        traits = []
        if self.mbti[0] > 0.5:
            traits.append(f"外向型(E)：喜欢社交，从与他人互动中获取能量")
        else:
            traits.append("内向型(I)：更喜欢独处，从内心世界获取能量")
            
        if self.mbti[1] > 0.5:
            traits.append("直觉型(N)：关注可能性和未来，喜欢抽象思考")
        else:
            traits.append("感觉型(S)：关注现实和具体细节，实际pragmatic")
            
        if self.mbti[2] > 0.5:
            traits.append("情感型(F)：决策基于价值观和人际关系")
        else:
            traits.append("思维型(T)：决策基于逻辑和客观分析")
            
        if self.mbti[3] > 0.5:
            traits.append("判断型(J)：喜欢计划和确定性")
        else:
            traits.append("感知型(P)：灵活适应，享受自发性")
            
        personality = "、".join(traits)
        self.background += f"你具有以下性格特点：{personality}。在对话中要体现这些特质。"
    
# =====定义消息类型=====
class Message(TypedDict):
    sender: str
    content: str
    timestamp: str  # 添加时间戳

# =====定义聊天室类=====  
class ChatRoom():
    '''聊天室类:包括角色列表，当前对话记录'''
    num_charactors = 0
    charactors = []
    chat_record:list[Message] = []
    chat_background = '你是一名大学生。你现在正与同在一所大学的朋友进行日常对话。要求：使用日常语言回复，使用中文，不用在回答前面加名字和冒号，别重复之前说过的话，每次回复不超过50字。'
    session_id = ""
    
    def __init__(self):
        # 创建一个唯一的会话ID，基于时间戳
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 确保存在记录文件夹
        os.makedirs(f"chat_histories/{self.session_id}", exist_ok=True)

    def add_charactor(self, charactor):
        self.num_charactors += 1
        self.charactors.append(charactor)

    def format_chat_history(self):
        """Format the chat history for the prompt."""
        history = ""
        for message in self.chat_record:
            history += f"{message['sender']}: {message['content']}\n"
        return history

    def save_chat_history(self, incremental=False):
        """将聊天历史保存到文件中
        
        Args:
            incremental: 如果为True，表示这是增量更新而不是完整保存
        """
        file_path = os.path.join(f"chat_histories/{self.session_id}", f"chat_{self.session_id}.json")
        
        # 准备要保存的数据
        chat_data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "participants": [char.name for char in self.charactors],
            "background": self.chat_background,
            "messages": self.chat_record
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

                """更新对话历史，添加时间戳"""
                timestamp = datetime.now().isoformat()
                self.chat_record.append({"sender": charactor.name, "content": response_content, "timestamp": timestamp})
                print(f"{charactor.name}: {response_content}")
                
                # 每次角色回复后立即更新聊天记录
                self.save_chat_history(incremental=True)
        
        # 聊天结束后，执行最终保存并显示提示信息
        self.save_chat_history(incremental=False)

       
if __name__ == "__main__":
    chat_room = ChatRoom()
    chat_room.add_charactor(charactor('Alice', [0.7, 0.5, 0.5, 0.5]))
    chat_room.add_charactor(charactor('Bob', [0.1, 0.5, 0.5, 0.5]))

    chat_room.start_chat(10)