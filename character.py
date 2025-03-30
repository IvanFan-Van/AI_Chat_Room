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
        
        # 添加自然对话风格的指导
        natural_dialogue_guidance = """
作为一个真实的大学生，你的对话应该自然流畅，像人类一样表达：

1. 不要使用括号"()"来描述动作或情感，而是通过语言表达和用词选择自然地传达情绪
2. 不要写"*笑*"、"*叹气*"等表情动作描述
3. 用适当的语气词、标点符号来传达情绪（如：啊、哦、嗯、！、？、...）
4. 使用符合你性格的口头禅和表达习惯
5. 你不是AI，不要过于正式或过度解释，有时可以使用不完整句子
6. 可以使用表情符号😊，但要适度且符合你的性格
7. 偶尔可以犯一些小的拼写错误或用词不当，这样更接近真人聊天
8. 避免过度文雅或结构化的语言，大学生更多使用简洁直接的表达方式

示例差异：
❌ "我觉得这很有趣 (微笑)"
✅ "哈哈这也太有意思了吧！"

❌ "我今天很开心，因为我拿到了好成绩 (开心)"
✅ "天啊！今天拿到成绩单了，超开心的！！"
"""
        
        self.background = '你是' + self.name + '。' + background + "\n\n" + self.generate_mbti_prompt() + "\n\n" + natural_dialogue_guidance
        self.thoughts = []
        self.schedule = {}

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
            f"我是{self.name}, 请为我生成今天的日程安排, 包括和要求如下:\n"
            "1. 早上的学习和工作安排\n"
            "2. 下午的活动和任务\n"
            "3. 晚上的计划和休息时间\n"
            "1. 使用24小时制（如 08:00-09:00），时间段不得重叠。\n"
            "仅返回 JSON 格式结果，不添加任何额外说明，不要添加任何markdown或代码块样式. 例如：\n"
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
        except json.JSONDecodeError:
            print(f"警告：{self.name} 的日程生成失败，使用默认日程")
            self.schedule = {
                "22:00-07:00": "睡觉",
                "07:00-08:00": "早餐",
                "12:00-13:00": "午餐",
                "18:00-19:00": "晚餐",
            }
        print(f"{self.name} 的日程：{json.dumps(self.schedule, ensure_ascii=False, indent=2)}")
        # 将日程存储到 chatroom.participants 中
        for participant in self.chatroom.participants:
            if participant["name"] == self.name:
                participant["schedule"] = self.schedule
                break


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

            # 检查当前时间是否在日程内
            current_activity, end_time = self.is_time_in_schedule(current_time)
            schedule_prompt = "你没有日程安排"
            if current_activity:
                schedule_prompt = f"当前时间是{current_time.strftime('%H:%M')}，你正在进行的活动是：{current_activity}"
            
            system_content = self.background + "\n" + self.chatroom.chat_background
            system_message = {"role": "system", "content": system_content}
            messages = [system_message]
            history = self.chatroom.format_chat_history()
            user_message = {
                "role": "user",
                "content": (
                    f"目前聊天内容如下\n---\n{history}\n---\n"
                    f"{schedule_prompt}\n"
                    f"你是{self.name}. 你的思考和言行受MBTI性格特质和日程安排影响。可选择是否回应当前话题。\n"
                    f"请按以下格式回复：\n"
                    f"<decision>yes/no</decision>\n"
                    f"<think>你的思考</think>\n"
                    f"<response>你的回应</response>（不参与则留空）\n"
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
