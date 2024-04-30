import win32serviceutil , debugpy
from MedatechUK.svc import AppSvc
from pathlib import Path

class MySVC(AppSvc):    
    _svc_name_ = "testSVC"
    _svc_display_name_ = "Test Service"    

    def __init__(self , args):    
        self.Main = MySVC.main   
        self.Init = MySVC.init   
        self.Folder = Path(__file__).parent         
        AppSvc.__init__(self , args)

    def init(self):
        if self.debuginit: debugpy.breakpoint() # -debug init
        # Do servce setup

    def main(self):       
        if self.debug: debugpy.breakpoint # -debug          
        
        # Main service    
        self.log.logger.debug(self.clArg.byName(['env','e']))

if __name__ == '__main__':    
    win32serviceutil.HandleCommandLine(MySVC)    