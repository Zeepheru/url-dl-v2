class RunInfo(): #todo import this class in all files
    def __init__(self):
        self.target_status = None
        self.settings = {}
        self.objects_list = []
        self.current = 0

    def get_duration(self): #duration in seconds
        breakpoint()
        return time.time() - self.start_time

        def beautify(): #Deal with this later
            duration_s = time.time()-start_time_int
            if duration_s >= 60:
                duration_m = int(duration_s/60)
                duration_s = duration_s % 60
                
                if duration_m >= 60:
                    duration_h = int(duration_m/60)
                    duration_m = duration_m % 60
                else:
                    duration_h = 0
            else:
                duration_m,duration_h = 0,0
            duration_s = "{:.2f}".format(duration_s)

    def lol():
        pass

class DownloadObject():
    def __init__(self):
        self.object_type = None
        self.site = None
        self.data = {}
        self.download_info = {}