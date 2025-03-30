from dotenv import load_dotenv, find_dotenv
from character import charactor
from chatroom import ChatRoom
from datetime import datetime

load_dotenv(find_dotenv())

if __name__ == "__main__":
    chat_room = ChatRoom()
    chat_room.add_charactor(charactor('David', [0.7, 0.6, 0.8, 0.7], chat_room, background="你是香港大学社会学系的学生，是ENFJ,喜欢组织社交活动和听流行音乐。"
        "你和Emily是同班同学，擅长激发团队灵感；和Helen是学生会同事，欣赏她的细心。"))  # ENFJ
    chat_room.add_charactor(charactor('Emily', [0.6, 0.3, 0.2, 0.8], chat_room, background="你是香港大学社会学系的学生，是ESTJ,喜欢制定计划和喝港式奶茶。"
        "你和David是同班同学，负责落实想法；你是George的堂姐，常叮嘱他。"))  # ESTJ
    chat_room.add_charactor(charactor('George', [0.2, 0.4, 0.3, 0.3], chat_room, background="你是香港大学工程系的学生，是ISTJ,喜欢玩滑板和修电子产品。"
        "你是Emily的堂弟，随性不爱被管；和Helen是社团朋友，帮她修东西。")) # ISTP
    chat_room.add_charactor(charactor('Helen', [0.3, 0.2, 0.7, 0.6], chat_room, background="你是香港大学心理学系的学生，是ISFJ,喜欢做手工艺和吃港式甜品。"
        "你和George是社团朋友，欣赏他独立；和David是学生会同事，视他为领袖。"))  # ISFJ
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