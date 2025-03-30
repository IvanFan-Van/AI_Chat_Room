import math
import threading
import time
from datetime import datetime
from typing import Dict, Tuple, Optional

class MoodState:
    """表示角色心情状态的类"""
    
    def __init__(self, valence: float = 0.0, arousal: float = 0.5):
        """
        初始化心情状态
        
        参数:
            valence: 愉悦度 (-1.0到1.0，负值表示负面情绪，正值表示正面情绪)
            arousal: 唤醒度 (0.0到1.0，低值表示低能量状态，高值表示高能量状态)
        """
        self.valence = valence    # 情绪的愉悦度
        self.arousal = arousal    # 情绪的唤醒度
        self.text = self._get_mood_text()  # 当前心情的文字描述
        
    def _get_mood_text(self) -> str:
        """根据愉悦度和唤醒度确定心情描述"""
        # 第一象限：高唤醒，高愉悦 - 积极激动的情绪
        if self.valence >= 0.3 and self.arousal >= 0.6:
            if self.valence > 0.7:
                return "兴高采烈"
            return "开心"
            
        # 第二象限：高唤醒，低愉悦 - 消极激动的情绪
        if self.valence <= -0.3 and self.arousal >= 0.6:
            if self.valence < -0.7:
                return "愤怒"
            return "焦虑"
            
        # 第三象限：低唤醒，低愉悦 - 消极沉静的情绪
        if self.valence <= -0.3 and self.arousal <= 0.4:
            if self.valence < -0.7:
                return "悲伤"
            return "失落"
            
        # 第四象限：低唤醒，高愉悦 - 积极沉静的情绪
        if self.valence >= 0.3 and self.arousal <= 0.4:
            if self.valence > 0.7:
                return "满足"
            return "平静"
            
        # 中性区域
        return "平静"
    
    def update(self, valence_change: float = 0, arousal_change: float = 0):
        """
        更新心情状态
        
        参数:
            valence_change: 愉悦度变化
            arousal_change: 唤醒度变化
        """
        self.valence += valence_change
        self.arousal += arousal_change
        
        # 限制在有效范围内
        self.valence = max(-1.0, min(1.0, self.valence))
        self.arousal = max(0.0, min(1.0, self.arousal))
        
        # 更新文本描述
        self.text = self._get_mood_text()
        
    def __str__(self) -> str:
        """返回心情状态的字符串表示"""
        return f"{self.text} (愉悦度: {self.valence:.2f}, 唤醒度: {self.arousal:.2f})"


class MoodManager:
    """管理角色情绪状态随时间和事件的变化"""
    
    # 情绪关键词映射到(愉悦度变化, 唤醒度变化)
    EMOTION_MAP = {
        # 积极情绪
        "开心": (0.2, 0.1),
        "兴奋": (0.3, 0.3),
        "高兴": (0.2, 0.1),
        "满足": (0.2, -0.1),
        "放松": (0.1, -0.2),
        # 消极情绪
        "悲伤": (-0.2, -0.1),
        "生气": (-0.3, 0.3),
        "愤怒": (-0.4, 0.4),
        "焦虑": (-0.2, 0.2),
        "担忧": (-0.1, 0.1),
        "失望": (-0.2, -0.1),
        # 中性情绪
        "惊讶": (0.1, 0.3),
        "困惑": (-0.1, 0.1),
    }
    
    def __init__(self, character_name: str, decay_rate: float = 0.05):
        """
        初始化心情管理器
        
        参数:
            character_name: 角色名称
            decay_rate: 情绪衰减率（每分钟）
        """
        self.character_name = character_name
        self.mood_state = MoodState()  # 初始心情状态
        self.decay_rate = decay_rate    # 情绪衰减率
        self.last_update_time = datetime.now()  # 上次更新时间
        
    def update_mood(self, message_content: str, sender: str):
        """
        根据消息内容更新心情
        
        参数:
            message_content: 消息内容
            sender: 消息发送者
        """
        # 应用时间衰减
        self._apply_time_decay()
        
        # 分析消息内容
        valence_change, arousal_change = self._analyze_message(message_content, sender)
        
        # 更新心情状态
        self.mood_state.update(valence_change, arousal_change)
        
    def _apply_time_decay(self):
        """随时间将情绪状态衰减回中性"""
        now = datetime.now()
        minutes_passed = (now - self.last_update_time).total_seconds() / 60.0
        
        # 愉悦度向0衰减
        decay_factor = math.exp(-self.decay_rate * minutes_passed)
        self.mood_state.valence *= decay_factor
        
        # 唤醒度向0.5衰减
        arousal_diff = self.mood_state.arousal - 0.5
        self.mood_state.arousal = 0.5 + arousal_diff * decay_factor
        
        # 更新文本描述
        self.mood_state.text = self.mood_state._get_mood_text()
        
        # 更新时间戳
        self.last_update_time = now
        
    def _analyze_message(self, message: str, sender: str) -> Tuple[float, float]:
        """
        分析消息对心情的影响
        
        参数:
            message: 消息内容
            sender: 消息发送者
            
        返回:
            (愉悦度变化, 唤醒度变化)
        """
        valence_change = 0.0
        arousal_change = 0.0
        
        # 检查是否被提及（被提及会增加唤醒度）
        if self.character_name in message:
            arousal_change += 0.1
        
        # 检测情绪关键词
        for emotion, (v_change, a_change) in self.EMOTION_MAP.items():
            if emotion in message:
                valence_change += v_change
                arousal_change += a_change
        
        # 检测问号（疑问可能增加唤醒度）
        if "?" in message or "？" in message:
            arousal_change += 0.05
        
        # 检测感叹号（强调可能增加唤醒度）
        if "!" in message or "！" in message:
            arousal_change += 0.1
        
        # 简单考虑消息长度（长消息可能含更多情感）
        message_length = len(message)
        if message_length > 100:
            arousal_change += 0.05
        
        return valence_change, arousal_change
        
    def get_mood_prompt(self) -> str:
        """获取当前心情状态的提示词"""
        return f"你目前的心情是{self.mood_state.text}。"
    
    def get_current_mood(self) -> MoodState:
        """获取当前心情状态"""
        self._apply_time_decay()  # 确保状态是最新的
        return self.mood_state