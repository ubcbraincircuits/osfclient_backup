'''
This code will automatically upload all the directories and files to an OSF
Project. Copy and run the file inside the directory that you want to upload.
Make sure to change the settings and directories.
No sudo or root privilages are needed. Use python3.
'''


'''
CONSTANTS
'''
# Look into making this an input to the command line, so that username and password
# is not stored.
import getpass

# USE THIS IF YOU WANT TO INPUT YOUR DETAILS IN THE COMMAND LINE
user = input("OSF Username: ")
passwd = getpass.getpass()
project_guid = input("Project GUID: ")
destination = input("Destination Folder (leave empty if none): ")

# USE THIS IF YOU WANT TO INPUT YOUR DETAILS IN THE SCRIPT
# user = '' # Enter OSF USERNAME here
# passwd = '' #Enter OSF Password here
# project_guid = '' #Enter Project GUID here. It can be found at the end of the project URL
# destination = '' #Enter a name for the destination folder. if left blank, it would be same as the current working directory


import osfclient
from osfclient import cli, utils
import os
import sys
import getpass
osf = osfclient.OSF()
ask = True
os.environ["OSF_PASSWORD"] = passwd #insert your OSF password as a string
cwd = os.getcwd()
destination = os.path.join(destination,os.path.basename(cwd))

class args:

    def __init__(self, project, username=None, update=False, force=False, destination=None, source=None, recursive=False, target=None, output=None, remote=None, local=None):
        self.project = project
        self.username = username
        self.update = update # applies to upload, clone, and fetch
        self.force = force # applies to fetch and upload
        # upload arguments:
        self.destination = destination
        self.source = source
        self.recursive = recursive
        # remove argument:
        self.target = target
        # clone argument:
        self.output = output
        # fetch arguments:
        self.remote = remote
        self.local = local

arguments = args(
    username= user, #insert your OSF username
    project=project_guid, # insert your project GUID
    # upload arguments:
    destination=os.path.join(destination,cwd),
    source=cwd,
    # remove argument:
    target='',
    # clone argument:
    output='',
    # fetch arguments:
    remote='',
    local=''
)

def save2osf(arguments):
    cli.upload(arguments)
    print('Upload Successful')
    
def normpath(path):
    while path.startswith('/'):
        path = path[1:]
    return path     

# Function to check if file exists in the osf project. Currently
# checks every file on OSF and sees if it is a match, which is 
# very slow for large projects.
def checkfile(args):
    storage, remote_path = utils.split_storage(args.remote)
    osf = cli._setup_osf(args)
    project = osf.project(args.project)
    store = project.storage(storage)
    exists = False
    for f in store.files:
        # print(f)
        if utils.norm_remote_path(f.path) == remote_path:
            print("%s exists!" % remote_path)
            exists = True
            break
    if not exists:
        print('%s does not exist!' % remote_path)
    return exists

# Function to upload to osf. Tries to upload if the file does not exist.
# Returns whether or not the upload was successful
def upload_to_osf(arguments):
    arguments.remote = arguments.destination
    exists = False
    # exists = checkfile(arguments)
    arguments.remote = ""
    
    if not exists:
        errors = 0
        success = False
        while(errors < 3 and not success):
            try:
                save2osf(arguments)
                print("Uploaded: " + arguments.source)
                success = True
            except Exception as e:
                if str(e) == normpath(arguments.destination):
                    print("Exists: " + arguments.source)
                    success = True
                else: 
                    print("Error uploading file: " + arguments.source)
                    print(e)
                    errors += 1   
    return success or exists


# This script assumes there are no subdirectories. This is a non-recursive upload.
arguments.recursive = False
file_list = os.listdir(cwd)
num_files = len(file_list) - 1
num_uploaded = 0
failed_files_list = []

# Then upload each of its contents to osf
for f in file_list:
    if ".tar" in f and os.path.isfile(f):
        arguments.source = os.path.join(cwd,f)
        arguments.destination = os.path.join(destination, f)
        if upload_to_osf(arguments):
            num_uploaded += 1
            print("Finished " + str(num_uploaded) + "/" + str(num_files))
        else: 
            print("FAILED")
            failed_files_list.append(f)

