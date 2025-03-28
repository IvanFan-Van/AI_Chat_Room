from typing import Annotated, TypedDict

# =====定义消息类型=====
class Message(TypedDict):
    sender: str
    content: str    # 实际对话内容（response部分）
    timestamp: str  # 添加时间戳
    thought: str    # 内心想法（think部分），对其他角色不可见
