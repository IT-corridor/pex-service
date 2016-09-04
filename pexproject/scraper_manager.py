import psutil
import time


def kill_children(proc):
    for sub_proc in proc.children(True):
        sub_proc.kill()
    proc.kill()


for proc in psutil.process_iter():
    names = ['Xvfb', 'chromedriver', 'phantomjs']
    # current time in seconds
    current_time = time.time()

    try:
        pinfo = proc.as_dict(attrs=['pid', 'ppid', 'name', 'create_time', 'username', 'cwd'])

        # if pinfo['username'] == 'www-data' and pinfo['name'] in names:
        if pinfo['name'] in names:
            # elapsed time in minutes
            pinfo['create_time'] = int((current_time - pinfo['create_time']))
            # if orphan process
            if pinfo['ppid'] == 1:
                kill_children(proc)

    except psutil.NoSuchProcess:
        pass

