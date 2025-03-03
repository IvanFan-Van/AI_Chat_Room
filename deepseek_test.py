from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages

#=====初始化LLM=====
from langchain_deepseek import ChatDeepSeek
llm = ChatDeepSeek(
    model="deepseek-chat",
    api_key="sk-34442cc84ebb4894b2eb884b3a6cd7f1"  # 替换实际密钥
)

#=====定义角色类和聊天室类=====
class charactor():
    '''角色类:包括名字，mbti，背景故事，心理活动'''
    name = 'undefined'
    mbti = [0.5, 0.5, 0.5, 0.5] #1/0 1st: E/I, 2nd: N/S, 3rd: F/T, 4th: J/P
    background = 'undefined'
    
    def __init__(self, name, mbti):
        self.name = name
        self.mbti = mbti
        self.background = '你是'+self.name+'。'
    
class chat_room():
    '''聊天室类:包括角色列表，当前对话记录'''
    num_charactors = 0
    charactors = []
    chat_record: Annotated[list, add_messages] = []
    chat_background = '模拟聊天背景：你是一名大学生。你现在正与同在一所大学的朋友进行日常对话，聊天内容如下，请继续。要求：使用日常语言回复，使用中文，不用在回答前面加名字和冒号，别重复之前说过的话，每次回复不超过50字。'
    def __init__(self):
        pass

    def add_charactor(self, charactor):
        self.num_charactors += 1
        self.charactors.append(charactor)

    def start_chat(self, chat_length):
        for i in range(chat_length):
            print("[%d]" % (i+1))
            # user_input = input("User: ")
            # self.chat_record.append({"role": "human", "content": "Gao:" + user_input})

            for charactor in self.charactors:
                #print(self.chat_record)
                response = llm.invoke(self.chat_record + [charactor.background + self.chat_background])
                self.chat_record.append({"role": 'ai', "content": charactor.name + ": " + response.content})
                print(charactor.name + ":" + response.content)
        
ChatRoom = chat_room()
ChatRoom.add_charactor(charactor('Alice', [0.5, 0.5, 0.5, 0.5]))
ChatRoom.add_charactor(charactor('Bob', [0.5, 0.5, 0.5, 0.5]))

ChatRoom.start_chat(10)