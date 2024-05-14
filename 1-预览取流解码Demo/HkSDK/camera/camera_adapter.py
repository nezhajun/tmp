
from ..core.base_adapter import BaseAdapter,GetPlatform,WINDOWS_FLAG

class CameraAdapter(BaseAdapter):
    def __init__(self, id=None, name=None) -> None:
        self.id = id
        self.name = name
        err = self.sdk_init()
        
    

        
    
        

