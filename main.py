from dotenv import load_dotenv, find_dotenv
from character import Character
from chatroom import ChatRoom
from datetime import datetime

load_dotenv(find_dotenv())

if __name__ == "__main__":
    chat_room = ChatRoom(initial_message=None)
    chat_room.add_charactor(Character('林一', chat_room, background_path="MBTI_characters\murder（INTJ）.txt"))  # ENFJ
    chat_room.add_charactor(Character('丁二', chat_room, background_path="MBTI_characters\murder（INTJ）.txt"))  # ESTJ
    chat_room.add_charactor(Character('肖九', chat_room, background_path="MBTI_characters\murder（INTJ）.txt")) # ISTP
    chat_room.add_charactor(Character('李四', chat_room, background_path="MBTI_characters\murder（INTJ）.txt"))  # ISFJ
    # # chat_room.add_charactor(charactor('Ivy', [0.4, 0.8, 0.9, 0.4], chat_room))    # INFP
    # # chat_room.add_charactor(charactor('Jack', [0.8, 0.4, 0.7, 0.3], chat_room))   # ESFP
    # # chat_room.add_charactor(charactor('Kelly', [0.9, 0.7, 0.3, 0.2], chat_room))  # ENTP
    # # chat_room.add_charactor(charactor('Lucy', [0.1, 0.9, 0.2, 0.8], chat_room))   # INTJ
    # # chat_room.add_charactor(charactor('Alice', [0.8, 0.7, 0.8, 0.4], chat_room))  # ENFP
    # # chat_room.add_charactor(charactor('Bob', [0.3, 0.4, 0.3, 0.7], chat_room))    # ISTJ
    # # chat_room.add_charactor(charactor('Charlie', [0.7, 0.3, 0.4, 0.2], chat_room))# ESTP
    # # chat_room.add_charactor(charactor('Diana', [0.2, 0.8, 0.9, 0.8], chat_room))  # INFJ
    # # chat_room.add_charactor(charactor('Eve', [0.6, 0.2, 0.8, 0.7], chat_room))    # ESFJ
    # # chat_room.add_charactor(charactor('Frank', [0.4, 0.6, 0.2, 0.3], chat_room))  # INTP
    # # chat_room.add_charactor(charactor('Grace', [0.9, 0.9, 0.4, 0.6], chat_room))  # ENTJ
    # # chat_room.add_charactor(charactor('Henry', [0.1, 0.1, 0.6, 0.1], chat_room))  # ISFP
    chat_room.start_chat(100)