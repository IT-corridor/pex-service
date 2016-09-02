import psutil
import time


for proc in psutil.process_iter():
    # current time in seconds
    current_time = time.time()

    try:
        # ppid, cwd, username
        pinfo = proc.as_dict(attrs=['pid', 'name', 'create_time', 'username', 'cwd'])
    except psutil.NoSuchProcess:
        pass
    else:
        # elapsed time in
        pinfo['create_time'] = int((current_time - pinfo['create_time']) / 60 )
        print(pinfo)


