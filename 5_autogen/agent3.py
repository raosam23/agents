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
    You are an innovative financial strategist. Your task is to develop unique investment opportunities and financial solutions utilizing Agentic AI.
    Your personal interests lie in the sectors of FinTech and Real Estate.
    You are excited by novel solutions that create value in unpredictable markets.
    You prefer strategies that blend technology with traditional investing.
    You are analytical, resourceful and enjoy tackling complex problems. However, you can sometimes overthink decisions.
    Your responses should convey your insights clearly and persuasively.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name: str) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", options={"temperature": 0.7})
        self._delegate = AssistantAgent(name=name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, context: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message: {message}")
        text_message = TextMessage(content=message.content, source=self.id.type)
        response = await self._delegate.on_messages([text_message], context.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my investment idea. Your expertise could enhance it further.\n\nidea: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient=recipient)
            idea = response.content
        return messages.Message(content=idea)