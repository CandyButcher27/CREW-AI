from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class MyCrew():
    """MyDebate crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

   
    @agent
    def debator(self) -> Agent:
        return Agent(
            config=self.agents_config['debator'], # type: ignore[index]
            verbose=True
        )

    @agent
    def judge(self) -> Agent:
        return Agent(
            config=self.agents_config['judge'], # type: ignore[index]
            verbose=True
        )

   
    @task
    def propose_motion(self) -> Task:
        return Task(
            config=self.tasks_config['propose_motion'], # type: ignore[index]
        )

    @task
    def oppose_motion(self) -> Task:
        return Task(
            config=self.tasks_config['oppose_motion'], # type: ignore[index]
        )
    
    @task
    def decide(self) -> Task:
        return Task(
            config=self.tasks_config['decide'], # type: ignore[index]
        )
    


    @crew
    def crew(self) -> Crew:
        """Creates the MyCrew crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
