import json
from decimal import Decimal

class CustomEncoder(json.JSONEncoder):


    def default(self,obj,Decimal):
        if isinstance(obj,Decimal):
            return float(Decimal)
        
        return json.JSONEncoder.default(self,obj)
        

