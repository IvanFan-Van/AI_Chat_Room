import random
import time

DEFAULT_INTERESTS = ["学习新知识", "看电影", "听音乐", "打游戏", "运动健身", "摄影", "旅行", "美食", "读书", "写作"]

#=====定义角色类=====
class Charactor():
    def __init__(self, name, mbti, interests=None):
        self.name = name
        self.mbti = mbti
        self.background = '你是' + self.name + '。'
        
        # 新增动态属性
        self.mood = 0.5  # 情绪值（0-1）
        self.energy = 0.8  # 精力值（影响回复频率）
        self.interests = self.interests if interests else random.sample(DEFAULT_INTERESTS, 3)  # 兴趣爱好

        self.generate_personality()


        
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
            f"\n\n你的当前情绪：{'积极' if self.mood > 0.6 else '平静' if self.mood > 0.3 else '低落'}"
            f"\n你的剩余精力：{int(self.energy * 100)}%"
        )
        self.background += (
            "\n\n你不必对每一个话题都做出回应。根据你的性格特点，以及目前情绪和精力来决定是否参与话题。"
            "\n每一次活动请按照以下格式回复："
            "\n1. 首先，决定你是否要对当前话题发表回应："
            "\n   - 使用 <decision>yes</decision> 表示你决定参与这个话题"
            "\n   - 使用 <decision>no</decision> 表示你决定不参与这个话题"
            "\n2. 然后，无论你决定是否参与，都需要解释你的决定理由："
            "\n   - 使用 <think>你的想法</think> 包裹你的内心活动或思考过程"
            "\n在<think>中需包含以下内容:"
            "\n1. 分析当前对话氛围"
            "\n2. 评估话题与自身兴趣的关联"
            "\n3. 预测他人可能的反应"
            "\n4. 最终决策的理由"
            "\n3. 如果你决定参与，请提供你的回应："
            "\n   - 使用 <response>你的回应</response> 包裹你要在群里说的话"
            "\n如果你决定不参与，则无需填写<response>部分"
        )

    def update_state(self):
        """动态更新角色状态"""
        self.mood = max(0, min(1, self.mood + random.uniform(-0.1, 0.1)))
        self.energy = max(0, min(1, self.energy - 0.05))

    def __str__(self):
        return f"角色：{self.name}，MBTI：{self.mbti}，兴趣爱好：{self.interests}"
    