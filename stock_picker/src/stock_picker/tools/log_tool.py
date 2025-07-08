from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field



class LogInput(BaseModel):
    """A message to be logged into a file"""
    message: str = Field(..., description="Message to be logged for the user")

class LogTool(BaseTool):
    name: str = "Log Tool"
    description: str = (
        "This tool logs a message for the user."
    )
    args_schema: Type[BaseModel] = LogInput

    def _run(self, message: str) -> str:
        # Implementation goes here
        with open("logging/output_log.txt", "w") as log_file:
            log_file.write(message)
        print("I have been used")

        return "The output has been logged in logging/output_log.txt"
