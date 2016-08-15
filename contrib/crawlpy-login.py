#!/usr/bin/env python
#-*- coding: utf-8 -*-

import sys
import getopt
import os.path
import pwd
import json     # json extract
from subprocess import Popen, PIPE, call

__author__ = "cytopia"
__license__ = "MIT"
__email__ = "cytopia@everythingcli.org"
__version__ = '0.1'



# Fix UTF-8 problems inside dict()
reload(sys)
sys.setdefaultencoding('utf8')


################################################################################
# Helper Class
################################################################################
class MyJson(object):

    #----------------------------------------------------------------------
    @staticmethod
    def _read(path):
        fp = open(path)
        data = fp.read()
        fp.close()
        return data

    #----------------------------------------------------------------------
    @staticmethod
    def validateFile(path):
        json_string = MyJson._read(path)
        return MyJson.validateString(json_string)

    #----------------------------------------------------------------------
    @staticmethod
    def validateString(json_string):
        try:
            json_object = json.loads(json_string)
        except ValueError, e:
            return False
        return True

    #----------------------------------------------------------------------
    @staticmethod
    def convertFile2dict(path):
        json_string = MyJson._read(path)
        return MyJson.convertString2dict(json_string)

    #----------------------------------------------------------------------
    @staticmethod
    def convertString2dict(json_string):
        # TODO:
        #content = json.loads(str(json_string))
        #print content
        #for key, value in content.iteritems():
        #    if type(value) == type(['']):
        #        for sub_value in value:
        #            strg = str(json.dumps(sub_value))
        #            MyJson.convertString2dict(strg)
        #    else:
        #        print value

        # fill in default values for missing values
        config = json.loads(json_string)
        jdict = dict()
        jdict['proto'] = str(config.get('proto', 'http'))
        jdict['domain'] = str(config.get('domain', 'localhost'))
        jdict['login'] = dict()
        jdict['login']['enabled'] = bool(config.get('login', dict()).get('enabled', False))
        jdict['login']['method'] = str(config.get('login', dict()).get('method', 'post'))
        jdict['login']['action'] = str(config.get('login', dict()).get('action', '/login.php'))
        jdict['login']['failure'] = str(config.get('login', dict()).get('failure', 'Invalid password'))
        jdict['login']['fields'] = config.get('login', dict()).get('fields', {'username': 'john', 'password': 'doe'})
        return jdict





################################################################################
# Helper Class
################################################################################
class Helper(object):

    #----------------------------------------------------------------------
    @staticmethod
    def which(program):
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        fpath, fname = os.path.split(program)
        if fpath:
            if is_exe(program):
                return program
        else:
            for path in os.environ["PATH"].split(os.pathsep):
                path = path.strip('"')
                exe_file = os.path.join(path, program)
                if is_exe(exe_file):
                    return exe_file

        return None


    #----------------------------------------------------------------------
    @staticmethod
    def readFile(path):
        fp = open(path)
        data = fp.read()
        fp.close()
        return data


    #----------------------------------------------------------------------
    @staticmethod
    def run(args):

        uid = pwd.getpwuid(os.getuid()).pw_name
        cmd = ' '.join(args)

        purple = Helper().get_color('purple')
        green = Helper().get_color('green')
        reset = Helper().get_color('reset')

        print purple + uid + ' $ ' + green + cmd + reset
        return call(args, shell=False)

    #----------------------------------------------------------------------
    @staticmethod
    def get_color(color):

        if color == "red":
            return '\033[0;31m'
        elif color == "green":
            return '\033[0;32m'
        elif color == "blue":
            return '\033[0;34m'
        elif color == "purple":
            return '\033[0;35m'
        else:
            return '\033[0m'

    #----------------------------------------------------------------------
    @staticmethod
    def print_headline(text):
        print Helper().get_color('blue') + text + Helper().get_color('reset')



################################################################################
# Function
################################################################################


#----------------------------------------------------------------------
def usage():
    filename = os.path.basename(sys.argv[0])

    print 'Usage: ' + filename + ' -C conf.json [-c cookie.txt] [-o output.html] [-y]'
    print '       ' + filename + ' -h'
    print '       ' + filename + ' -v'
    print
    print filename + ' will test whether or not the specified crawlpy config'
    print 'is valid and can successfully login.'
    print
    print 'You can optionally save a login session cookie (-c/--cookie) in wget format'
    print 'which can be used by tools such as sqlmap.'
    print
    print 'You can also store the html output from a successfull/unsuccessful login'
    print 'to file (-o/--output).'
    print
    print
    print "Required arguments:"
    print "  -C, --config=      Path to crawlpy json config."
    print "                         -C /path/to/conf.json"
    print "                         --config=/path/to/conf.json"
    print
    print "Optional arguments:"
    print "  -c, --cookie=      Path where to store the session cookie."
    print "                         -c /path/to/cookie.txt"
    print "                         --cookie=/path/to/cookie.txt"
    print
    print "  -o, --output=      Path where to store the html source after logging in."
    print "                         -o /path/to/login.html"
    print "                         --cookie=/path/to/login.html"
    print
    print "  -y, --yes          Answer 'yes' to all questions."
    print
    print "System options:"
    print "  -h, --help         Show help."
    print "  -v, --version      Show version information."


#----------------------------------------------------------------------
def credits():
    filename = os.path.basename(sys.argv[0])
    print filename + ' ' + __version__ + ' by ' + __author__ + ' <' + __email__ + '>'


#----------------------------------------------------------------------
def check_requirements():

    if Helper().which('wget') is None:
        print "wget is required, but not found."
        return False

    return True


#----------------------------------------------------------------------
def get_arguments(argv):

    # Parse command line arguments
    try:
        opts, args = getopt.getopt(argv, 'C:c:o:yhv', ['config=', 'cookie=', 'output=', 'yes', 'help', 'version'])
    except getopt.GetoptError:
        print "Invalid argument(s)"
        usage()
        sys.exit(2)

    # Get values from command line arguments
    for opt, arg in opts:
        if opt in ("-C", "--config"):
            config = arg
        elif opt in ("-c", "--cookie"):
            cookie = arg
        elif opt in ("-o", "--output"):
            output = arg
        elif opt in ("-y", "--yes"):
            yes = True
        elif opt in ("-h", "--help"):
            usage()
            sys.exit()
        elif opt in ("-v", "--version"):
            credits()
            sys.exit()
        else:
            print "Invalid argument: " + opt
            usage()
            sys.exit(2)

    # Check existance of command line arguments
    if 'config' not in locals():
        print "Missing -C, --config argument"
        usage()
        sys.exit(2)

    # Set default values
    if 'cookie' not in locals():
        cookie = False
    if 'output' not in locals():
        output = False
    if 'yes' not in locals():
        yes = False

    # Return values
    return config, cookie, output, yes






################################################################################
# Main Entry Point
################################################################################


if __name__ == "__main__":

    # Retrieve cmd arguments
    config, cookie, output, yes = get_arguments(sys.argv[1:])


    # Check requirements
    if not check_requirements():
        sys.exit(2)

    # Check if config file exists
    if not os.path.isfile(config):
        print "Specified config file does not exist: " + config
        sys.exit(2)

    # Check valid json
    if not MyJson.validateFile(config):
        print "Invalid JSON data in: " + config
        sys.exit(2)


    # 4. Read JSON config into dict()
    jdict = MyJson.convertFile2dict(config)


    # 5. Set up base
    base_url = jdict['proto'] + '://' + jdict['domain']
    login_url = base_url + jdict['login']['action']

    post_data = []
    for key,val in jdict['login']['fields'].iteritems():
        post_data.append(key + '=' + val)



    # Cookie/Output files
    file_output = output if output else '/tmp/login.html'
    file_cookie = cookie if cookie else '/tmp/cookie.txt'


    wget_create_session = [
        'wget',
        '--quiet',
        '--delete-after',
        '--keep-session-cookies',
        '--save-cookies',
        file_cookie,
        login_url
    ]

    wget_login = [
        'wget',
        '--quiet',
        '--keep-session-cookies',
        '--load-cookies',
        file_cookie,
        '--save-cookies',
        file_cookie,
        '--post-data',
        '&'.join(post_data),
        '-O',
        file_output,
        login_url
    ]


    # TODO:
    # check if file exists

    print "============================================================"
    print " Custom Deployment"
    print "============================================================"

    # Make calls
    Helper().print_headline('[1] Creating initial session request')
    if Helper.run(wget_create_session) != 0:
        print "wget session call failed"
        sys.exit(2)

    Helper().print_headline('[2] Submitting POST login')

    # Could return > 0 if main after-login page is 404 or other than 200
    Helper().run(wget_login)

    source = Helper.readFile(file_output)


    if jdict['login']['failure'] in source:
        print
        print "[FAILED] Login failed"
        os.unlink(file_output)
        os.unlink(file_cookie)
        sys.exit(2)

    elif '</html>' in source:
        print
        print "[OK] Login successful"

        if cookie:
            print "[OK] Session cookie created: " + file_cookie
        else:
            os.unlink(file_cookie)

        if output:
            print "[OK] Output file saved: " + file_output
        else:
            os.unlink(file_output)

        sys.exit()

    else:
        print
        print "[FAILED] Unable to check for successful or failed login"
        os.unlink(file_output)
        os.unlink(file_cookie)
        sys.exit(2)

