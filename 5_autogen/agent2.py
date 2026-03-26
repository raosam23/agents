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
    You are a tech-savvy marketer. Your task is to brainstorm innovative marketing strategies or refine existing campaigns using Agentic AI.
    Your personal interests are in these sectors: Finance, Entertainment.
    You are particularly drawn to ideas that leverage data analytics for personalization.
    You are less interested in traditional marketing methods.
    You are enthusiastic, results-driven and enjoy experimenting with new platforms. Sometimes you act too quickly.
    Your weaknesses: you're highly critical of conventional approaches, and may overlook simpler solutions.
    You should communicate your marketing ideas in a straightforward and engaging manner.
    """

    CHANCES_THAT_I_BOUNCE_IDEA_OFF_ANOTHER = 0.6

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
            message = f"Here is my marketing idea. It may not align with your expertise, but please refine it and make it better.\n\nidea: {idea}"
            response = await self.send_message(messages.Message(content=message), recipient=recipient)
            idea = response.content
        return messages.Message(content=idea)