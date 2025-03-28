from dotenv import load_dotenv, find_dotenv

from character import Charactor
from chat_room import ChatRoom

load_dotenv(find_dotenv()) # 加载环境变量, 使用langsmith监控
   
if __name__ == "__main__":
    chat_room = ChatRoom()
    
    # 增加更多角色信息
    chat_room.add_charactor(Charactor('Alice', [0.8, 0.7, 0.8, 0.4]))  # ENFP - 活泼外向，想象力丰富
    chat_room.add_charactor(Charactor('Bob', [0.3, 0.4, 0.3, 0.7]))    # ISTJ - 内向严谨，逻辑性强
    chat_room.add_charactor(Charactor('Charlie', [0.7, 0.3, 0.4, 0.2])) # ESTP - 外向但实际，喜欢冒险
    chat_room.add_charactor(Charactor('Diana', [0.2, 0.8, 0.9, 0.8]))  # INFJ - 深思熟虑，理想主义者

    print(chat_room)
    chat_room.start_chat(5)