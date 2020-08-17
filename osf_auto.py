'''
This code will automatically upload all the directories and files to an OSF
Project. Copy and run the file inside the directory that you want to upload.
Make sure to change the settings and directories.
No sudo or root privilages are needed. Use python3.
'''


'''
You can either manually enter the values for user/password and project id here, or just enter them while running the code.
This file is also automatically uploaded to the OSF destination, so try to use the prompt while running the code.
'''
import getpass
user = input("OSF Username: ") # Enter OSF USERNAME here
passwd = getpass.getpass(prompt='OSF Password: ', stream=None) #Enter OSF Password here
project_guid = input("Project GUID: ") #Enter Project GUID here. It can be found at the end of the project URL
destination = '/' #Enter a name for the destination folder. if left blank, it would be same as the current working directory


import osfclient
from osfclient import cli, utils
import os
import sys

osf = osfclient.OSF()
os.environ["OSF_PASSWORD"] = passwd #insert your OSF password as a string
cwd = os.getcwd()
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
    destination=destination,
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


def checkfile(args):
    storage, remote_path = utils.split_storage(args.remote)
    osf = cli._setup_osf(args)
    project = osf.project(args.project)
    store = project.storage(storage)
    exists = False

    for f in store.files:
        if utils.norm_remote_path(f.path) == remote_path:
            print("%s exists!" % remote_path)
            exists = True
            break
    if not exists:
        print('%s does not exist!' % remote_path)
    return exists



try:
    input('Press Enter to Upload files. \n current directory which will be Uploaded is %s' %cwd)
    print("Initiating the upload")
    arguments.recursive = True
    save2osf(arguments)
    print('All files and directories saved to OSF')
except:
    print("Error: Could not finish the Upload")
    pass

notUploaded = []
file_set = set()
print('Checking to see all files were copied. It is now safe to do a keyboard interruption')
for dir_, _, files in os.walk(cwd):
    for file_name in files:
        rel_dir = os.path.relpath(dir_, cwd)
        rel_file = os.path.join(rel_dir, file_name)
        if rel_file[0] == '.':
            rel_file = rel_file[1:]
        file_set.add(rel_file)
        p = normpath(destination) +'/'+ normpath(os.path.basename(cwd))+ '/' + normpath(rel_file)
        arguments.remote = p
        exists = checkfile(arguments)
        if not exists:
            notUploaded.append(normpath(rel_file))
print(notUploaded)
arguments.remote = ''
arguments.recursive = False
for file in notUploaded:
    if not file.endswith('_auto.py'):
        arguments.source = cwd + '/'+normpath(file)
        arguments.destination = normpath(destination)+'/'+normpath(os.path.basename(cwd))+ '/' +normpath(file)
        print('Uploading %s to %s ' % (arguments.source, arguments.destination))
        save2osf(arguments)
