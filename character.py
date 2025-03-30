import threading
import json
from datetime import datetime
import time
import random
from typing import Dict, Any, List, Optional, Tuple

from willingness_manager import WillingnessManger
from prompt_builder import PromptBuilder

# =====初始化LLM=====
from langchain_deepseek import ChatDeepSeek
llm_chat = ChatDeepSeek(
    model="deepseek-chat",
    api_key="sk-34442cc84ebb4894b2eb884b3a6cd7f1"
)

llm_reasoner = ChatDeepSeek(
    model="deepseek-reasoner",
    api_key="sk-34442cc84ebb4894b2eb884b3a6cd7f1"
)

scheduler = ChatDeepSeek(
    model="deepseek-chat",
    api_key="sk-34442cc84ebb4894b2eb884b3a6cd7f1"
)


class Character(threading.Thread):
    """
    角色类: 管理角色属性、状态和行为
    
    属性:
        name: 角色名称
        mbti: MBTI性格特质权重 [I倾向, N倾向, F倾向, P倾向]
        chatroom: 所在聊天室引用
        background: 角色背景故事
        thoughts: 角色心理活动记录
        schedule: 角色日程安排
        willingness_manager: 聊天意愿管理器
    """
    
    def __init__(self, name: str, mbti: List[float], chatroom: Any, background: str):
        """
        初始化角色
        
        参数:
            name: 角色名称
            mbti: MBTI性格特质权重
            chatroom: 聊天室对象
            background: 角色背景描述
        """
        threading.Thread.__init__(self)
        self.name = name
        self.mbti = mbti
        self.chatroom = chatroom
        self.background = background
        
        # 创建聊天意愿管理器
        self.willingness_manager = WillingnessManger(name)


        self.thoughts = []
        self.schedule = {}

    def run(self) -> None:
        """线程运行函数，生成日程并开始响应聊天"""
        print(f"【线程开始】{self.name}")
        self.generate_schedule()  # 先生成日程
        self.generate_response()
        print(f"【线程结束】{self.name}")

    def __del__(self) -> None:
        """析构函数，清理资源"""
        pass

    def generate_schedule(self) -> None:
        """生成日程安排，存储在角色内部和chatroom.participants中"""
        starttime = time.time()

        # 使用PromptBuilder构建日程生成提示
        system_content = PromptBuilder.build_schedule_prompt(self.name, self.background)
        system_message = {"role": "user", "content": system_content}
        messages = [system_message]

        # 调用LLM生成日程
        response = scheduler.invoke(messages)
        response_content = response.content.strip()
        print(f"{self.name} 的日程: {response_content}")
        endtime = time.time()
        print(f"生成 {self.name} 的日程用时：{endtime - starttime:.2f}秒")

        # 处理日程结果
        try:
            self.schedule = json.loads(response_content)
        except json.JSONDecodeError:
            print(f"警告：{self.name} 的日程生成失败，使用默认日程")
            self.schedule = {
                "22:00-07:00": "睡觉",
                "07:00-08:00": "早餐",
                "12:00-13:00": "午餐",
                "18:00-19:00": "晚餐",
            }
        # 将日程存储到 chatroom.participants 中
        for participant in self.chatroom.participants:
            if participant["name"] == self.name:
                participant["schedule"] = self.schedule
                break

    def is_time_in_schedule(self, current_time: datetime) -> Tuple[Optional[str], Optional[datetime]]:
        """检查当前时间是否在某项日程内，返回活动描述和结束时间"""
        current_hour_min = current_time.strftime("%H:%M")
        for time_range, activity in self.schedule.items():
            start, end = time_range.split("-")
            if start <= current_hour_min < end:
                end_time = datetime.strptime(f"{current_time.strftime('%Y-%m-%d')} {end}", "%Y-%m-%d %H:%M")
                return activity, end_time
        return None, None

    def generate_response(self) -> None:
        """生成角色的聊天响应"""
        while self.chatroom.chat_round > 0:
            starttime = time.time()
            current_time = datetime.now()

            # 检查当前时间是否在日程内
            current_activity, end_time = self.is_time_in_schedule(current_time)
            
            # 更新聊天意愿
            chat_history = self.chatroom.chat_record[-10:]  # 获取最近10条消息
            willingness = self.willingness_manager.update_willingness(chat_history, current_time)
            response_prob = self.willingness_manager.get_response_probability()
            
            # 基于性格特质调整概率
            # 内向型人格可能更少参与对话
            if self.mbti[0] > 0.7:  # 高度内向
                response_prob *= 0.8
            # 外向型人格可能更多参与对话
            elif self.mbti[0] < 0.3:  # 高度外向
                response_prob *= 1.2
                
            # 限制范围
            response_prob = min(max(response_prob, 0.05), 0.95)
            
            # 使用PromptBuilder构建消息
            history = self.chatroom.format_chat_history()
            messages = PromptBuilder.build_messages(
                self.name,
                self.background,
                self.chatroom.chat_background,
                history,
                current_time,
                current_activity
            )

            # 使用聊天意愿系统决定是否回应
            prob = random.uniform(0, 1)
            if prob < response_prob:
                # 根据意愿强度决定使用哪个模型
                if willingness > 0.7:
                    print(f"【{self.name}】兴趣高，使用思考模型...")
                    response = llm_reasoner.invoke(messages)
                else:
                    print(f"【{self.name}】使用聊天模型...")
                    response = llm_chat.invoke(messages)
                    
                response_content = response.content
                decision, thought, chat_response = self.chatroom.extract_response_parts(response_content)
                
                # 调整决策结果以符合聊天意愿
                if willingness < 0.3 and decision == "yes":
                    # 低意愿时，有50%概率改为不回应
                    if random.random() < 0.5:
                        decision = "no"
                        chat_response = ""
                
                # 更新发送消息后的状态
                if decision == "yes" and chat_response.strip():
                    self.willingness_manager.message_sent(current_time)
            else:
                # 兴趣不够，直接不回应
                decision = "no"
                thought = "我现在不太想参与这个话题。"
                chat_response = ""
                
            # 剩余处理逻辑保持不变...
            endtime = time.time()
            
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
            print(f"  🤔 决定{'参与' if decision == "yes" else '不参与'}发言 (意愿值: {willingness:.2f}, 概率: {response_prob:.2f})")
            if thought:
                print(f"  💭 {thought}")
            if decision == "yes" and chat_response.strip():
                print(f"  🗣️ {chat_response}")
            
            print(f"生成 {self.name} 的回应用时：{endtime - starttime:.2f}秒")
            self.chatroom.save_chat_history(incremental=True)
            time.sleep(1)
