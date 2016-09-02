import psutil
import time

names = ['chrome', 'nacl_helper', 'Xvfb', 'chromedriver', 'cat', 'phantomjs']

for proc in psutil.process_iter():
    # current time in seconds
    current_time = time.time()

    try:
        # ppid, cwd, username
        pinfo = proc.as_dict(attrs=['pid', 'ppid', 'name', 'create_time', 'username', 'cwd'])
        # elapsed time in minutes
        pinfo['create_time'] = int((current_time - pinfo['create_time']))

        if pinfo['username'] == 'www-data' and pinfo['create_time'] > 150 and pinfo['name'] in names:
            print pinfo['pid'], pinfo['name']
            proc.kill()

    except psutil.NoSuchProcess:
        pass


