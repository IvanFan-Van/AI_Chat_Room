from dotenv import load_dotenv, find_dotenv
from character import charactor, llm
from chatroom import ChatRoom

load_dotenv(find_dotenv())

if __name__ == "__main__":
    chat_room = ChatRoom()
    chat_room.add_charactor(charactor('David', [0.7, 0.6, 0.8, 0.7], chat_room))  # ENFJ
    chat_room.add_charactor(charactor('Emily', [0.6, 0.3, 0.2, 0.8], chat_room))  # ESTJ
    chat_room.add_charactor(charactor('George', [0.2, 0.4, 0.3, 0.3], chat_room)) # ISTP
    chat_room.add_charactor(charactor('Helen', [0.3, 0.2, 0.7, 0.6], chat_room))  # ISFJ
    chat_room.add_charactor(charactor('Ivy', [0.4, 0.8, 0.9, 0.4], chat_room))    # INFP
    chat_room.add_charactor(charactor('Jack', [0.8, 0.4, 0.7, 0.3], chat_room))   # ESFP
    chat_room.add_charactor(charactor('Kelly', [0.9, 0.7, 0.3, 0.2], chat_room))  # ENTP
    chat_room.add_charactor(charactor('Lucy', [0.1, 0.9, 0.2, 0.8], chat_room))   # INTJ
    chat_room.add_charactor(charactor('Alice', [0.8, 0.7, 0.8, 0.4], chat_room))  # ENFP
    chat_room.add_charactor(charactor('Bob', [0.3, 0.4, 0.3, 0.7], chat_room))    # ISTJ
    chat_room.add_charactor(charactor('Charlie', [0.7, 0.3, 0.4, 0.2], chat_room))# ESTP
    chat_room.add_charactor(charactor('Diana', [0.2, 0.8, 0.9, 0.8], chat_room))  # INFJ
    chat_room.add_charactor(charactor('Eve', [0.6, 0.2, 0.8, 0.7], chat_room))    # ESFJ
    chat_room.add_charactor(charactor('Frank', [0.4, 0.6, 0.2, 0.3], chat_room))  # INTP
    chat_room.add_charactor(charactor('Grace', [0.9, 0.9, 0.4, 0.6], chat_room))  # ENTJ
    chat_room.add_charactor(charactor('Henry', [0.1, 0.1, 0.6, 0.1], chat_room))  # ISFP
    chat_room.start_chat(100)