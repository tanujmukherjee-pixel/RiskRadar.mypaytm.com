
class DruidTool:
    name = "Druid"
    description = "Fetch data from Druid"

    def __init__(self):
        pass

    def get_metadata(self) :
        return {"name": self.name, "description": self.description}
    
    def execute(self, query: str) -> str:
        '''
        Execute the query and return the result
        '''
        return "Hello, world!"
