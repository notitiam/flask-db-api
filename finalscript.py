import argparse # To use command line arguments

import ast # To parse and check input model file


#
#    Errors and Exceptions
#
#

class Error(Exception):
    #Base Class for Exceptions.
    pass

class TooManyArguments(Error):
    pass

class InvalidFilenameExtension(Error):
    pass

class UserTerminating(Error):
    pass

#
# Command Line Arguments Definitions
#
parser = argparse.ArgumentParser(prog='finalscript.py',
                                usage='python3 %(prog)s input-file [optional arguments]',
                                description='Generate a FlaskAPI server (FPVAPIserver.py) from a Peewee Model File(infile)')


# Add a required, positional argument for the input data file name,
# and open in 'read' mode
parser.add_argument('ifile',
                    metavar='Input File',
                    action='store',
                    nargs='?',
                    default='db_model.py',
                    type=argparse.FileType('r'),
                    help='Default db_model.py')


parser.add_argument('-i', '--ipv4', 
                    dest='hostip',
                    metavar='', 
                    action='store', 
                    default='0.0.0.0',
                    help="host-ip, Default 0.0.0.0")

parser.add_argument('-p', '--port', 
                    dest='port',
                    metavar='', 
                    action='store', 
                    type=int,
                    default='8000',
                    help="Port Number, Default 8000")



# Add an optional argument for the output file,
# open in 'write' mode and and specify encoding
parser.add_argument('-o', '--output',
                    metavar='', 
                    type=argparse.FileType('w+', encoding='UTF-8'), 
                    dest='ofile', 
                    action='store', 
                    default='FPVAPIserver.py',
                    help='Output File, Default FPVAPIserver.py')

parser.add_argument('rargs',
                    metavar='',
                    nargs=argparse.REMAINDER)

# Now variable parser contains all information.

#
# Functions To find and filter ClassNames
#

# Given a node, Find all instances of Class within it
def classes_in(node):
    return [n for n in node.body if isinstance(n, ast.ClassDef)]

# Given a node which is a class, determine if it is basemodel per PeeWee.
def is_basemodel(aclass_node):
    result = False
    l = len(aclass_node.body)
    scls = classes_in(aclass_node)
    if l == 1 and len(scls) == 1:
        n = scls[0].name
        if n == 'Meta':
            result = True
    return result

# Boolean opposite of is_basemodel        
def isnot_basemodel(m):
    return not is_basemodel(m)
    
#
# Functions to Generate the final code
#

# Make header string

# fname = 'models'
# cnamelist = ['FirstClass', 'SecondClass', 'ThirdClass']

def headstring(fname, cnamelist):
    s = f"""
from flask import Flask, request
from {fname} import { ', '.join(cnamelist) }
import json

app = Flask(__name__)

"""
    return s


def apistring4class(cname):
    s = f"""
@app.route('/{cname}', methods=['GET', 'POST'])
def fn{cname}():
    if request.method == 'GET':
        # select
        q = {cname}.select()
        for k in request.args:
            # filter
            field = getattr({cname}, k)
            q = q.where(field == request.args[k])
        return json.dumps(list(q.dicts()))
    elif request.method == 'POST':
        if 'id' in request.form:
            # update
            q = {cname}.update(request.form).where({cname}.id == request.form['id'])
            print(q.sql())
            q.execute()
            return f'updated ' + request.form['id'] 
        else:
            # insert
            rid = {cname}.create( **request.form
            )

            return f'inserted {{rid}}'

"""
    return s
             
def apistrings4classlist(cnamelist):
    s = ''
    for c in cnamelist:
        s = s + apistring4class(c)
    return s

def tailstring(host='0.0.0.0', port=8000, debug=True):
    s = f"""
app.run(host=\'{host}\', port={port}, debug={debug})    

"""
    return s

def makefinalstring(fname, cnamelist, host='0.0.0.0', port=8000, debug=True):
    head = headstring(fname, cnamelist)
    apis = apistrings4classlist(cnamelist)
    tail = tailstring(host, port, debug)
    result = head + apis + tail
    return result

#final = makefinalstring(fname, cnamelist)

#Check why 0.0.0.0 not printing correctly

#
# Now the main function
#

def main(parser):
    try:
        args = parser.parse_args()
        if args.rargs:
            print("Unnecessary arguments Have been given")
            print(args.rargs)
            raise TooManyArguments("You Have given more than necessary arguments")
        
        # Validate Input File Name has '.py' Extension
        f = args.ifile.name

        if not f.endswith("py"):
            print("Input File does not have Valid Extension")
            raise InvalidFilenameExtension("FileName must end with '.py'")
        of = args.ofile.name
        
        print("Will Proceed further with \n \n")
        print("Input File Name: ", f)
        print("Output File Name: ", of)
        print("Host IP: ", args.hostip)
        print("Port Number: ", args.port)
        print("\nEverything seems okay for now. Continue?")
        yesno = input("Enter Y(y)/N(n), Default N(No):  ")
        
        if not yesno.casefold() == 'y':
            raise UserTerminating("\nYou chose No. So, Quitting ...")
        
        # Getting first part of filename as Module Name to be imported
        [fname, _] = f.split(".")
        # Reading the Input File
        with open(f) as file:
            text = file.read()
        #Parsing text as Python code
        root_node = ast.parse(text)
                
        classes = classes_in(root_node) # All Classes in the File
        filtered_list = list(filter(isnot_basemodel, classes)) # Filtering out Base Model and making a list
        cname_list = [c.name for c in filtered_list] # List of classnames
        final = makefinalstring(fname, cname_list, host=args.hostip, port=args.port, debug=True)
        
        with open(of, "w+") as file:
            file.write(final)
        
        #print(final)

    except TooManyArguments as e:
        print(e)
        print("Too many arguments Error")
    except InvalidFilenameExtension as e:
        print(e)
        print("Input must be a python file")
    except UserTerminating as e:
        print(e)
        print("Next time, please choose input parameters carefully!!")
    except SyntaxError as e:
        print(e)
        print("Input file is not valid Python code")
    else:
        print("Done!")
        
main(parser)
