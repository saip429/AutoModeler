'''
directory purge module
purges files in a directory and retains recent most files (number specified)
Requires two args: directory path (str), number of files to keep (int)
'''

import os


class PurgeDirectory:
    def __init__(self,purge_path:str, max_files:int)->None:
        self.purge_path=purge_path
        self.max_files=max_files
        self.logs:list=[]
        self.purgeDir()
        

    def purgeDir(self)->list:
    
        try:
            files=[f for f in os.listdir(self.purge_path)]
            files.sort(key=lambda f:os.path.getmtime(os.path.join(self.purge_path,f)))
            files_purge=len(files)-self.max_files
            if files_purge>0:
                files_remove=files[:files_purge]
                for file_to_remove in files_remove:
                    file_path=os.path.join(self.purge_path,file_to_remove)
                    os.remove(file_path)
                    self.logs.append(f"removed: {file_path}")
            else:
                self.logs.append(f'no files in: {self.purge_path}')
            

        except Exception as e:
            raise ValueError(e)
        
    def returnLogs(self):
        return self.logs
    
        





