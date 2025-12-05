from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class Debate():
    """Debate crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def debater(self) -> Agent:
        return Agent(
            config=self.agents_config['debater'], # type: ignore[index]
            verbose=True
        )

    @agent
    def judge(self) -> Agent:
        return Agent(
            config=self.agents_config['judge'], # type: ignore[index]
            verbose=True
        )

    @task
    def propose_task(self) -> Task:
        return Task(
            config=self.tasks_config['propose_task'], # type: ignore[index]
        )

    @task
    def oppose_task(self) -> Task:
        return Task(
            config=self.tasks_config['oppose_task'], # type: ignore[index]
        )

    @task
    def decide_task(self) -> Task:
        return Task(
            config=self.tasks_config['decide_task'], # type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Debate crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
