################################################################################
#          __  __ _              _ _                                           #
#         |  \/  (_)___  ___ ___| | | __ _ _ __   ___  ___  _   _ ___          #
#         | |\/| | / __|/ __/ _ \ | |/ _` | '_ \ / _ \/ _ \| | | / __|         #
#         | |  | | \__ \ (_|  __/ | | (_| | | | |  __/ (_) | |_| \__ \         #
#         |_|  |_|_|___/\___\___|_|_|\__,_|_| |_|\___|\___/ \__,_|___/         #
#                        |_   _|__   ___ | |___                                #
#                          | |/ _ \ / _ \| / __|                               #
#                          | | (_) | (_) | \__ \                               #
#                          |_|\___/ \___/|_|___/                               #
#                                                                              #
#           == A set of miscellaneous helper functions and tools ==            #
#                                                                              #
################################################################################
#                                                                              #
#                                                                              #
################################################################################
#                                                                              #
# Copyright (c) 2015 Cisco Systems                                             #
# All Rights Reserved.                                                         #
#                                                                              #
#    Unless required by applicable law or agreed to in writing, this software  #
#    is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF   #
#    ANY KIND, either express or implied.                                      #
#                                                                              #
################################################################################

# Standard library imports
import sys

# Globals
g_do_debug=False

# FUNCTION DEFINITIONS
def fatal(msg):
    """
    Prints and error message and aborts program execution
    """
    sys.stderr.write(str(msg)+"\n")
    sys.exit(1)
    
def warning(msg):
    """
    Prints a warning message to stderr
    """
    sys.stderr.write(str(msg)+"\n")

def output(msg):
    """
    Prints a message to stdout
    """
    sys.stdout.write(str(msg)+"\n")

def debug(msg):
    """
    Prints a message to stdout only if the global g_do_debug var is True
    """
    global g_do_debug
    if g_do_debug==True:
        sys.stdout.write(str(msg)+"\n")

def debug_enable():
    """
    Enables debug mode
    """
    global g_do_debug
    g_do_debug=True

def is_number(s):
    """
    Checks whether the supplied parameter is a number.
    @return True if the paremeter is a number.
    @return False if the parameter is not a number.
    """
    try:
        float(s)
        return True
    except ValueError:
        return False

def list_to_dict_by_key(slist, key):
    """
    This function takes a list of objects and returns a dictionary, indexed
    by the value of the supplied attribute
    @param slist is the list to convert
    @param key is the name of the object attribute to be used as key
    @return dictionary of objects in slist, indexed by key
    """
    mydict={}
    for l in slist:
        mydict[ l.__dict__[key] ] = l


def list_to_dict_by_method(slist, method):
    """
    This function takes a list of objects and returns a dictionary, indexed
    by the value returned by the supplied method
    @param slist is the list to convert
    @param method is the methor reference to be used as key
    @return dictionary of objects in slist, indexed by key
    """
    mydict={}
    for l in slist:
        mydict[ l.method() ] = l

