import threading
import json
from datetime import datetime
import time
import random

# =====初始化LLM=====
from langchain_deepseek import ChatDeepSeek
llm_chat = ChatDeepSeek(
    model="deepseek-chat",
    api_key="sk-34442cc84ebb4894b2eb884b3a6cd7f1"  # 替换实际密钥
)

llm_reasoner = ChatDeepSeek(
    model="deepseek-reasoner",
    api_key="sk-34442cc84ebb4894b2eb884b3a6cd7f1"  # 替换实际密钥
)

scheduler = ChatDeepSeek(
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
    
    def __init__(self, name, mbti, chatroom, background):
        threading.Thread.__init__(self)
        self.name = name
        self.mbti = mbti
        self.chatroom = chatroom
        self.background = '你是' + self.name + '。' + background + "\n\n" + self.generate_mbti_prompt()
        self.thoughts = []
        self.schedule = {}
        self.busy_until = None # 新增：表示当前是否处于“忙碌”状态（如开会
        self.is_busy = False # 新增：忙碌状态的结束时间


    def run(self):
        print("【线程开始】", self.name)
        self.generate_schedule()  # 先生成日程
        self.generate_response()
        print("【线程结束】", self.name)

    def __del__(self):
        pass

    def generate_mbti_prompt(self):
        """
        根据MBTI倾向程度生成角色扮演提示词
        
        参数:
        mbti_weights - 包含4个值的列表 [I倾向, N倾向, F倾向, P倾向]，每个值范围0~1
                    (例如 [0.3, 0.6, 0.4, 0.2] 表示 30%内向, 60%直觉, 40%情感, 20%感知)
        
        返回:
        角色扮演提示词字符串
        """
        if len(self.mbti) != 4 or any(not 0 <= w <= 1 for w in self.mbti):
            raise ValueError("输入必须是一个包含4个0~1之间数值的列表")
        
        i, n, f, p = self.mbti
        e, s, t, j = 1 - i, 1 - n, 1 - f, 1 - p
        
        # 确定MBTI类型
        ei = "I" if i > 0.5 else "E"
        sn = "N" if n > 0.5 else "S"
        tf = "F" if f > 0.5 else "T"
        jp = "P" if p > 0.5 else "J"
        
        mbti_type = ei + sn + tf + jp
        
        # 各维度描述
        ei_desc = {
            "E": f"外向型(倾向程度{int(e * 100)}%)，喜欢与人互动，从社交中获得能量",
            "I": f"内向型(倾向程度{int(i * 100)}%)，喜欢独处，从内心世界获得能量"
        }
        
        sn_desc = {
            "S": f"实感型(倾向程度{int(s * 100)}%)，注重现实和具体细节，关注事实",
            "N": f"直觉型(倾向程度{int(n * 100)}%)，关注大局和可能性，喜欢抽象概念"
        }
        
        tf_desc = {
            "T": f"思考型(倾向程度{int(t * 100)}%)，做决定时更注重逻辑和客观分析",
            "F": f"情感型(倾向程度{int(f * 100)}%)，做决定时更注重价值观和人际关系"
        }
        
        jp_desc = {
            "J": f"判断型(倾向程度{int(j * 100)}%)，喜欢有计划、有条理的生活方式",
            "P": f"感知型(倾向程度{int(p * 100)}%)，喜欢灵活、自发的生活方式"
        }
        
        # 组合提示词
        prompt = f"""请你扮演一个MBTI性格类型为{mbti_type}的人。你的性格特点如下：
    1. {ei_desc[ei]}
    2. {sn_desc[sn]}
    3. {tf_desc[tf]}
    4. {jp_desc[jp]}

    请完全按照这个性格特征来回应我，包括语言风格、思考方式和行为模式。你的回答应该自然、真实地反映{mbti_type}型人格的典型特征。你可以根据具体情境自由发挥，但要始终保持{mbti_type}型人格的核心特质。"""
        
        return prompt

    def generate_schedule(self):
        starttime = time.time()

        """生成日程安排，仅存储在 agent 内部和 chatroom.participants 中"""
        system_content = (
            self.background + "\n\n"
            "你是一名香港大学的学生，根据你的MBTI性格特点和兴趣，生成你今天的合理日程安排。\n"
            "要求：\n"
            "1. 使用24小时制（如 08:00-09:00），时间段不得重叠。\n"
            "2. 每个活动描述控制在20字以内，符合你的性格特点。\n"
            "3. 必须包含以下必选活动：睡觉时间（至少6小时）、三餐时间（早餐、午餐、晚餐）、至少1小时休息时间。\n"
            "4. 此外，至少安排3项个性化活动（例如学习、社交、兴趣等），覆盖上午、下午和晚上。\n"
            "仅返回 JSON 格式结果，不添加任何额外说明，例如：\n"
            "{\n"
            "  \"00:00-07:00\": \"睡觉\",\n"
            "  \"07:00-08:00\": \"早餐\",\n"
            "  \"12:00-13:00\": \"午餐\",\n"
            "  \"14:00-16:00\": \"上数学课\",\n"
            "  \"18:00-19:00\": \"晚餐\",\n"
            "  \"20:00-21:00\": \"休息放松\",\n"
            "  \"22:00-23:00\": \"夜读\"\n"
            "}"
        )
        system_message = {"role": "user", "content": system_content}
        messages = [system_message]

        response = scheduler.invoke(messages)
        response_content = response.content.strip()
        print(f"{self.name} 的原始日程输出: {response_content}")
        endtime = time.time()
        print(f"生成 {self.name} 的日程用时：{endtime - starttime}")

        try:
            self.schedule = json.loads(response_content)
            has_sleep = any("睡觉" in desc for desc in self.schedule.values())
            has_meals = sum(1 for desc in self.schedule.values() if "早餐" in desc or "午餐" in desc or "晚餐" in desc) >= 3
            has_rest = any("休息" in desc for desc in self.schedule.values())
            if not (has_sleep and has_meals and has_rest):
                raise ValueError("日程缺少必选活动")
        except json.JSONDecodeError:
            print(f"警告：{self.name} 的日程生成失败，使用默认日程")
            self.schedule = {
                "00:00-07:00": "睡觉",
                "07:00-08:00": "早餐",
                "08:00-10:00": "晨读",
                "12:00-13:00": "午餐",
                "14:00-16:00": "上课",
                "18:00-19:00": "晚餐",
                "20:00-21:00": "休息放松",
                "21:00-22:00": "社团活动"
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

    def is_time_in_schedule(self, current_time):
        """检查当前时间是否在某项日程内，返回活动描述和结束时间"""
        current_hour_min = current_time.strftime("%H:%M")
        for time_range, activity in self.schedule.items():
            start, end = time_range.split("-")
            if start <= current_hour_min < end:
                end_time = datetime.strptime(f"{current_time.strftime('%Y-%m-%d')} {end}", "%Y-%m-%d %H:%M")
                return activity, end_time
        return None, None

    def generate_response(self):
        while self.chatroom.chat_round > 0:
            starttime = time.time()
            current_time = datetime.now()


            # 检查是否处于忙碌状态
            if self.is_busy and current_time < self.busy_until:
                print(f"{self.name}: 当前忙碌中，直到 {self.busy_until.strftime('%H:%M')}，暂不发言")
                time.sleep(1)
                continue

            # 检查当前时间是否在日程内
            current_activity, end_time = self.is_time_in_schedule(current_time)
            if current_activity and "开会" in current_activity:
                self.is_busy = True
                self.busy_until = end_time
                print(f"{self.name}: 当前在开会，暂停发言直到 {end_time.strftime('%H:%M')}")
            
            system_content = self.background + "\n" + self.chatroom.chat_background
            system_message = {"role": "system", "content": system_content}
            messages = [system_message]
            history = self.chatroom.format_chat_history()
            user_message = {
                "role": "user",
                "content": (
                    f"目前聊天内容如下\n---\n{history}\n---\n"
                    f"当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"你是{self.name}，你的日程安排如下：\n{json.dumps(self.schedule, ensure_ascii=False)}\n"
                    f"你的思考和言行受MBTI性格特质和日程安排影响。可选择是否回应当前话题。\n"
                    f"如果当前活动让你无法发言（如开会），可以说‘我先忙，你们聊’并暂停参与。\n"
                    f"请按以下格式回复：\n"
                    f"<decision>yes/no</decision>\n"
                    f"<think>你的思考</think>\n"
                    f"<response>你的回应</response>（不参与则留空）\n"
                    f"回应为中文，40字以内，符合大学生日常语言风格。"
                )
            }
            messages.append(user_message)

            prob = random.uniform(0, 1)
            if prob < 0.3:
                print(f"【{self.name}】使用思考模型...")
                response = llm_reasoner.invoke(messages)
            else:
                print(f"【{self.name}】使用聊天模型...")
                response = llm_chat.invoke(messages)
            response_content = response.content
            decision, thought, chat_response = self.chatroom.extract_response_parts(response_content)

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

                # 如果提到“开会”或类似活动，设置为忙碌状态
                if "开会" in chat_response or "我先忙" in chat_response:
                    self.is_busy = True
                    self.busy_until = end_time if end_time else current_time.replace(hour=current_time.hour + 1, minute=0, second=0)
            
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
            
            print(f"生成 {self.name} 的回应用时：{endtime - starttime}")
            self.chatroom.save_chat_history(incremental=True)
            time.sleep(1)
