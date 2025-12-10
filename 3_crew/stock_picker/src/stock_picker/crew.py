from crewai import Agent, Crew, Process, Task, tools
from crewai import memory
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from pydantic import BaseModel, Field, config
from crewai_tools import SerperDevTool
from .tools.push_tool import PushNotificationTool
from crewai.memory import LongTermMemory, ShortTermMemory, EntityMemory
from crewai.memory.storage.rag_storage import RAGStorage
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage

class TrendingCompany(BaseModel):
    """ A company that is in the news and attracting attention """
    name: str = Field(description='Company name')
    ticker: str = Field(description='Stock ticker symbol')
    reason: str = Field(description='Reason this company is trending in the news')

class TrendingCompanyList(BaseModel):
    ''' List of multiple trending companies that are in the news '''
    companies: List[TrendingCompany] = Field(description='List of companies trending in the news')

class TrendingCompanyResearch(BaseModel):
    ''' Detailed research of a company '''
    name: str = Field(description='Companu Name')
    market_position: str = Field(description='Current market position and competitive analysis')
    future_outlook: str = Field(description='Future outlook and growth prospects')
    investment_potentials: str = Field(description='Investment potential and suitability for investment')

class TrendingComapanyResearchList(BaseModel):
    ''' A list of detailed research on all the companies '''
    research_list: List[TrendingCompany] = Field(description='Comprehensive research on all trending comapnies')

@CrewBase
class StockPicker():
    """StockPicker crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    
    @agent
    def trending_company_finder(self) -> Agent:
        return Agent(
            config=self.agents_config['trending_company_finder'], # type: ignore[index]
            verbose=True,
            tool = [SerperDevTool()],
            memory=True
        )

    @agent
    def financial_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_researcher'], # type: ignore[index]
            verbose=True,
            tool = [SerperDevTool()]
        )

    @agent
    def stock_picker(self) -> Agent:
        return Agent(
            config=self.agents_config['stock_picker'], # type: ignore[index]
            verbose=True,
            tools=[PushNotificationTool()],
            memory=True
        )
    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'], # type: ignore[index]
            output_pydantic=TrendingCompanyList
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'], # type: ignore[index]
            output_pydantic=TrendingComapanyResearchList
        )
    
    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company'], #type: ignore[index]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""

        manager = Agent(
            config=self.agents_config['manager'],
            allow_delegation=True
        )

        short_term_memory = ShortTermMemory(
            storage=RAGStorage(
                embedder_config={
                    'provider': 'openai',
                    'config': {
                        'model': 'text-embedding-3-small'
                    }
                },
                type='short_term',
                path='./memory/'
            )
        )

        long_term_memory = LongTermMemory(
            storage=LTMSQLiteStorage(
                db_path='./memory/long_term_memory_storage.db'
            )
        )

        entity_memory = EntityMemory(
            storage=RAGStorage(
                embedder_config={
                    'provider': 'openai',
                    'config': {
                        'model': 'text-embedding-3-small'
                    }
                },
                type='short-term',
                path='./memory'
            )
        )

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.hierarchical,
            verbose=True,
            manager_agent=manager,
            memory=True,
            long_term_memory=long_term_memory,
            short_term_memory=short_term_memory,
            entity_memory=entity_memory,
        )
