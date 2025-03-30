from datetime import datetime
from typing import List, Dict, Any, Optional

class PromptBuilder:
    """
    处理AI聊天室中角色交互的提示构建。
    将提示构建逻辑与角色行为逻辑分离。
    """
    
    # 自然对话风格的指导，作为类变量存储
    NATURAL_DIALOGUE_GUIDANCE = """
作为一个真实的大学生，你的对话应该自然流畅，像人类一样表达：

1. 不要使用括号"()"来描述动作或情感，而是通过语言表达和用词选择自然地传达情绪
2. 不要写"*笑*"、"*叹气*"等表情动作描述
3. 用适当的语气词、标点符号来传达情绪（如：啊、哦、嗯、！、？、...）
4. 使用符合你性格的口头禅和表达习惯
5. 你不是AI，不要过于正式或过度解释，有时可以使用不完整句子
6. 可以使用表情符号😊，但要适度且符合你的性格
7. 偶尔可以犯一些小的拼写错误或用词不当，这样更接近真人聊天
8. 避免过度文雅或结构化的语言，大学生更多使用简洁直接的表达方式
9. 要求简短明了，避免冗长的句子和复杂的结构
"""

    @staticmethod
    def build_character_background(name: str, background: str, mbti_prompt: str) -> str:
        """
        构建完整的角色背景描述
        
        参数:
            name: 角色名称
            background: 角色基础背景描述
            mbti_prompt: MBTI性格提示
            
        返回:
            完整的角色背景提示
        """
        return f'你是{name}。{background}\n\n{mbti_prompt}\n\n{PromptBuilder.NATURAL_DIALOGUE_GUIDANCE}'
    
    @staticmethod
    def build_mbti_prompt(mbti_weights: List[float]) -> str:
        """
        根据MBTI倾向程度生成角色扮演提示词
        
        参数:
            mbti_weights: 包含4个值的列表 [I倾向, N倾向, F倾向, P倾向]，每个值范围0~1
                        (例如 [0.3, 0.6, 0.4, 0.2] 表示 30%内向, 60%直觉, 40%情感, 20%感知)
        
        返回:
            角色扮演提示词字符串
        """
        if len(mbti_weights) != 4 or any(not 0 <= w <= 1 for w in mbti_weights):
            raise ValueError("输入必须是一个包含4个0~1之间数值的列表")
        
        i, n, f, p = mbti_weights
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

    @staticmethod
    def build_schedule_prompt(name: str, background: str) -> str:
        """构建生成日程的提示"""
        return (
            background + "\n\n"
            f"请为我生成今天的日程安排, 包括和要求如下:\n"
            "1. 早上的学习和工作安排\n"
            "2. 下午的活动和任务\n"
            "3. 晚上的计划和休息时间\n"
            "4. 使用24小时制（如 08:00-09:00），时间段不得重叠。\n"
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

    @staticmethod
    def build_system_message(background: str, chat_background: str) -> Dict[str, str]:
        """构建包含角色和聊天上下文的系统消息"""
        system_content = background + "\n" + chat_background
        return {"role": "system", "content": system_content}
    
    @staticmethod
    def build_user_message(name: str, chat_history: str, schedule_prompt: str) -> Dict[str, str]:
        """构建包含指令和上下文的用户消息"""
        return {
            "role": "user",
            "content": (
                f"目前聊天内容如下\n---\n{chat_history}\n---\n"
                f"{schedule_prompt}\n"
                f"你是{name}. 你的思考和言行受MBTI性格特质和日程安排影响。可选择是否回应当前话题。\n"
                f"请按以下格式回复：\n"
                f"<decision>yes/no</decision>\n"
                f"<think>你的思考</think>\n"
                f"<response>你的回应</response>（不参与则留空）\n"
            )
        }
    
    @staticmethod
    def format_schedule_prompt(current_time: datetime, current_activity: Optional[str] = None) -> str:
        """格式化角色当前日程的提示"""
        if current_activity:
            return f"当前时间是{current_time.strftime('%H:%M')}，你正在进行的活动是：{current_activity}"
        return "你没有日程安排"
    
    @staticmethod
    def build_messages(name: str, background: str, 
                      chat_history: str, current_time: datetime, 
                      current_activity: Optional[str] = None) -> List[Dict[str, str]]:
        """构建用于LLM输入的完整消息数组"""
        chat_background = ""
        system_message = PromptBuilder.build_system_message(background, chat_background)
        schedule_prompt = PromptBuilder.format_schedule_prompt(current_time, current_activity)
        user_message = PromptBuilder.build_user_message(name, chat_history, schedule_prompt)
        
        return [system_message, user_message]


# 测试功能
if __name__ == "__main__":
    from pprint import pprint as pp

    # 测试数据
    name = "张三"
    background = "你是健身教练之子，母亲早逝，靠奖学金维持学业,你喜欢健身和弹吉他. 表面玩世不恭，实际用健身对抗焦虑症."
    
    # 测试消息构建
    chat_history = "David: Emily 我喜欢你\nEmily: 你喜欢我？\nGeorge: 哈哈，David又在开玩笑了"
    current_time = datetime.now()
    current_activity = "阅读书籍"
    
    # 构建生成Schedule的提示
    prompt = PromptBuilder.build_schedule_prompt(name, background)
    print("===生成日程的提示===")
    print(prompt)

    messages = PromptBuilder.build_messages(
        name, background, chat_history, 
        current_time, current_activity
    )
    
    print("\n===消息构建结果===")
    print("系统消息长度:", len(messages[0]["content"]))
    print("用户消息长度:", len(messages[1]["content"]))
    print("\n系统消息内容:")
    print(messages[0]["content"])
    print("\n用户消息内容:")
    print(messages[1]["content"])
