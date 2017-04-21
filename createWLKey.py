import sys
import os.path
import thread
import time
from java.util import Date

def loadPropertyFile(pfile):
    p = java.util.Properties()
    try:
        p.load(java.io.FileInputStream(pfile))
    except: 
        raise Exception, '\n# Problem loading properties file: ' + pfile + '!' 
    return p

def getProperty(key):
    try:
        return props.getProperty(key)
    except: 
        # raise Exception, '\nProblem getting property ' + key + ' from properties file!'     
        print ('\t# roblem getting property ' + key + ' from properties file!')
        # sys.exit(1)
        

if len(sys.argv) != 2: exit("Usage: " + sys.argv[0] + " <property file to load>")
propfile = sys.argv[1]

if not os.path.isfile(propfile) :   exit("Usage: " + sys.argv[0] + " <property file to load>")

props = loadPropertyFile(propfile)

print props

url = getProperty("ADMIN.URL")
# username=getProperty("ADMIN.USER")
# password=getProperty("ADMIN.PASSWORD")
ucf = getProperty("ADMIN.UCF")
ukf = getProperty("ADMIN.UKF")

if (not os.path.isfile(ucf)) or (not os.path.isfile(ukf)) or (not os.path.isfile(urlFile)) :
    # Move user input out of Python
    username = raw_input('Enter User Name for weblogic Console: ')
    password = raw_input('Enter Password for weblogic Console: ')    
    # admurl   = raw_input('Enter weblogic Admin Console t3/t3s URL(like t3://127.0.0.1:7001): ')
    # admurl   = 't3://'+'$admurl'
    try:
        # f=open(urlFile,'wr+')
        # f.write(admurl)
        # f.flush()
        # f.close            
        connect(username, password, url, timeout='10000')
        storeUserConfig(ucf, ukf)
        disconnect()
        print '# Successfully stored encrypted user credential and url to files.'            
    except WLSTException, e:
        print '# Unable to Creates a user configuration file and an associated key file. Exit...'
        print e
        sys.exit()
    except IOError, e:
        print "# IOError\n", e
        sys.exit()

