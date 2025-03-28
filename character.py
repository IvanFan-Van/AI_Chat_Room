import threading
import json
from datetime import datetime
import time

# =====初始化LLM=====
from langchain_deepseek import ChatDeepSeek
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key="sk-34442cc84ebb4894b2eb884b3a6cd7f1"  # 替换实际密钥
)

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
