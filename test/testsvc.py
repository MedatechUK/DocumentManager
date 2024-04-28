import win32serviceutil
from MedatechUK.svc import AppSvc
from pathlib import Path
import debugpy

class MySVC(AppSvc):    
    _svc_name_ = "testSVC"
    _svc_display_name_ = "Test Service"    

    def __init__(self,args):    
        self.Main = MySVC.main   
        self.Folder = Path(__file__).parent         
        AppSvc.__init__(self,args)

    def main(self):       
        if self.debug: debugpy.breakpoint()          
            
        self.log.logger.debug(self.clArg.byName(['env','e']))

if __name__ == '__main__':    
    win32serviceutil.HandleCommandLine(MySVC)    