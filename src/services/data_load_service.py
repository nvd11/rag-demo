
from pydantic import BaseModel

class DocLoadService(BaseModel):



    def load(self, filepath:str)->Document:
        
        

