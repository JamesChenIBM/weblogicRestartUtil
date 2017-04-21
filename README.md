# weblogicRestartUtil
This Jython script stops / starts / restart / healthcheck Weblogic domain in a defined fashion. For example, rolling restart fashion.
Run on windows:

C:\Oracle\Middleware\WLS1221\user_projects\domains\TEST\bin\startNodeManager.cmd

C:\Oracle\Middleware\WLS1221\user_projects\domains\TEST\bin\setDomainEnv.cmd

cd C:\Users\jchen\work\WLRestartUtil\src


java weblogic.WLST  WLSRestartUtil.py wlsRestartUtil.template.properties healthcheck


Step 1: 
Download script from git

Modify template.properties

Step 4: Run the following command to create keys
./runWLST.ksh createWLkey.py <new template property file>

runWLST.ksh webopsRestartUtil.py osb.restart.properties restart

1.Create a script and place in /etc/init.d (e.g /etc/init.d/myscript). 
The script should have the following format:

#!/bin/bash
# chkconfig: 2345 20 80
# description: Description comes here....

# Source function library.
. /etc/init.d/functions

start() {
    # code to start app comes here 
    # example: daemon program_name &
}

stop() {
    # code to stop app comes here 
    # example: killproc program_name
}

case "$1" in 
    start)
       start
       ;;
    stop)
       stop
       ;;
    restart)
       stop
       start
       ;;
    status)
       # code to check status of app comes here 
       # example: status program_name
       ;;
    *)
       echo "Usage: $0 {start|stop|status|restart}"
esac

exit 0 

The format is pretty standard and you can view existing scripts in /etc/init.d. 
You can then use the script like so /etc/init.d/myscript start or chkconfig 
myscript start. The ckconfig man page explains the header of the script:
  This says that the script should be started in levels 2,  3,  4, and   5, 
  that its start priority should be 20, and that its stop priority should be 80.

The example start, stop and status code uses helper functions defined in /etc/init.d/functions

2.Enable the script 
chkconfig --add myscript 
chkconfig --level 2345 myscript on 

3.Check the script is indeed enabled - you should see "on" for the levels you selected. 
chkconfig --list | grep myscript
 
