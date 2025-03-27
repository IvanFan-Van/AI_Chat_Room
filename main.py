from typing import Annotated, TypedDict
from dataclasses import dataclass
from dotenv import load_dotenv, find_dotenv
import os
import json
from datetime import datetime
import time
import re
import threading # 多线程

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
# charactor继承Thread父类，并进行重写补充
class charactor(threading.Thread):
    '''角色类:包括名字，mbti，所在聊天室，背景故事，心理活动'''
    name = 'undefined'
    mbti = [0.5, 0.5, 0.5, 0.5] #1/0 1st: E/I, 2nd: N/S, 3rd: F/T, 4th: J/P
    chatroom = None
    background = 'undefined'
    # TODO 添加心理活动、日程安排等属性
    thoughts = []

    def __init__(self, name, mbti, chatroom):
        threading.Thread.__init__(self)
        self.name = name
        self.mbti = mbti
        self.chatroom = chatroom
        self.background = '你是' + self.name + '。'
        self.generate_personality()
        self.thoughts = []

    
    def run(self):      # 重写父类中的run函数
        print("【线程开始】", self.name)
        self.chat_multi()
        print("【线程结束】", self.name)
 
    def __del__(self):  # 重写父类析构函数
        print("【线程销毁释放内存】", self.name)

    # TODO 添加更多属性, 丰富性格特征描述, 添加程度描述
    def generate_personality(self):
        """根据MBTI重新生成更加完整且符合实际的MBTI性格描述"""
        description = ""
        # Extraversion vs. Introversion
        if self.mbti[0] > 0.5:
            description += "你较为外向：你在与他人互动时能快速充电，乐观开朗，擅长在社交场合中表达自我。\n"
        else:
            description += "你较为内向：你倾向于从独处和内省中恢复能量，注重深入思考，显得沉着稳重。\n"
        # inTuition vs. Sensing
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
        self.background = basic_info + "\n\n你的MBTI性格描述：\n" + description + "\n你的思考和言行将会受上述性格特质影响。"

    def add_thought(self, thought):
        self.thoughts.append({
            "thought": thought,
            "timestamp": datetime.now().isoformat()
        })

    # 自定义的线程任务函数
    def chat_multi(self):
        while self.chatroom.chat_round > 0:
            """构建系统消息 (角色设定 + 聊天背景) """
            system_content = self.background + "\n" + self.chatroom.chat_background
            system_message = {"role": "system", "content": system_content}

            """构建 message 列表"""
            messages = [system_message]

            """构建对话历史"""
            history = self.chatroom.format_chat_history()

            """构建用户消息"""
            user_message = {
                "role": "user", 
                "content": (
                    # 获取聊天记录，以及回复的提示和格式
                    f"目前聊天内容如下\n---\n{history}\n---\n"
                    f"你是{self.name}，你的思考和言行将会受到你的MBTI性格特质的影响。你可以自行选择是否要对当前话题做出回应。\n"
                    f"请根据以下格式回复：\n"
                    f"如果你要参与发言，请使用“<decision>yes</decision>”，并使用“<response>你的回应</response>”，在“你的回应”中填入你的回应。\n"
                    f"如果你不参与发言，请使用“<decision>no</decision>”，无需在<response>中回应。\n"
                    f"如果想要对某个人说话，可以在回应中“@”对方。\n"
                    f"请使用“<think>你的思考</think>”，在“你的思考”中解释参与或不参与的原因。\n"
                    f"回应应该反映你的MBTI性格特点,但请尽量不要明说MBTI相关内容。"
                )
            }
            messages.append(user_message)

            """获取回复"""
            response = llm.invoke(messages)
            response_content = response.content

            """处理回复，提取决策、思考和回应部分"""
            decision, thought, chat_response = self.chatroom.extract_response_parts(response_content)

            ######回合数减一#####若回合数为0，则结束对话，等待其他进程结束######
            if self.chatroom.chat_round <= 0:
                break
            self.chatroom.chat_round -= 1

            """更新对话历史，添加时间戳"""
            timestamp = datetime.now().isoformat()

            if decision == "yes" and chat_response.strip():
                self.chatroom.chat_record.append({
                    "sender": self.name, 
                    "content": chat_response, 
                    "timestamp": timestamp
                })

            """添加完整记录（包括决策、思考和回应）"""
            full_message = {
                "sender": self.name,
                "content": chat_response if decision == "yes" else "",
                "timestamp": timestamp,
                "thought": thought,
                "decision": decision
            }
            self.chatroom.full_record.append(full_message)

            """打印输出，包括决策、思考和回应"""
            print()
            print(f"{self.name}: ")
            print(f"  🤔 决定{'参与' if decision == 'yes' else '不参与'}发言")
            if thought:
                print(f"  💭 {thought}")  # 思考
            
            if decision == "yes" and chat_response.strip():
                print(f"  🗣️ {chat_response}")  # 发言
            
            # 每次角色回复后立即更新聊天记录
            self.chatroom.save_chat_history(incremental=True)

            # 模拟思考时间，防止回复过快
            time.sleep(1)



# =====定义聊天室类=====  
class ChatRoom():
    '''聊天室类:包括角色列表，当前对话记录'''
    num_charactors = 0
    charactors = []
    chat_round = 0
    chat_record = [] # 公开的对话记录（其他角色可见的部分）
    full_record = [] # 完整的记录, 包含内心活动部分

    # 聊天室背景设定
    chat_background = '''
你是一名大学生，刚刚加入香港大学的学生群。这个群聊中有来自不同专业、不同年级的同学。
你可以从一下话题展开聊天：校园生活、课业学习、社团活动、兴趣爱好、感情爱情、近期热门话题等。

请注意对话要求：
1. 基本要求：使用中文交流，不要在回答前加名字和冒号，不要重复之前说过的内容。
2. 参考微信、QQ等社交媒体的聊天记录的发言回复篇幅长短，每次回复不超过50字，保持对话流畅自然和逻辑性。
3. 使用符合当代大学生的日常语言风格，可以自然地使用一些网络用语。
4. 根据你的性格特点、心理状态和日程安排来回应。
5. 敢于开启新话题，可以多个话题并行，随心所欲地聊天。
6. 不要把群聊聊成私聊，如果发现一直和某个人在聊天，请及时调整话题。
'''
    session_id = ""
    
    def __init__(self):
        # 创建一个唯一的会话ID，基于时间戳
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 创建日志文件夹
        os.makedirs(f"log/{self.session_id}", exist_ok=True)
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
        initial_message = {
            "sender": "system",
            "content": "群公告: 欢迎来到香港大学的学生群聊！请同学们畅所欲言，希望大家交到好朋友，度过愉快的时光！刚进群的同学可以自我介绍一下~",
            "timestamp": datetime.now().isoformat()
        }
        self.chat_record.append(initial_message)
        self.full_record.append(initial_message)

        self.chat_round = chat_length
        # 启动多线程
        for charactor in self.charactors:
            charactor.start()
        # 等待所有线程结束
        for charactor in self.charactors:
            charactor.join()
        print("聊天结束")

        # 聊天结束后，执行最终保存并显示提示信息
        self.save_chat_history(incremental=False)

       
if __name__ == "__main__":
    chat_room = ChatRoom()
    # 增加更多角色信息
    chat_room.add_charactor(charactor('Alice', [0.8, 0.7, 0.8, 0.4], chat_room))    # ENFP - 活泼外向，想象力丰富
    chat_room.add_charactor(charactor('Bob', [0.3, 0.4, 0.3, 0.7], chat_room))      # ISTJ - 内向严谨，逻辑性强
    chat_room.add_charactor(charactor('Charlie', [0.7, 0.3, 0.4, 0.2], chat_room))  # ESTP - 外向但实际，喜欢冒险
    chat_room.add_charactor(charactor('Diana', [0.2, 0.8, 0.9, 0.8], chat_room))    # INFJ - 深思熟虑，理想主义者
    chat_room.add_charactor(charactor('Eve', [0.6, 0.2, 0.8, 0.7], chat_room))      # ESFJ - 社交活跃，关心他人
    chat_room.add_charactor(charactor('Frank', [0.4, 0.6, 0.2, 0.3], chat_room))    # INTP - 内向思考者，喜欢独立思考
    chat_room.add_charactor(charactor('Grace', [0.9, 0.9, 0.4, 0.6], chat_room))    # ENTJ - 领导者，目标明确
    chat_room.add_charactor(charactor('Henry', [0.1, 0.1, 0.6, 0.1], chat_room))    # ISFP - 内向艺术家，喜欢创造
    chat_room.start_chat(100)