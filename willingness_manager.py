# 聊天意愿管理器类
class WillingnessManger:
    """
    角色聊天意愿管理器：模拟人类自然的聊天兴趣和参与度
    
    属性:
        - willingness: 角色当前的聊天意愿值 (0.0-1.0)
        - name: 角色名称 
        - last_spoke_time: 角色上次发言时间
        - mentioned_boost: 被提及时意愿提升值
        - base_decay: 基础衰减值
    """
    
    def __init__(self, name):
        """初始化意愿管理器"""
        self.willingness = 0.5  # 初始聊天意愿值
        self.name = name
        self.last_spoke_time = None  # 上次发言时间
        self.mentioned_boost = 0.4   # 被提及时意愿提升值
        self.base_decay = 0.05       # 基础衰减值
    
    def update_willingness(self, messages, current_time):
        """
        根据聊天内容和时间更新聊天意愿
        
        参数:
            messages: 最近的聊天消息
            current_time: 当前时间
        """
        # 应用时间衰减
        self._apply_time_decay(current_time)
        
        # 分析最近消息
        recent_msgs = messages[-5:]  # 只分析最近5条消息
        mentioned = self._check_if_mentioned(recent_msgs)
        topic_interest = self._calculate_topic_interest(recent_msgs)
        
        # 更新意愿值
        if mentioned:
            self.willingness += self.mentioned_boost
            
        # 话题兴趣度影响
        self.willingness += topic_interest * 0.2
        
        # 限制范围
        self.willingness = min(max(self.willingness, 0.1), 1.0)
        
        return self.willingness
    
    def _apply_time_decay(self, current_time):
        """随时间衰减聊天意愿"""
        if self.last_spoke_time:
            # 计算自上次发言过去的时间（分钟）
            time_diff = (current_time - self.last_spoke_time).total_seconds() / 60
            
            # 应用衰减
            if time_diff > 1:  # 超过1分钟开始衰减
                decay = min(self.base_decay * time_diff / 5, 0.3)  # 最大衰减0.3
                self.willingness = max(0.1, self.willingness - decay)
    
    def _check_if_mentioned(self, messages):
        """检查是否被提及"""
        for msg in messages:
            if msg.get('sender') != self.name and self.name in msg.get('content', ''):
                return True
        return False
    
    def _calculate_topic_interest(self, messages):
        """计算对当前话题的兴趣度"""
        # 简化实现，实际可以基于角色性格和话题关键词分析
        topic_interest = 0.0
        
        # 提取最后一条非自己发的消息
        other_messages = [msg for msg in messages if msg.get('sender') != self.name]
        if not other_messages:
            return topic_interest
            
        last_msg = other_messages[-1]['content']
        
        # 简单规则：消息越长，可能越有讨论价值
        msg_length = len(last_msg)
        if msg_length > 100:
            topic_interest += 0.2
        elif msg_length > 50:
            topic_interest += 0.1
            
        # 检测问句（简化实现）
        if '?' in last_msg or '？' in last_msg:
            topic_interest += 0.15
            
        return topic_interest
    
    def message_sent(self, current_time):
        """发送消息后更新状态"""
        self.last_spoke_time = current_time
        # 说话后稍微降低意愿（模拟人类说完话后会有短暂的"听"的阶段）
        self.willingness = max(0.2, self.willingness - 0.3)
        
    def get_response_probability(self):
        """根据当前意愿值计算回应概率"""
        # 非线性映射，使中等意愿时反应更自然
        if self.willingness > 0.8:
            return min(0.95, self.willingness)
        elif self.willingness > 0.5:
            return self.willingness * 0.8
        else:
            return self.willingness * 0.5