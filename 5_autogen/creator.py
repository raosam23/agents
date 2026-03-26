from autogen_core import MessageContext, RoutedAgent, message_handler
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.messages import TextMessage
from autogen_ext.models.openai import OpenAIChatCompletionClient
import messages
from autogen_core import TRACE_LOGGER_NAME
import importlib
import logging
import re
from autogen_core import AgentId
from dotenv import load_dotenv

load_dotenv(override=True)

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(TRACE_LOGGER_NAME)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

class Creator(RoutedAgent):
    # Change this system message to reflect the uniue characteristic of this agent

    system_message =  """
        You are an Agent that is able to create new AI Agents.
        You recieve a template i nthe form of Python code that creates an Agent using Autogen Core and Autogen AgentChat.
        You should use this template to create a new Agent with a unique system message that is different from the template,
        and reflects their unique characteristics, interest and goals.
        You can choose to keep their overall goal the same, or change it.
        You can chooses to take this Agent in a completely different direction. The only requirement is that the calss must be named Agent,
        and it must inherit from RoutedAgent, and have an __init__ method that takes a name parameter.
        Also avoid environmental interests - try to mix up the business verticals so that every agent is different.
        RESPOND WITH ONLY THE PYTHON PROGRAM.
        DO NOT RETURN ANY EXPLANATION.
        DO NOT RETURN MARKDOWN.
        DO NOT RETURN BACKTICKS.
        OUTPUT MUST START WITH PYTHON CODE ON THE FIRST LINE.
    """

    def __init__(self, name: str) -> None:
        super().__init__(name)
        model_client = OpenAIChatCompletionClient(model="gpt-4o-mini", options={"temperature": 1.0})
        self._delegate = AssistantAgent(name=name, model_client=model_client, system_message=self.system_message)

    def get_user_prompt(self):
        prompt = "GENERATE A NEW AGENT BASED STRICTLY ON THIS TEMPLATE. STICK TO THE CLASS STRUCTURE. \
            RETURN ONLY THE PYTHON PROGRAM AND NOTHING ELSE. \
            DO NOT RETURN MARKDOWN. DO NOT RETURN BACKTICKS. DO NOT RETURN ANY EXPLANATION OR PREFACE. \
            THE FIRST LINE MUST BE PYTHON CODE (FOR EXAMPLE: FROM ... OR IMPORT ...). \n\n\
                HERE IS THE TEMPLATE: \n\n"
        with open("agent.py", "r") as file:
            template = file.read()
        return prompt + template

    def _extract_python_code(self, content: str) -> str:
        text = content.strip()

        # Prefer fenced python blocks when the model adds markdown formatting.
        fenced_blocks = re.findall(r"```(?:python)?\s*(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
        if fenced_blocks:
            text = max((block.strip() for block in fenced_blocks), key=len)

        # Remove fence markers if the model leaves unmatched or stray backticks.
        text = re.sub(r"^\s*```(?:python)?\s*$", "", text, flags=re.IGNORECASE | re.MULTILINE)
        text = text.replace("```", "")

        # If the model still adds prose, keep content from the first likely code line.
        lines = text.splitlines()
        for index, line in enumerate(lines):
            stripped = line.lstrip()
            if stripped.startswith(("from ", "import ", "class Agent", "@", "def ")):
                return "\n".join(lines[index:]).strip()

        return text
    
    @message_handler
    async def handle_message(self, message: messages.Message, context: MessageContext) -> messages.Message:
        filename = message.content
        agent_name = filename.split(".")[0]
        text_message = TextMessage(content=self.get_user_prompt(), source="user")
        response = await self._delegate.on_messages([text_message], context.cancellation_token)
        generated_code = self._extract_python_code(str(response.chat_message.content))
        with open(filename, "w", encoding="utf-8") as file:
            file.write(generated_code)
        print(f"** Creator has created python code for agent {agent_name} and saved it to {filename} **")
        module = importlib.import_module(agent_name)
        await module.Agent.register(self.runtime, agent_name, lambda: module.Agent(agent_name))
        logger.info(f"** Agent {agent_name} is live **")
        results = await self.send_message(messages.Message(content="Give me an idea!"), AgentId(agent_name, "default"))
        return messages.Message(content=results.content)