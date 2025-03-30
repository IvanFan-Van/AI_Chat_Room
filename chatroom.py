"""
聊天室模块：负责管理AI角色之间的聊天交流
包含聊天记录的存储、角色的管理以及聊天流程的控制
"""

import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any, TypedDict, Optional
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Message(TypedDict):
    """消息数据结构定义"""
    sender: str
    content: str
    timestamp: str
    thought: str  # 角色的内心想法（可选）
    decision: str  # 决策结果（可选）


class Participant(TypedDict):
    """参与者数据结构定义"""
    name: str
    mbti: List[float]
    schedule: Dict[str, str]  # 时间段到活动的映射


class ChatRoom:
    """
    聊天室类：管理多个AI角色之间的对话交流
    
    主要功能：
    1. 添加和管理角色
    2. 记录聊天历史
    3. 提取响应内容
    4. 保存聊天记录
    5. 控制聊天流程
    """
    
    def __init__(self, initial_message: Optional[Dict[str, Any]] = None):
        """
        初始化聊天室
        
        参数:
            initial_message: 可选，聊天的初始消息
        """
        # 生成会话ID（基于当前时间）
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 创建日志目录
        os.makedirs(f"log/{self.session_id}", exist_ok=True)
        
        # 初始化聊天相关属性
        self.charactors = []  # 角色对象列表
        self.participants: List[Participant] = []  # 参与者信息列表
        self.chat_record = []  # 可见聊天记录
        self.full_record = []  # 完整聊天记录（包含内部状态）
        self.chat_round = 0  # 聊天轮数
        
        # 设置初始消息
        self.initial_message = initial_message if initial_message else None

    def add_charactor(self, character):
        """
        添加角色到聊天室
        
        参数:
            character: 角色对象，应该是charactor类的实例
        """
        # 添加角色对象到列表
        self.charactors.append(character)
        
        # 将角色信息添加到参与者列表
        self.participants.append({
            "name": character.name,
            "mbti": character.mbti,
            "schedule": {}  # 初始化为空，日程将在generate_schedule中填充
        })

    @property
    def num_charactors(self) -> int:
        """获取角色数量"""
        return len(self.charactors)

    def format_chat_history(self, max_messages: int = 20) -> str:
        """
        格式化最近的聊天记录为文本
        
        参数:
            max_messages: 最多包含的消息数量
            
        返回:
            格式化后的聊天记录文本
        """
        history = ""
        for message in self.chat_record[-max_messages:]:
            history += f"{message['sender']}: {message['content']}\n"
        return history

    def extract_response_parts(self, message_content: str) -> tuple:
        """
        从LLM响应中提取决策、思考和回复部分
        
        参数:
            message_content: LLM生成的原始响应内容
            
        返回:
            (决策, 思考内容, 回复内容)的元组
        """
        # 提取决策部分(yes/no)
        decision_match = re.search(r'<decision>(.*?)</decision>', message_content, re.DOTALL)
        decision = decision_match.group(1).strip().lower() if decision_match else "yes"
        
        # 提取思考内容
        think_match = re.search(r'<think>(.*?)</think>', message_content, re.DOTALL)
        thought = think_match.group(1).strip() if think_match else ""
        
        # 提取回复内容
        response_match = re.search(r'<response>(.*?)</response>', message_content, re.DOTALL)
        response = response_match.group(1).strip() if response_match else ""
        
        return decision, thought, response

    def save_chat_history(self, incremental: bool = False) -> str:
        """
        将聊天历史保存到文件
        
        参数:
            incremental: 是否为增量保存（不打印保存信息）
            
        返回:
            保存的文件路径
        """
        # 构建文件路径
        file_path = os.path.join(f"log/{self.session_id}", f"chat_{self.session_id}.json")
        
        # 准备聊天数据
        chat_data = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "participants": self.participants,  # 保存每个角色的信息，包括日程
            "background": self.chat_background,  # 聊天背景
            "messages": self.full_record  # 完整消息记录
        }
        
        # 写入文件
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
        
        # 仅在非增量保存时打印信息
        if not incremental:
            print(f"\n聊天记录已保存至: {file_path}")
            
        return file_path

    def start_chat(self, chat_length: int):
        """
        启动聊天流程
        
        参数:
            chat_length: 聊天总轮数
        """
        print("=== 生成每日日程 ===")
        # 为每个角色生成日程安排
        for character in self.charactors:
            character.generate_schedule()
            
        print("=== 开始聊天 ===")
        # 添加初始消息
        if self.initial_message:
            self.chat_record.extend(self.initial_message)
            self.full_record.extend(self.initial_message)

        # 设置聊天轮数并启动所有角色线程
        self.chat_round = chat_length
        for character in self.charactors:
            character.start()
            
        # 等待所有角色线程完成
        for character in self.charactors:
            character.join()
            
        print("【聊天结束】")
        # 清理角色资源
        for character in self.charactors:
            character.__del__()
            
        # 保存最终的聊天历史
        self.save_chat_history(incremental=False)
        
    def add_chat_background(self, background: str):
        """
        设置聊天背景信息
        
        参数:
            background: 聊天的背景描述
        """
        self.chat_background = background
