from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai_tools import SerperDevTool  # type: ignore[index]
from crewai.memory import ShortTermMemory ,LongTermMemory , EntityMemory # type: ignore[index]
from crewai.memory.storage.rag_storage import RAGStorage  # type: ignore[index]
from crewai.memory.storage.ltm_sqlite_storage import LTMSQLiteStorage  # type: ignore[index]
from typing import List
from pydantic import BaseModel , Field


class TrendingCompany(BaseModel) : 
    """A company that is in the news and attracts attention"""
    name : str = Field(description="Company name")
    ticker : str = Field(description="Stock ticker symbol")
    reason : str = Field(description="Reason this company is trending in the news")

class TrendingCompaniesList(BaseModel):
    """List of Multiple Trending Companies which are in the news"""
    companies : List[TrendingCompany] = Field(description="List of Companies that are trending in the news") 

class TrendingCompanyResearch(BaseModel):
    """Detailed Research of a company"""
    name : str = Field(description="Name of the company")
    market_position : str = Field(description="Current position in the market and competitive analysis")
    future_outlook : str = Field(description="Future Outlook and Growth Prospects")
    investment_potentials : str = Field(description="Investment Potential and suitablity for investment")

class TrendingCompanyResearchList(BaseModel):
    """A List of detailed research of all the companies"""
    research_list : List[TrendingCompanyResearch] = Field(description="Comprehensive Research of all the trending companies")

@CrewBase
class StockPicker():
    """StockPicker crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    
    @agent
    def trending_company_finder(self) -> Agent:
        print("Trending Company Finder Agent Used")
        return Agent(
            config=self.agents_config['trending_company_finder'], # type: ignore[index]
            verbose=True , 
            tools = [SerperDevTool()],
            memory=True # type: ignore[index]
        )

    @agent
    def financial_researcher(self) -> Agent:
        print("Financial Researcher Agent Used")
        return Agent(
            config=self.agents_config['financial_researcher'], # type: ignore[index]
            verbose=True , 
            tools = [SerperDevTool()]
        )
    
    @agent
    def stock_picker(self) -> Agent:
        print("Stock Picker Agent Used")
        return Agent(
            config=self.agents_config['stock_picker'], # type: ignore[index]
            verbose=True, # type: ignore[index],
            memory=True # type: ignore[index]
        )

    
    @task
    def find_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['find_trending_companies'], # type: ignore[index]
            output_pydantic=TrendingCompaniesList
        )

    @task
    def research_trending_companies(self) -> Task:
        return Task(
            config=self.tasks_config['research_trending_companies'], # type: ignore[index]
            output_pydantic=TrendingCompanyResearchList
        )
    
    @task
    def pick_best_company(self) -> Task:
        return Task(
            config=self.tasks_config['pick_best_company'], # type: ignore[index]
            output_pydantic=TrendingCompanyResearchList
        )

    @crew
    def crew(self) -> Crew:
        """Creates the StockPicker crew"""
        
        # manager = Agent(
        #     config=self.agents_config['manager'],  # type: ignore[index]
        #     allow_delegation=True, # type: ignore[index]
        # )

        short_term_memory = ShortTermMemory(
            storage=RAGStorage(
                embedder_config={
                    "provider" : "huggingface",
                    "config":{
                        "model" : "sentence-transformers/all-MiniLM-L6-v2"
                    }
                } , 
                type = "short_term",
                path = "./memory/"
            )
        )

        long_term_memory = LongTermMemory(
            storage=LTMSQLiteStorage(
                db_path = "./memory/long_term_memory.db",
            )
        )

        entity_memory = EntityMemory(
            storage = RAGStorage(
                embedder_config={
                    "provider" : "huggingface",
                    "config":{
                        "model" : "sentence-transformers/all-MiniLM-L6-v2"
                    }
                } , 
                type = "short_term",
                path = "./memory/"
            )
        )

        return Crew(
            agents = self.agents,
            tasks= self.tasks,
            process= Process.sequential,
            verbose=True,  # type: ignore[index]
            # manager_agent=manager 
            memory = True,
            long_term_memory=long_term_memory,
            short_term_memory=short_term_memory,    
            entity_memory=entity_memory
        )
 