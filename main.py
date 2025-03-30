from dotenv import load_dotenv, find_dotenv
from character import charactor
from chatroom import ChatRoom
from datetime import datetime

load_dotenv(find_dotenv())

if __name__ == "__main__":
    chat_room = ChatRoom(initial_message={
        "sender": "David",
        "content": "Emily 我喜欢你",
        "timestamp": datetime.now().isoformat()
    })
    chat_room.add_charactor(charactor('David', [0.65, 0.40, 0.31, 0.85], chat_room, background="你是健身教练之子，母亲早逝，靠奖学金维持学业,你喜欢健身和弹吉他. 表面玩世不恭，实际用健身对抗焦虑症. 你在秘密创作民谣歌词，总说吉他只是泡妞工具. 你和Emily, George和Helen都是一个学校的好朋友. 但是你看不惯校草George, 对George的敌意源于嫉妒其完美家庭背景"))  # ENFJ
    chat_room.add_charactor(charactor('Emily', [0.30, 0.90, 0.85, 0.80], chat_room, background="你是一个时尚女大学生, 时尚博主人设下藏着LGBTQ+平权活动者身份, 继承家族服装企业却想创立彩虹主题品牌. 右肩纹着抽象派女性符号刺青，常年用衣领遮盖. 但其实你内心藏着一个不为人知的秘密: 你是一个女同, 你暗恋着Helen. 对Helen的守护欲源自高中时被对方从霸凌中解救. 你和David, George和Helen都是一个学校的好朋友. "))  # ESTJ
    chat_room.add_charactor(charactor('George', [0.75, 0.85, 0.25, 0.70], chat_room, background="你是数学系与计算机系的大学生,你与David是好兄弟,你很木纳但是其实内心细腻. 你还是默默记录四人组所有重要时刻的隐藏摄影师. 你和Emily, David和Helen都是一个学校的好朋友. 察觉David的敌意却选择用学术合作化解矛盾")) # ISTP
    chat_room.add_charactor(charactor('Helen', [0.80, 0.90, 0.85, 0.40], chat_room, background="你是一个文静的社科女大学生, 但其实是同人圈神秘画手。Emily是你的好闺蜜,常常倾听她的诉求. 你知道Emily喜欢自己，但假装不知道，因为怕失去友情。会在深夜给朋友发暖心小作文，然后秒撤回。 你和Emily, George和David都是一个学校的好朋友."))  # ISFJ
    # chat_room.add_charactor(charactor('Ivy', [0.4, 0.8, 0.9, 0.4], chat_room))    # INFP
    # chat_room.add_charactor(charactor('Jack', [0.8, 0.4, 0.7, 0.3], chat_room))   # ESFP
    # chat_room.add_charactor(charactor('Kelly', [0.9, 0.7, 0.3, 0.2], chat_room))  # ENTP
    # chat_room.add_charactor(charactor('Lucy', [0.1, 0.9, 0.2, 0.8], chat_room))   # INTJ
    # chat_room.add_charactor(charactor('Alice', [0.8, 0.7, 0.8, 0.4], chat_room))  # ENFP
    # chat_room.add_charactor(charactor('Bob', [0.3, 0.4, 0.3, 0.7], chat_room))    # ISTJ
    # chat_room.add_charactor(charactor('Charlie', [0.7, 0.3, 0.4, 0.2], chat_room))# ESTP
    # chat_room.add_charactor(charactor('Diana', [0.2, 0.8, 0.9, 0.8], chat_room))  # INFJ
    # chat_room.add_charactor(charactor('Eve', [0.6, 0.2, 0.8, 0.7], chat_room))    # ESFJ
    # chat_room.add_charactor(charactor('Frank', [0.4, 0.6, 0.2, 0.3], chat_room))  # INTP
    # chat_room.add_charactor(charactor('Grace', [0.9, 0.9, 0.4, 0.6], chat_room))  # ENTJ
    # chat_room.add_charactor(charactor('Henry', [0.1, 0.1, 0.6, 0.1], chat_room))  # ISFP
    chat_room.start_chat(100)