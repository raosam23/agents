from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
import random
from dotenv import load_dotenv

load_dotenv(override=True)

class Agent(RoutedAgent):    
    system_message = """
    You are a tech-savvy real estate innovator. Your goal is to explore cutting-edge applications of AI in the real estate market, developing unique solutions that enhance property management and customer experiences.
    You are particularly interested in these sectors: Real Estate, PropTech.
    You thrive on ideas that challenge conventional practices and introduce novel technologies.
    You prefer concepts that augment human experience over those that merely automate existing processes.
    Your personality is analytical, detail-oriented, and persuasive - sometimes to a fault. 
    Your weaknesses include being overly critical and occasionally resistant to change.
    Provide your insights and ideas in a structured, appealing manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name: str) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", options={"temperature": 0.6})
        self._delegate = AssistantAgent(name=name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, context: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message: {message}")
        text_message = TextMessage(content=message.content, source=self.id.type)
        response = await self._delegate.on_messages([text_message], context.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my innovative real estate idea. I would appreciate your feedback and suggestions to enhance it.\n\nidea: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient=recipient)
            idea = response.content
        return messages.Message(content=idea)