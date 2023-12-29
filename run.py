'''
    This is a file that configures how your server runs
    You may eventually wish to have your own explicit config file
    that this reads from.

    For now this should be sufficient.

    Keep it clean and keep it simple, you're going to have
    Up to 5 people running around breaking this constantly
    If it's all in one file, then things are going to be hard to fix

    If in doubt, `import this`
'''

#-----------------------------------------------------------------------------
import os
import sys
import sql
from bottle import run
import gunicorn


#-----------------------------------------------------------------------------
# You may eventually wish to put these in their own directories and then load 
# Each file separately

# For the template, we will keep them together

import model
import view
import controller

#-----------------------------------------------------------------------------

# It might be a good idea to move the following settings to a config file and then load them
# Change this to your IP address or 0.0.0.0 when actually hosting
host = 'localhost'

# Test port, change to the appropriate port to host
port = 8081

# Turn this off for production
debug = True

def run_server():    
    '''
        run_server
        Runs a bottle server
    '''
    # use openssl to generate key pairs and certificate.
    # key_file : certificates/localhost.key
    # cert_file : certificates/localhost.crt
    
    run(host=host, port=port, server='gunicorn', keyfile='certificates/localhost.key', certfile='certificates/localhost.crt', debug=debug) 

#-----------------------------------------------------------------------------
# Optional SQL support
# Comment out the current manage_db function, and 
# uncomment the following one to load an SQLite3 database
def manage_db():
    '''
        Blank function for database support, use as needed
    '''
    sql_db = sql.SQLDatabase()
    sql_db.database_setup()

    # Print the https domain, Please use this link to visit
    print("Please use this HTTPS Domain: https://localhost:8081")

    #print(sql_db.debug())
    #print(sql_db.get_user('admin'))

    pass


#-----------------------------------------------------------------------------

# What commands can be run with this python file
# Add your own here as you see fit

command_list = {
    'manage_db' : manage_db,
    'server'       : run_server
}

# The default command if none other is given
default_command = 'server'

def run_commands(args):
    '''
        run_commands
        Parses arguments as commands and runs them if they match the command list

        :: args :: Command line arguments passed to this function
    '''


    for command in command_list:

        command_list[command]()

#-----------------------------------------------------------------------------

run_commands(sys.argv)
