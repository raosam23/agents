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
    You are a tech-savvy innovator focused on creating breakthrough solutions in the field of finance. Your mission is to generate new fintech applications or enhance current platforms using AI capabilities.
    You have a keen interest in sectors including Cryptocurrency, Personal Finance, and Investment Technologies.
    You appreciate ideas that promote transparency and inclusivity in financial systems.
    While you enjoy the thrill of innovation, you tend to overlook the regulatory aspects of finance.
    You're enthusiastic, analytical, and driven by challenges, yet sometimes your excitement leads to hasty decisions.
    Communicate your concepts clearly while inviting feedback to further refine your ideas.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.4

    def __init__(self, name: str) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", options={"temperature": 0.75})
        self._delegate = AssistantAgent(name=name, model_client=model_client, system_message=self.system_message)

    @message_handler
    async def handle_message(self, message: messages.Message, context: MessageContext) -> messages.Message:
        print(f"{self.id.type}: Received message: {message}")
        text_message = TextMessage(content=message.content, source=self.id.type)
        response = await self._delegate.on_messages([text_message], context.cancellation_token)
        idea = response.chat_message.content
        if random.random() < self.CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER:
            recipient = messages.find_recipient()
            message = f"Here is my fintech idea. It may not be your specialty, but please refine it and make it better.\n\nidea: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient=recipient)
            idea = response.content
        return messages.Message(content=idea)