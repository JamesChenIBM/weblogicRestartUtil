"""
Author: jms_chn@yahoo.com
"""

import sys, urllib
import os.path
import thread
import time
from time import gmtime, strftime
from java.util import Date
import smtplib
# from cProfile import Profile


class loadParameters:

    def __init__(self, propfile, action="healthCheck"):
        self.propfile = propfile
        self.action = action

        print "DEBUG:", self.propfile
        self.props = self.loadPropertyFile(self.propfile)
    
        self.appname = self.getProperty("APP.NAME")
        
        if self.appname == None: 
            self.appname = "APPLICATION_NOT_DEFINED"
        
        self.admurl = self.getProperty("ADMIN.URL")
        self.ucf = self.getProperty("ADMIN.UCF")
        self.ukf = self.getProperty("ADMIN.UKF")
        
        self.username = self.getProperty("ADMIN.USERNAME")
        self.password = self.getProperty("ADMIN.PASSWORD")
        
        self.stopbefore = self.getProperty("STOP.OS.COMMAND.BEFORE")
        self.stoplist = self.splitProp(self.getProperty("STOP.LIST"))
        
        self.stopafter = self.getProperty("STOP.OS.COMMAND.AFTER")
        
        self.startbefore = self.getProperty("START.OS.COMMAND.BEFORE")
        self.startlist = self.splitProp(self.getProperty("START.LIST"))
        self.startafter = self.getProperty("START.OS.COMMAND.AFTER")        
        
        self.rollingseq = self.getProperty("ROLLINGRESTART.NUMINBATCHES")
        if self.getProperty("ROLLINGRESTART.NUMINBATCHES") != None:
            self.rollingseq = int(self.rollingseq)
        
        self.rollingexclude = self.getProperty("ROLLINGRESTART.EXCLUDENOTRUNNING")
        
        self.cacheclean = self.getProperty("START.CLEANCACHE")
        self.urls = self.getProperty("HEALTH.URLS")
        
        self.mailSvr = self.getProperty("MAIL.SERVER")
        self.mailFrom = self.getProperty("MAIL.FROM")
        self.mailto = self.getProperty("MAIL.TO")
        self.mailcc = self.getProperty("MAIL.CC")
        self.mailft = self.getProperty("MAIL.FAILTO")
        
        if self.mailSvr == None or self.mailSvr == "": 
            self.mailSvr = ""
        
        if self.mailFrom == None: 
            self.mailFrom = "noreply_byrestartscript"
        
        if self.mailcc == None: 
            self.mailcc = ""
        
        if self.mailft == None: 
            self.mailft = ""
        
        self.logfile = self.appname + "." + self.action + ".log"    
        
        redirect(self.logfile)
        
        self.logfilefh = open(self.logfile, "w")
        # File Handle
        # self.connWithKey(self.ucf, self.ukf, self.admurl)
        
        # 3 arrays. Default is []
        # List of 
        self.sts = self.getStandaloneServerList()
        self.cls = self.getClusterList()
        self.ams = self.getAllManagedServerList()
    
    def colorPrint(self, txt):
        print >> self.logfilefh, txt
        if os.pathsep == ":" : 
            print "\033[1;31m", txt, "\033[0m"
        else:
            print txt
    
    def timeStampPrint_(self, *arg):
        print "<", strftime("%a, %d %b %Y %H:%M:%S %Z"), ">" , arg
    
    def timeStampPrint(self, arg):
        print "<", strftime("%a, %d %b %Y %H:%M:%S %Z"), ">" , arg
        print >> self.logfilefh, "<" + strftime("%a, %d %b %Y %H:%M:%S %Z") + "> " + arg
    
    def loadPropertyFile(self, pfile):
        p = java.util.Properties()
        try:
            p.load(java.io.FileInputStream(pfile))
        except: 
            dumpStack()
            raise Exception, "\n# Problem loading properties file: " + str(pfile) + "!" 
        return p
    
    def valid(self, prop):
        prop = str(prop).strip()
        if (prop != "") and (prop.lower() != "none"): 
            return prop
        else: 
            return None
            
    def getProperty(self, key):
        try:
            return self.valid(self.props.getProperty(key))
        except: 
            # raise Exception, "\nProblem getting property " + key + " from properties file!"     
            self.colorPrint ("## Problem getting property " + key + " from properties file!")
            # sys.exit(1) 
    
    def connWithPassword(self, username, password, admurl):
      if connected == "true":
        self.timeStampPrint("# Already connected to Admin server.")
      else:
        try:
            # self.timeStampPrint( username + password + admurl)
            connect(self.username, self.password, self.admurl, timeout="30000")
        except:
            self.sendFailEMail(self.appname + " " + action + " FAILED - cannot conn admin server. PLEASE PAGE WEBOPS!")        
            sys.exit("#Fail to connect admin server")
    
    def connWithKey(self, ucf, ukf, admurl):
      if connected == "true":
        self.timeStampPrint("# Already connected to Admin server !!")
      else:
        try:
            # self.timeStampPrint( ucf,ukf,admurl)
            # Timeout 30 seconds
            connect(userConfigFile=ucf, userKeyFile=ukf, url=admurl, timeout="30000")
        except:
            self.sendFailEMail(self.appname + " " + action + " FAILED - cannot conn admin server. PLEASE PAGE WEBOPS!")        
            sys.exit("#Fail to connect admin server")        

    def connectToAdmin(self):
        if self.ucf != None and self.ukf != None:
            self.connWithPassword(self.username, self.password, self.admurl)
        elif self.ucf != None and self.ukf != None:
            self.connWithKey(self.ucf, self.ukf, self.admurl)
        else:
            sys.exit("#Both config key and username/password not set up. Not able to connect to Admin server.")
    
    def getStatus(self, serverName):
      # self.timeStampPrint( "## cd domainRuntime:/ServerLifeCycleRuntimes/"+serverName)
      cd("domainRuntime:/ServerLifeCycleRuntimes/" + serverName)
      return cmo.getState()

    def getServerList(self):
        if connected == "true": 
            return cmo.getServers()
        else:
            self.colorPrint ("# NOT connect to Admin server yet and NOT able to get Managed server list")
    
    # Should return a list instead of a dict
    def getClusterList(self):
        clusters = []
        if connected == "true":         
            config = domainRuntimeService.getDomainConfiguration().getClusters()
            if config != None:
                for c in config:
                    clusters.append(c.getName())
        return clusters
    
    def getStandaloneServerList(self):
        standaloneserverlist = []
        if connected == "true":
            domainConfig()
            adminserver = cmo.getAdminServerName()
            for s in cmo.getServers():
                if s.getCluster() == None and s.getName() != adminserver:
                    standaloneserverlist.append(s.getName())
        return standaloneserverlist
    
    def getAllManagedServerList(self):
        serverlist = []
        if connected == "true":         
            adminserver = cmo.getAdminServerName()
            for s in cmo.getServers():
                if s.getName() != adminserver:
                    serverlist.append(s.getName())
        return serverlist

    def sendEMail(self, subj, body=""):
        self.timeStampPrint("mailto: " + self.mailto)
        if self.mailto == "": self.timeStampPrint("#Email address NOT defined. ")
        else:
            self.mt = (self.mailto + "," + self.mailcc).split(",")    
            self.message = """\
    From: %s
    To: %s
    Subject: %s
    
    %s
    """ % (self.mailFrom, ", ".join(self.mt), subj , open(self.logfile, "r").read())
    
        # Send the mail
    
        server = smtplib.SMTP(self.mailSvr)
        server.sendmail(self.mailFrom, self.mt, self.message)
        server.quit()
    
    
    def sendFailEMail(self, subj, body=""):
      self.timeStampPrint("mailto: " + self.mailto)
      if body == "": 
        emailboday = open(self.logfile, "r").read()
      else: 
        emailboday = body
      if self.mailto == "": self.timeStampPrint("#Email address NOT defined. ")
      else:
        mt = (self.mailto + "," + self.mailft + "," + self.mailcc).split(",")    
        message = """\
    From: %s
    To: %s
    Subject: %s
    
    %s
    """ % (self.mailFrom, ", ".join(mt), subj, emailboday)
    
        # Send the mail
    
        server = smtplib.SMTP(self.mailSvr)
        server.sendmail(self.mailFrom, mt, message)
        server.quit()
    
    def splitProp(self, item):
        if item == None: 
            return None
        else:
            return item.split(",")
        
    def testURL(self):
      
      result = 0
      problemurls = ""
      if self.urls != None:
        su = self.splitProp(self.urls)
        i = 0
        while i < len(su):
          self.timeStampPrint("## Testing health URL: " + str(su[i + 1]))
          try:
            if urllib.urlopen(su[i + 1]).geturl() == su[i + 1]: 
                self.timeStampPrint(str(su[i]) + " is health by testing health URL.")
          except:
            self.colorPrint("[WARNING]: " + su[i] + " is NOT healthy by testing health URL.")
            problemurls = problemurls + "\n" + su[i] + " " + su[i + 1]
            pass
          i = i + 2  
      if problemurls != "":
        result = 1
        print self.appname, self.action, problemurls
        self.sendFailEMail(self.appname + " Health Pages Check Failed after " + self.action, self.problemurls)
      return result

class stopWLServices(loadParameters):

    def __init__(self, propfile, action="healthCheck"):
        loadParameters.__init__(self, propfile, action)
    
    def stopManagedServers(self, serverList):
      self.timeStampPrint("## Stopping Managed Servers: " + str(serverList))
      failmsg = ""
      for inst in serverList:
        status = getStatus(inst)
        # if str(status) == "RUNNING":
        if str(status) != "SHUTDOWN":
          state(str(inst))
          self.timeStampPrint("## Shutting down server " + inst)
          try: 
            shutdown(str(inst), "Server", force="true", block="false")    
          except:  # WLSTException, e:
            failmsg = failmsg + " Fail to stop " + inst
            pass
        else:
          self.timeStampPrint("## Status of Server " + inst + " is " + status)
      
      # nmkill after 10minutes
      
      if failmsg != "":
        self.sendFailEMail(self.appname + ": " + self.failmsg + ". PLEASE PAGE WEBOPS!")
        sys.exit(failmsg)
    
      for inst in serverList:
        count = 1
        while 1:
          flag = "Done"
          status = self.getStatus(inst)
          if status != "SHUTDOWN":
            flag = "StillChecking"
            sys.stdout.write(".")        
          if flag == "Done" : break
          count = count + 1
          # MAX 30 minutes to stop this
          if count > 600: 
            self.sendFailEMail(self.appname + " FAIL TO STOP. PLEASE PAGE WEBOPS!")
            sys.exit("## Fail to start")      
          Thread.currentThread().sleep(5000)
          if "FAILED_NOT_RESTARTABLE" == status:
            self.timeStampPrint("## " + inst + " in FAILED_NOT_RESTARTABLE state.")
            break
        print
            
    def stopClstr(self, clstrName):
      self.timeStampPrint("## Stopping Clusters: " + str(clstrName))
      domainConfig()
      failmsg = ""
      try:
        clsmbean = getMBean("/Clusters/" + clstrName)
        svrsmbean = clsmbean.getServers()
      except:
        dumpStack()
        pass
      # self.timeStampPrint( "Cluster Bean:" + str(clsmbean))
      # self.timeStampPrint( "Servers Name:" + str(svrsmbean))
      runStop = "false"
      for smbean in svrsmbean:
        inst = smbean.getName()
        status = self.getStatus(inst)
        if status != "SHUTDOWN": runStop = "true"
      if runStop == "true":
        try:
          shutdown(clstrName, "Cluster", force="true")
        except:  # WLSTException, e:
          failmsg = failmsg + " Fail to stop " + clstrName
          # dumpStack()
          pass
      else: 
          self.timeStampPrint("## " + str(clstrName) + "is down already.")
      if failmsg != "":
          self.sendFailEMail(self.appname + ": " + failmsg + ". PLEASE PAGE WEBOPS!")
          sys.exit(failmsg)
    
      count = 0
      while 1:
        flag = "Done"
        for smbean in svrsmbean:
          inst = smbean.getName()
          status = self.getStatus(inst)
          if status != "SHUTDOWN":
            flag = "StillChecking"
            self.timeStampPrint("## " + inst + " is not shut down completely. Please wait a bit more!!")
          else:
            self.timeStampPrint("## " + inst + " is down NOW.")
        if flag == "Done" :
          break
        count = count + 1
        # MAX 30 minutes to start this
        if count > 600: 
            self.sendFailEMail(self.appname + " FAIL TO STOP CLUSTER. PLEASE PAGE WEBOPS!")
            sys.exit("## Fail to start")
        Thread.currentThread().sleep(5000)
      
      # """
      self.timeStampPrint("## Checking state of Cluster ##")
      state(clstrName, "Cluster")

class startWLServices(loadParameters):  
    def __init__(self, propfile, action="healthCheck"):
        loadParameters.__init__(self, propfile, action)

    def startManagedServers(self, serverList):
      self.timeStampPrint("## Starting Managed Servers: " + str(serverList))
      failmsg = ""
      for inst in serverList:
        self.timeStampPrint("## Checking status of Server: " + inst)
        try:
          status = self.getStatus(inst)  
          self.timeStampPrint("## " + "Status of Managed Server is " + status)
          if status != "RUNNING":
            self.timeStampPrint("## " + "Starting server " + inst)
            # start(inst, block="true")
            # set block false to start next MS immediately
            start(inst, block="false")
        except:  # WLSTException, e:
          failmsg = failmsg + " Fail to start " + inst      
          pass      
      if failmsg != "":
          self.sendFailEMail(self.appname + ": " + failmsg + ". PLEASE PAGE WEBOPS!")
          sys.exit(failmsg)
      count = 0
      while 1:
        flag = "Done"
        for inst in serverList:
          status = self.getStatus(inst)
          if status != "RUNNING":
            flag = "StillChecking"
            self.timeStampPrint("## " + str(inst) + " is not up completely. Please wait a bit more!!")
          else:
            self.timeStampPrint("## " + str(inst) + " is up and running NOW.")
        if flag == "Done" :
            break
        count = count + 1
        # MAX 30 minutes to start this
        if count > 600: 
            self.sendFailEMail(self.appname + ": FAIL TO START. PLEASE PAGE WEBOPS!")
            sys.exit("## Fail to start")
        Thread.currentThread().sleep(5000)        
    
    def startClstr(self, clstrName):
      self.timeStampPrint("## Starting Clusters: " + str(clstrName))
      domainConfig()
      clsmbean = getMBean("domainConfig:/Clusters/" + clstrName)
      svrsmbean = clsmbean.getServers()
      # Check if the cluster is up and running
      failmsg = ""
      runStart = "false"
      
      for smbean in svrsmbean:
        inst = smbean.getName()
        status = self.getStatus(inst)
        if status != "RUNNING": runStart = "true"
      
      if runStart == "true":
        try:
          start(clstrName, "Cluster")
        except Exception, e:
          failmsg = failmsg + " Fail to start " + clstrName
          pass
      else: 
        self.timeStampPrint("## " + clstrName + "is up and running already.")
              
      if failmsg != "":
          self.sendFailEMail(self.appname + ": " + failmsg + ". PLEASE PAGE WEBOPS!")
          sys.exit(failmsg)
    
      count = 0
      while 1:
        flag = "Done"
        for smbean in svrsmbean:
          inst = smbean.getName()
          status = self.getStatus(inst)
          if status != "RUNNING":
            flag = "StillChecking"
            self.timeStampPrint("## " + str(inst) + " is not up completely. Please wait a bit more!!")
          else:
            self.timeStampPrint("## " + str(inst) + " is up and running already.")
        if flag == "Done" :
          break
        count = count + 1
        
        # MAX 30 minutes to start this
        if count > 600: 
          self.sendFailEMail(self.appname + " FAIL TO START Cluster. PLEASE PAGE WEBOPS!")
          sys.exit("## Fail to start")
        Thread.currentThread().sleep(5000)
    
      self.timeStampPrint("## Checking state of Cluster ##")
      state(clstrName, "Cluster") 
    
    def startAll(self):
      if self.startbefore != None: 
        self.timeStampPrint("## Running " + self.startbefore + " before star task ...")
        os.system(self.startbefore)
      # conn(username,password,admurl)
      self.connWithKey(ucf, ukf, admurl)
      # Customized start list have been defined.
      if self.startlist != None:
        slist = []
        for item in self.startlist:
          for c in self.cls:
            if item == c: 
              self.startClstr(item)
          for s in self.ams: 
            if item == s: 
              # start(item, "Server")
              # startManagedServers([item]) will start MS one by one
              # startManagedServers([item])
              # Create a list of managed servers
              slist.append(s)
        # Starting managed servers in a batch
        self.startManagedServers(slist)
      # if not customized start list defined. start cluster and then stand alone servers.
      else:
        for c in self.cls:
            self.startClstr(c)  
        if self.sts != []: 
            self.startManagedServers(self.sts)
      if self.startafter != None:     
        self.timeStampPrint("## Running " + self.startafter + " after star task ...")
        os.system(self.startafter)


    def rollingRestart(self):
      if self.stopbefore != None: 
        self.timeStampPrint("## Running " + self.stopbefore + " before stop task ...")
        os.system(self.stopbefore)
      self.connWithKey(self.ucf, self.ukf, self.admurl)
      # Rolling restart servers only in stop list
      if self.stoplist != None:
        sts = self.stoplist
      else:
        sts = self.ams
      # self.timeStampPrint( sts)
      if self.rollingseq == None or self.rollingseq == 1:
        # restart one by one
        for s in sts:
          self.stopManagedServers([s])
          self.startManagedServers([s])
      else:
        times = len(sts) / self.rollingseq
        i = 0
        j = 0
        if len(sts) % self.rollingseq != 0: times = times + 1
        while i < times:
          slist = []
          while j < len(sts):
            # Restart instance only in RUNNING state
            if self.getStatus(sts[j]) == "RUNNING" or self.rollingexclude == "false": slist.append(sts[j])
            else: self.colorPrint ("[WARNING]: " + str(sts[j]) + " is NOT in RUNNING state. Excluded in rolling restart list!!!")
            j = j + times
          self.colorPrint("## Restarting... " + str(slist))
          self.stopManagedServers(slist)      
          self.startManagedServers(slist)
          i = i + 1
          j = i
      if self.stopafter != None: 
        self.timeStampPrint("## Running " + self.stopafter + " after stop task...")
        os.system(self.stopafter)


# main function starts here

argnum = len(sys.argv)
if argnum == 2:
    print "#Action for the script is healthchek be default."
    action = "healthcheck"
elif argnum == 3: 
    action = sys.argv[2]
else:
    sys.exit("Usage: " + sys.argv[0] + " property_file start/stop/restart/rollingrestart/healthcheck")
    
propfile = sys.argv[1]

if (not os.path.isfile(propfile)):   
    sys.exit("Property file not file")

parameterBox = loadParameters(propfile, action)

if action == "start" :
    startServiceBox = startWLServices(propfile, action)
    startServiceBox.connectToAdmin()
    startServiceBox.startAll()
    parameterBox.testURL()
elif action == "stop" :
    stopServiceBox = stopWLServices(propfile, action)
    stopServiceBox.connectToAdmin()
    stopServiceBox.stopAll()
elif action == "restart" :
    startServiceBox = startWLServices(propfile, action)
    stopServiceBox = stopWLServices(propfile, action)
    stopServiceBox.connectToAdmin()
    stopServiceBox.stopAll()  
    startServiceBox.startAll()
    parameterBox.testURL()
elif action == "rollingrestart" :
    startServiceBox = startWLServices(propfile, action)
    startServiceBox.connectToAdmin()
    startServiceBox.rollingRestart()
    startServiceBox.testURL()
elif action == "healthcheck" :    
    r = parameterBox.testURL()
    sys.exit(r)
else :    
    parameterBox.timeStampPrint("## Must run with one of start|stop|restart|rollingrestart|healthcheck options")
    sys.exit(1)
  
if connected == "true": 
    disconnect()

stopRedirect()
parameterBox.sendEMail(parameterBox.appname + " " + parameterBox.action + " Successfully")
