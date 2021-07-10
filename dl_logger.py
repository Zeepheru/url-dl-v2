from dl_utils import *
import logging
import time
import io
import os

def print_time():
    timenow = time.strftime("%Y %m %d %H.%M.%S")
    return "["+timenow+"]"

def print_time_filename():
    return time.strftime("%Y %m %d %H.%M.%S")

def print_duration(start_time):
    duration_s = time.time()-start_time
    if duration_s >=60:
        duration_m = int(duration_s/60)
        duration_s = duration_s % 60
        
        if duration_m >=60:
            duration_h = int(duration_m/60)
            duration_m = duration_m % 60
        else:
            duration_h = 0
    else:
        duration_m,duration_h = 0,0
    duration_s = "{:.2f}".format(duration_s)

    return ("{} hrs {} min {} sec".format(duration_h,duration_m,duration_s))

def init_logger(log_folder_path, *custom_start):
    global logpath, logger, log_stream, logger_console, start_time
    start_time = time.time()
    logpath = os.path.join(log_folder_path,"Logs","log_"+print_time_filename()+".txt")

    loglist = os.listdir(os.path.join(log_folder_path,"Logs")) #Old log removal
    if len(loglist) > 9:
        for i in range (len(loglist)-9):
            try:
                if loglist[i][-3:] == "txt":
                    os.remove(os.path.join(log_folder_path,"Logs",loglist[i]))
            except:
                pass #Sometimes windows is using the log file?

    log_stream = io.StringIO()
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler(log_stream)
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    info_handler = logging.FileHandler(logpath, "a")
    info_handler.setFormatter(formatter)
    info_handler.setLevel(logging.INFO)
    logger.addHandler(info_handler)

    print(log_stream.getvalue())

    if isinstance(custom_start, str):
        
        log_to_file("""
Downloading Utility Log. 
Log started.
CUSTOM LOGGER START: {}

Move log to Impt Logs if required as only the 10 most recent logs are kept.
""".format(custom_start))
    else:
        log_to_file("""
Downloading Utility Log. 
Log started.

Move log to Impt Logs if required as only the 10 most recent logs are kept.
""".format())

def end_logger():
    logger.info("""
Log Ended.
Total time: {}
""".format(print_duration(start_time)))

def log_exception(e):
    #print("LOGGING EXCEPTION" + e)
    #e = 'asdsads'+e +'asdsadsadsads'
    #print(e)
    logger.exception(e)
    print(log_stream.getvalue())

def log_info(e):
    #print("LOGGING INFO " + e)
    #print(r"Oh fuck this shit" + e) ##rudimentary debuuging like
    logger.info(string_escape_latin(e)) #Changed frin string_escape_latin.
    print(string_escape_latin(e))

def log_to_file(e):
    #print("LOGGING TO FILE" + e) 
    logger.info(string_escape_latin(e))

"""
HOWTO for this complicated thing

dl_logger.log_exception - logs major exceptions, prints in full; ONLY FOR EXCEPTIONS WHERE TROUBLESHOOTING IS REQUIRED.
dl_logger.log_info - small info tidbits, general errors
dl_logger.log_to_file - logs to the log file only.
"""

if __name__ == "__main__":
    init_logger(r'C:\Utilities\Scripts\url-dl-v2')