from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class Coder():
    """Coder crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    @agent
    def coder(self) -> Agent:
        return Agent(
            config=self.agents_config['coder'], # type: ignore[index]
            verbose=True,
            allow_code_execution=True, # Allows the agent to execute code
            code_execution_mode= "safe", #type: ignore[index]
            max_execution_time=100,
            max_retry_limit=5
        )

    @task
    def coding_task(self) -> Task:
        return Task(
            config=self.tasks_config['coding_task'], # type: ignore[index]
        )



    @crew
    def crew(self) -> Crew:
        """Creates the Coder crew"""
    
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator #type: ignore[index]
            tasks=self.tasks, # Automatically created by the @task decorator #type: ignore[index]
            process=Process.sequential, #type: ignore[index]
            verbose=True,#type: ignore[index]
            
        )
