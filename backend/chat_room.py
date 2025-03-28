import re
import json
from datetime import datetime
from pathlib import Path
from .llm import llm

LOG_FOLDER = Path("../frontend/log") # 日志文件夹

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
3. 使用口语化表达（如“哈哈哈”、“emmm”、“awsl”）
4. 可适当加入表情符号（如😂、👀、👍）或颜文字（如~、>_<）
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
                        f"当前你的情绪：{'较高' if charactor.mood > 0.6 else '一般'}, 剩余精力：{charactor.energy:.1f}。"
                        f"如果精力低于0.3或情绪低落，你可能更倾向于不参与讨论。"
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

    def __str__(self):
        character_list = '\n'.join([str(character) for character in self.charactors])
        return f"聊天室包含{self.num_charactors}个角色:" + "\n" + f"{character_list}"
    