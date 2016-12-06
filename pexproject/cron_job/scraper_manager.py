import psutil
import time


def kill_children(proc):
    for sub_proc in proc.children(True):
        sub_proc.kill()
    proc.kill()

names = ['node', 'phantomjs', 'Xvfb', 'chromedriver']

for proc in psutil.process_iter():
    """ current time in seconds """
    current_time = time.time()

    try:
        pinfo = proc.as_dict(attrs=['pid', 'ppid', 'name', 'create_time', 'username', 'cwd'])

        """ if orphan process """
        # if pinfo['username'] == 'www-data' and pinfo['name'] in names:
        if pinfo['name'] in names and pinfo['ppid'] == 1:
            kill_children(proc)
        elif pinfo['name'] == 'python' and pinfo['username'] == 'www-data':
            """ for long-running processes """
            # elapsed time in seconds
            duration = int((current_time - pinfo['create_time']))
            if duration > 60 * 3:
                kill_children(proc)

    except psutil.NoSuchProcess:
        pass

