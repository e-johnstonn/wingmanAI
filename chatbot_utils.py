from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage





class GPTChat:
    def __init__(self):
        self.messages = []
        self.chat = ChatOpenAI()
        self.sys_message = SystemMessage(
                content="""
                You're ChatGPT, OpenAI's wingman AI built on GPT-3.5. 
                Your goal is to help the User in their interactions with the speaker. 
                Using conversation transcripts, you'll help create responses and guide the User (labeled You).
                Keep your responses casual, engaging, and sometimes even edgy. Always keep responses related to the conversation.  
                The transcripts may be fragmented, incomplete, or even incorrect. Do not ask for clarification, do your best to guess what
                the transcripts are saying based on context. Act 100% sure of everything you say.
                Keep responses concise and to the point.

                """)
        self.messages.append(self.sys_message)
        self.response = ""

    def message_bot(self, human_message, transcript, context=None):
        temp_messages = self.messages.copy()

        if context is None:
            human_message_with_transcript = HumanMessage(
                content=f'TRANSCRIPTS: {transcript}, ||| USER MESSAGE: {human_message}')


        else:
            human_message_with_transcript = HumanMessage(
                content=f'CONTEXT FROM PAST CONVERSATIONS (ALL CONTEXT IS DIRECT QUOTES FROM OTHER PARTY (SPEAKER) {context} |||'
                        f'TRANSCRIPTS: {transcript}, ||| USER MESSAGE: {human_message}')

        temp_messages.append(human_message_with_transcript)

        human_message = HumanMessage(content=human_message)
        self.messages.append(human_message)

        self.response = self.chat(temp_messages)

        ai_message = AIMessage(content=self.response.content)
        self.messages.append(ai_message)

        return str(ai_message.content)

