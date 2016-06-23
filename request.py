# -*- coding: utf-8 -*-
# This script was written for Python 2.7.11 and is compatible with Windows, Mac OS X and Linux
# It requires the 'requests'-module, which will be automatically installed, if the script is started with administrator-privileges
# The purpose of this script is to check for new files on the StudIP-website of the university of Passau,
# which are then downloaded and saved in your desired destination folder

# Overview about the cookies:
#   - cookie_seminar_session
#   - cookie_shibstate
#   - sibboleth_cookies (consisting of cookie_jsessionid and cookie_idp_authn_lc_key)
#   - cookie_idp_session
#   - shibsession


import HTMLParser
import sys
import codecs
import os
import getpass
import base64
import ctypes
import importlib
import zipfile
import time
import shutil
from os import path, environ

APPNAME = "StudIP File Downloader"
APPKEY = '54t50bttvyk9ioq'
APPSECRET = 'rd34w4ga83u31es'
ONEDRIVEKEY = 'WhFPgXqZH4GpCDGh4ARQnyw-dVOYO1sI'
ONEDRIVEID = '0000000048193446'
REDIRECTURI = "http://localhost:8080"
FORBIDDEN_CHARS = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
FORBIDDEN_CHARS_PATH = ['<', '>', ':', '"', '|', '?', '*']

COUNT_DATA_STORED_IN_CONFIG = 9
WHERETOSAVELINE = 1
LOCALSAVEPATHLINE = 2
DROPBOXSAVEPATHLINE = 2
DRIVESAVEPATHLINE = 2
ONEDRIVESAVEPATHLINE = 2
USERNAMELINE = 3
PASSWORDLINE = 4
LOGFILELINE = 5
DROPBOXKEYLINE = 6
OVERWRITELINE = 7
NOTIFICATIONLINE = 8
PUSHBULLETKEYLINE = 9

DEFAULTWRITELOGFILE = "False"
DEFAULTNOTIFICATIONLINE = "False"
CONFIGFILENAME = "config.conf"
LOGFILENAME = "studip.log"
DRIVESJSONNAME = "client_secret.json"
DRIVECREDENTIALSNAME = "usercred.json"
SCOPES = 'https://www.googleapis.com/auth/drive'
JSONTEXT = '{"installed":{"client_id":"159043213923-6b0eehkfgu23ougnvga8hs9jc0oc0uqp.apps.googleusercontent.com","project_id":"eighth-radio-129614","auth_uri":"https://accounts.google.com/o/oauth2/auth","token_uri":"https://accounts.google.com/o/oauth2/token","auth_provider_x509_cert_url":"https://www.googleapis.com/oauth2/v1/certs","client_secret":"DSgbLaIsZx4IU8bYNzJGr9gV","redirect_uris":["urn:ietf:wg:oauth:2.0:oob","http://localhost"]}}'


def install_and_import_package(packagename):
    if packagename == "google-api-python-client":
        if len(sys.argv) > 1:
            sys.argv[1] = "--noauth_local_webserver"
        try:
            globals()['discovery'] = importlib.import_module('apiclient.discovery')
            globals()['oauth2client'] = importlib.import_module('oauth2client')
            globals()['client'] = importlib.import_module('oauth2client.client')
            globals()['tools'] = importlib.import_module('oauth2client.tools')
        except ImportError:
            try:
                is_admin = os.getuid() == 0
            except AttributeError:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if is_admin == False:
                print "You haven't installed the required  '" + packagename + "'-module, please restart this script with administrator-privileges, so that I can install it for you."
                sys.exit()
            import pip
            pip.main(['install', packagename])
            globals()['discovery'] = importlib.import_module('apiclient.discovery')
            globals()['oauth2client'] = importlib.import_module('oauth2client')
            globals()['client'] = importlib.import_module('oauth2client.client')
            globals()['tools'] = importlib.import_module('oauth2client.tools')
    elif packagename == "onedrivesdk":
        try:
            globals()['onedrivesdk'] = importlib.import_module('onedrivesdk')
        except ImportError:
            try:
                is_admin = os.getuid() == 0
            except AttributeError:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if is_admin == False:
                print "You haven't installed the required  '" + packagename + "'-module, please restart this script with administrator-privileges, so that I can install it for you."
                sys.exit()
            import pip
            pip.main(['install', packagename])
            globals()['onedrivesdk'] = importlib.import_module('onedrivesdk')
    elif packagename == "pushbullet":
        try:
            globals()['pushbullet'] = importlib.import_module('pushbullet')
        except ImportError:
            try:
                is_admin = os.getuid() == 0
            except AttributeError:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if is_admin == False:
                print "You haven't installed the required  '" + packagename + "'-module, please restart this script with administrator-privileges, so that I can install it for you."
                sys.exit()
            import pip
            pip.main(['install', packagename + ".py"])
            globals()['pushbullet'] = importlib.import_module('pushbullet')
    else:
        try:
            globals()[packagename] = importlib.import_module(packagename)
        except ImportError:
            try:
                is_admin = os.getuid() == 0
            except AttributeError:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
            if is_admin == False:
                print "You haven't installed the required  '" + packagename + "'-module, please restart this script with administrator-privileges, so that I can install it for you."
                sys.exit()
            import pip
            pip.main(['install', packagename])
            globals()[packagename] = importlib.import_module(packagename)


def touch_file(file, length):
    with open(file, 'w') as f:
        index = 0
        while index < length:
            f.write("\n")
            index += 1


def drawProgressBar(string, percent, barLen=20):
    progress = ""
    for i in range(barLen):
        if i < int(barLen * percent):
            progress += "#"
        else:
            progress += " "
    sys.stdout.write("\r%s [ %s ] %.0f%%" % (string, progress, percent * 100))
    sys.stdout.flush()


def write_line_in_file(file, line, string):
    data = None
    with open(file, 'r') as f:
        data = f.readlines()
        data[line - 1] = string + "\n"
    with open(file, 'w') as f:
        f.writelines(data)


def read_line_in_file(file, line):
    with open(file, 'r') as f:
        data = f.readlines()
        return data[line - 1].replace("\n", "")


def read_directory_from_console():
    temp_save_path = ""
    while temp_save_path == "":
        temp_save_path = raw_input(
            "Please enter the absolute path to the folder where I should save your downloaded files:\n")
        if not os.path.exists(temp_save_path):
            yesorno = raw_input(
                "I can't find the directory '" + temp_save_path + "'. Should I create it for you? <y/n>\n")
            if yesorno == "y":
                try:
                    os.makedirs(temp_save_path)
                    print "Folder successfully created\n"
                except Exception, e:
                    print "Folder could not be created\n"
                    temp_save_path = ""
            elif yesorno == "n":
                print "Aborted\n"
                temp_save_path = ""
            else:
                print "Invalid input\n"
                temp_save_path = ""
        elif os.path.isfile(temp_save_path):
            print "This is a file, not a directory\n"
            temp_save_path = ""
    return temp_save_path


def read_username_from_console():
    temp_username = ""
    while temp_username == "":
        temp_username = raw_input("Please enter your studip-username:\n")
    return temp_username


def read_password_from_console():
    temp_password = ""
    while temp_password == "":
        temp_password = getpass.getpass("Please enter your studip-password:\n")
    return temp_password


def read_overwrite_from_console():
    temp_overwride = ""
    while temp_overwride != "y" and temp_overwride != "n":
        temp_overwride = raw_input("Would you like to enable overwriting of existing files?<y/n>\n")
    if temp_overwride == "y":
        temp_overwride = "True"
    elif temp_overwride == "n":
        temp_overwride = "False"
    return temp_overwride


def read_dropbox_key_from_console():
    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(APPKEY, APPSECRET)
    authorize_url = flow.start()
    print "To authorize this script to save files on your dropbox, please do the following steps:"
    print '1. Go to: ' + authorize_url
    print '2. Click "Allow" (you might have to log in first)'
    print '3. Copy the authorization code'
    validcode = False
    access_token = None
    while validcode == False:
        code = raw_input("Enter the authorization code here: ").strip()
        try:
            access_token, user_id = flow.finish(code)
            validcode = True
        except:
            print "The authorization code you entered is invalid"
    print "Authorization successfully\n"
    return access_token


def get_drive_service_from_console():
    store = oauth2client.file.Storage(path.join(appdatapath, DRIVECREDENTIALSNAME))
    flow = client.flow_from_clientsecrets(path.join(appdatapath, DRIVESJSONNAME), SCOPES)
    flow.user_agent = APPNAME
    credentials = tools.run_flow(flow, store)
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    return service


def get_onedrive_client_from_console(savesession):
    install_and_import_package("onedrivesdk")
    from onedrivesdk.helpers import GetAuthCodeServer
    onedriveclient = onedrivesdk.get_default_client(client_id=ONEDRIVEID,
                                                    scopes=['wl.signin', 'wl.offline_access', 'onedrive.readwrite'])
    if savesession == True:
        auth_url = onedriveclient.auth_provider.get_auth_url(REDIRECTURI)
        code = GetAuthCodeServer.get_auth_code(auth_url, REDIRECTURI)
        onedriveclient.auth_provider.authenticate(code, REDIRECTURI, ONEDRIVEKEY)
        onedriveclient.auth_provider.save_session()
    else:
        onedriveclient.auth_provider.load_session()
        onedriveclient.auth_provider.refresh_token()
    return onedriveclient


def read_dropbox_directory_from_console(client):
    temp_save_path = ""
    while temp_save_path == "":
        temp_save_path = raw_input(
            "Please enter the absolute path to the folder in your Dropbox where I should save your downloaded files:\n")
        try:
            metadata = client.metadata(temp_save_path)
            if metadata['is_dir'] == True:
                pass
            else:
                print "This is a file, not a directory\n"
                temp_save_path = ""
        except Exception, e:
            if any(c in temp_save_path for c in FORBIDDEN_CHARS_PATH if c in temp_save_path):
                print "Your selected path contains one or more of these unallowed characters: " + str(
                    FORBIDDEN_CHARS_PATH)
                temp_save_path = ""
            else:
                yesorno = raw_input(
                    "I can't find the directory '" + temp_save_path + "' in your Dropbox. Should I create it for you? <y/n>\n")
                if yesorno == "y":
                    client.file_create_folder(temp_save_path)
                    print "Folder successfully created\n"
                elif yesorno == "n":
                    print "Aborted\n"
                    temp_save_path = ""
                else:
                    print "Invalid input\n"
                    temp_save_path = ""
    return temp_save_path


def read_onedrive_directory_from_console(client):
    temp_path = ""
    while temp_path == "":
        temp_path = raw_input(
            "Please enter the absolute path to the folder on OneDrive where I should save your downloaded files:\n")
        if any(c in temp_path for c in FORBIDDEN_CHARS_PATH if c in temp_path):
            print "Your selected path contains one or more of these unallowed characters: " + str(FORBIDDEN_CHARS_PATH)
            temp_path = ""
        else:
            orig_temp_path = temp_path
            if temp_path[0] == "/":
                temp_path = temp_path[1:]
            if temp_path[-1] == "/":
                temp_path = temp_path[:-1]
            folders = temp_path.split("/");
            collection = client.item(drive="me", id="root").children.get()
            exists = False
            folderindex = 0
            id = None
            while folderindex < len(folders):
                exists = False
                for i in range(0, len(collection)):
                    if collection[i].folder != None and collection[i].name == folders[folderindex]:
                        exists = True
                        id = collection[i].id
                        collection = client.item(drive="me", id=collection[i].id).children.get()
                        break
                folderindex += 1
            if exists == False:
                print "I can't find the directory '" + orig_temp_path + "' on OneDrive. Please create this directory first\n"
                temp_path = ""
    return id


def read_drive_directory_from_console(service):
    temp_save_path = ""
    id = ""
    while temp_save_path == "":
        temp_save_path = raw_input(
            "Please enter the absolute path to the folder on your Google Drive where I should save your downloaded files:\n")
        if any(c in temp_save_path for c in FORBIDDEN_CHARS_PATH if c in temp_save_path):
            print "Your selected path contains one or more of these unallowed characters: " + str(FORBIDDEN_CHARS_PATH)
            temp_save_path = ""
        else:
            try:
                exists = True
                orig_temp_save_path = temp_save_path
                if temp_save_path[0] == "/":
                    temp_save_path = temp_save_path[1:]
                if temp_save_path[-1] == "/":
                    temp_save_path = temp_save_path[:-1]
                foldernames = temp_save_path.split('/')
                index = 0
                exists = False
                response = drive_service.files().list(
                    q="mimeType = 'application/vnd.google-apps.folder' and 'root' in parents").execute()
                for file in response.get('files', []):
                    if file.get('name') == foldernames[index]:
                        id = file.get('id')
                        exists = True
                        break;
                while exists == True and index < len(foldernames) - 1:
                    index += 1
                    exists = False
                    response = drive_service.files().list(
                        q="mimeType = 'application/vnd.google-apps.folder' and '" + id + "' in parents").execute()
                    for file in response.get('files', []):
                        if file.get('name') == foldernames[index]:
                            id = file.get('id')
                            exists = True
                            break;
                if exists == False:
                    print "I can't find the directory '" + orig_temp_save_path + "' on Google Drive. Please create this directory first\n"
                    temp_save_path = ""
            except Exception, e:
                print "Exception code: " + str(e)
    return id


def print_help():
    print " -h [help]			Prints out the help"
    print " -s [service]			Change the service you want to use to save the downloaded files (Dropbox, Google Drive, OneDrive or local disc)"
    print " -d [dropbox]			Change your Dropbox account"
    print " -g [google drive]		Change your Google Drive account"
    print " -o [onedrive]			Change your OneDrive account"
    print " -c [change directory]		Change the directory where the downloaded files are stored"
    print " -u [username]			Change the username, that is used for the studip login"
    print " -p [password]			Change the password, that is used for the studip login"
    print " -f [force override]		Forces to override files that already exist"
    print " -l [logfile]			Enables or disables logfiles"
    print " -n [notification]              Enables or disables notifications via Pushbullet for new files"
    print " -r [reset]			Resets all your settings"


def handle_error(e):
    if type(e) == requests.exceptions.ConnectionError:
        print("A connection-error occured, are you sure you have access to the internet?")
    elif type(e) == requests.exceptions.HTTPError:
        print "A http-error occured"
    elif type(e) == requests.exceptions.Timeout:
        print "The connection timed out, maybe the server is currently not available. Please try again later"
    elif type(e) == requests.exceptions.TooManyRedirects:
        print "There occured an error as there were to many redirects"
    elif type(e) == KeyError and str(e) == "'location'":
        print "Couldn't login to studip. You probably entered a wrong username or password. To change your username or password, use the -u or -p parameter"
    else:
        print "An unknown error occured:"
        print str(e)
    if createlogfile == "True":
        print "For further information look at the logifle " + path.join(os.path.dirname(os.path.realpath(sys.argv[0])),
                                                                         LOGFILENAME)
    else:
        print "For further information enable the logfile-feature via the -l commandline parameter"
    write_to_logfile(str(e))
    sys.exit()


def write_to_logfile(string):
    if createlogfile == "True":
        logfilepath = path.join(os.path.dirname(os.path.realpath(sys.argv[0])), LOGFILENAME)
        if not os.path.exists(logfilepath):
            open(logfilepath, 'a').close()
        with open(logfilepath, 'a') as f:
            f.write(time.strftime("%c") + "	" + string + "\n")
            f.close()


def print_and_log(string):
    write_to_logfile(string)
    print string


def savefile(directoryname, file):
    filename = os.path.basename(file.name)
    if wheretosave == "Local":
        tosave_directory = path.join(save_path, directoryname)
        if not os.path.exists(tosave_directory):
            os.makedirs(tosave_directory)
        if overwrite == "True":
            shutil.copy(file.name, tosave_directory)
        else:
            if os.path.exists(path.join(tosave_directory, filename)):
                number = 1
                new_file = os.path.splitext(os.path.join(tosave_directory, filename))[0] + "(" + str(number) + ")" + \
                           os.path.splitext(filename)[-1]
                while os.path.exists(new_file):
                    number += 1
                    new_file = os.path.splitext(os.path.join(tosave_directory, filename))[0] + "(" + str(number) + ")" + \
                               os.path.splitext(filename)[-1]
                shutil.copy(file.name, new_file)
            else:
                shutil.copy(file.name, tosave_directory)
    elif wheretosave == "Google Drive":
        from apiclient.http import MediaFileUpload
        fileextension = os.path.splitext(filename)[-1].lower()
        filemimetype = ""
        if fileextension == ".pdf":
            filemimetype = "application/pdf"
        else:
            filemimetype = "text/" + fileextension[1:]
        exists = False
        response = drive_service.files().list(q="mimeType = 'application/vnd.google-apps.folder' and '" + save_path + "' in parents").execute()
        for f in response.get('files', []):
            if f.get('name') == directoryname:
                id = f.get('id')
                exists = True
                break;
        if exists == False:
            folder_metadata = {'name': directoryname, 'mimeType': 'application/vnd.google-apps.folder',
                               'parents': [save_path]}
            createdfolder = drive_service.files().create(body=folder_metadata, fields='id').execute()
            id = createdfolder.get('id')
        file_metadata = {'name': filename, 'parents': [id]}
        response = drive_service.files().list(q="mimeType = '" + filemimetype + "' and '" + id + "' in parents").execute()
        for f in response.get('files', []):
			if f.get('name') == filename:
				if overwrite == "True":
					file_id = f.get('id')
					drive_service.files().delete(fileId=file_id).execute()
				else:
					already_exists = True
					number = 1
					while already_exists:
						filename = os.path.splitext(filename)[0] + "(" + str(number) + ")" + \
								   os.path.splitext(filename)[-1]
						number += 1
						for f in response.get('files', []):
							already_exists = False
							if f.get('name') == filename:
								already_exists = True
								break;
					file_metadata['name'] = filename
				break;
        media = MediaFileUpload(file.name, mimetype=filemimetype, resumable=True)
        file_uploaded = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    elif wheretosave == "OneDrive":  # TODO: Test override feature
        collection = onedriveclient.item(drive="me", id=save_path).children.get()
        exists = False
        id = ""
        for i in range(0, len(collection)):
            if collection[i].name == directoryname and collection[i].folder != None:
                exists = True
                id = collection[i].id
                break
        if exists == False:
            folder = onedrivesdk.Folder()
            item = onedrivesdk.Item()
            item.name = directoryname
            item.folder = folder
            createdfolder = onedriveclient.item(drive="me", id=save_path).children.add(item)
            id = createdfolder.id
        else:
            items = client.item(id=id).children.get()
            for item in items:
                if item.name == filename:
                    if overwrite == "True":
                        file_id = item.id
                        onedriveclient.item(id=file_id).delete()
                    else:
                        already_exists = True
                        number = 1
                        while already_exists:
                            filename = os.path.splitext(filename)[0] + "(" + str(number) + ")" + \
                                       os.path.splitext(filename)[-1]
                            number += 1
                            for item in items:
                                already_exists = False
                                if item.name == filename:
                                    already_exists = True
                                    break;
                    break;
        onedriveclient.item(drive="me", id=id).children[filename.encode('utf-8')].upload(file.name)
    elif wheretosave == "Dropbox":
        tosave_directory = (save_path + "/" + directoryname).replace("\\\\", "/")
        tosave_directory = tosave_directory.replace("\\", "/")
        try:
            metadata = dropboxclient.metadata(tosave_directory)
            if metadata['is_dir'] == True:
                pass
            else:
                dropboxclient.file_create_folder(tosave_directory)
        except Exception, e:
            dropboxclient.file_create_folder(tosave_directory)
        if overwrite == "True":
            response = dropboxclient.put_file(tosave_directory + "/" + filename, file, overwrite=True)
        else:
            response = dropboxclient.put_file(tosave_directory + "/" + filename, file, overwrite=False)


def main():
    global username
    global password
    global save_path
    global dropboxkey
    global configfilepath
    global appdatapath
    global createlogfile
    global notification
    global pushbulletkey
    global overwrite
    global wheretosave
    global drive_service
    global dropboxclient
    global onedriveclient
    username = ""
    password = ""
    save_path = ""
    dropboxkey = ""
    configfilepath = ""
    appdatapath = ""
    createlogfile = ""
    notification = ""
    pushbulletkey = ""
    overwrite = ""
    wheretosave = ""
    drive_service = None
    dropboxclient = None
    onedriveclient = None
    # Check python version, as this script is made for Python 2.7.11
    version = sys.version_info
    if version[0] == 2:
        if version[1] == 7:
            if version[2] >= 9:  # Script should work for version 2.7.9 and greater
                pass
            else:
                print "This script was written for Python 2.7.11, your current version is " + str(
                    version[0]) + "." + str(version[1]) + "." + str(version[2])
                print "It may happen that the script doesn't work as expected, so consider changing to the appropriate version"
                print "You may also trie out to install the required security-modules with the following command running as administrator: pip install 'requests[security]'\n"
        else:
            print "This script was written for Python 2.7.11, your current version is " + str(version[0]) + "." + str(
                version[1]) + "." + str(version[2])
            print "It may happen that the script doesn't work as expected, so consider changing to the appropriate version"
    else:
        print "This script was written for Python 2.7.11, your current version is " + str(version[0]) + "." + str(
            version[1]) + "." + str(version[2])
        print "It may happen that the script doesn't work as expected, so consider changing to the appropriate version"

    install_and_import_package('requests')

    # Get the path for the config-file depending on the operating system
    if sys.platform == "win32":
        appdatapath = path.join(environ['APPDATA'], APPNAME)
        configfilepath = path.join(appdatapath, CONFIGFILENAME)
    elif sys.platform == 'darwin':
        appdatapath = path.join("/Users/" + getpass.getuser() + "/Library/Application Support", APPNAME)
        configfilepath = path.join(appdatapath, CONFIGFILENAME)
    else:
        appdatapath = path.join("/etc", APPNAME)
        configfilepath = path.join(appdatapath, CONFIGFILENAME)

    # Handle command line arguments
    paraminput = sys.argv
    if len(paraminput) - 1 == 1:
        if paraminput[1] == "-c":
            if not os.path.exists(configfilepath):
                print "This option is only availible if you have already specified a path where to save your files. Please restart the script without a command line parameter"
            else:
                wheretosave = read_line_in_file(configfilepath, WHERETOSAVELINE)
                if wheretosave == "Local":
                    yesorno = raw_input("Would you like to change the path for the downloaded files? <y/n>\n")
                elif wheretosave == "Google Drive":
                    yesorno = raw_input(
                        "Would you like to change the path for the downloaded files on Google Drive? <y/n>\n")
                elif wheretosave == "OneDrive":
                    yesorno = raw_input(
                        "Would you like to change the path for the downloaded files on OneDrive? <y/n>\n")
                elif wheretosave == "Dropbox":
                    yesorno = raw_input(
                        "Would you like to change the path for the downloaded files in your Dropbox? <y/n>\n")
                if yesorno == 'y':
                    if wheretosave == "Local":
                        save_path = read_directory_from_console()
                        write_line_in_file(configfilepath, LOCALSAVEPATHLINE, save_path)
                    elif wheretosave == "Google Drive":
                        install_and_import_package('google-api-python-client')
                        install_and_import_package('httplib2')
                        store = oauth2client.file.Storage(path.join(appdatapath, DRIVECREDENTIALSNAME))
                        credentials = store.get()
                        http = credentials.authorize(httplib2.Http())
                        drive_service = discovery.build('drive', 'v3', http=http)
                        if not credentials or credentials.invalid:
                            print "Invalid Google-Drive credentials. To change your Google Drive account, please use the -g parameter"
                            sys.exit()
                        save_path = read_drive_directory_from_console(drive_service)
                        write_line_in_file(configfilepath, DRIVESAVEPATHLINE, save_path)
                    elif wheretosave == "OneDrive":
                        install_and_import_package('onedrivesdk')
                        from onedrivesdk.helpers import GetAuthCodeServer
                        onedriveclient = get_onedrive_client_from_console(False)
                        save_path = read_onedrive_directory_from_console(onedriveclient)
                        write_line_in_file(configfilepath, ONEDRIVESAVEPATHLINE, save_path)
                    elif wheretosave == "Dropbox":
                        install_and_import_package('dropbox')
                        try:
                            dropboxclient = dropbox.client.DropboxClient(
                                read_line_in_file(configfilepath, DROPBOXKEYLINE))
                        except Exception, e:
                            print "Invalid Dropbox credentials. To change your Dropbox account, please use the -g parameter"
                            sys.exit()
                        save_path = read_dropbox_directory_from_console(dropboxclient)
                        write_line_in_file(configfilepath, DROPBOXSAVEPATHLINE, save_path)
                    print "Successfully updated the config file"
                elif yesorno == 'n':
                    print "Aborted\n"
                else:
                    print "Invalid input\n"
            sys.exit()
        elif paraminput[1] == "-u":
            if not os.path.exists(configfilepath):
                print "This option is only availible if you have already specified a username. Please restart the script without a command line argument"
            else:
                yesorno = raw_input("Would you like to change your username? <y/n>\n")
                if yesorno == 'y':
                    username = read_username_from_console()
                    write_line_in_file(configfilepath, USERNAMELINE, username)
                    print "Successfully changed your username"
                elif yesorno == 'n':
                    print "Aborted\n"
                else:
                    print "Invalid input\n"
            sys.exit()
        elif paraminput[1] == "-p":
            if not os.path.exists(configfilepath):
                print "This option is only availible if you have already specified a password. Please restart the script without a command line argument"
            else:
                yesorno = raw_input("Would you like to change your password? <y/n>\n")
                if yesorno == 'y':
                    password = read_password_from_console()
                    password = base64.b64encode(password)
                    write_line_in_file(configfilepath, PASSWORDLINE, password)
                    print "Successfully changed your password"
                elif yesorno == 'n':
                    print "Aborted\n"
                else:
                    print "Invalid input\n"
            sys.exit()
        elif paraminput[1] == "-f":
            if not os.path.exists(configfilepath):
                print "This option is not availible, until you restart the script without a command line argument"
            else:
                enableordisable = ""
                towrite = ""
                overwrite = read_line_in_file(configfilepath, OVERWRITELINE)
                if overwrite == "True":
                    enableordisable = "disable"
                    towrite = "False"
                elif overwrite == "False":
                    enableordisable = "enable"
                    towrite = "True"
                else:
                    print "Your config-file is corrupted and deleted now, please restart the script to create a new config-file"
                    os.remove(configfilepath)
                    sys.exit()
                yesorno = raw_input("Would you like to " + enableordisable + " overwriting of existing files? <y/n>\n")
                if yesorno == 'y':
                    write_line_in_file(configfilepath, OVERWRITELINE, towrite)
                    print "Successfully updated the config file"
                elif yesorno == 'n':
                    print "Aborted\n"
                else:
                    print "Invalid input\n"
            sys.exit()
        elif paraminput[1] == "-l":
            if not os.path.exists(configfilepath):
                print "This option is not availible, until you restart the script without a command line argument"
            else:
                enableordisable = ""
                towrite = ""
                createlogfile = read_line_in_file(configfilepath, LOGFILELINE)
                if createlogfile == "True":
                    enableordisable = "disable"
                    towrite = "False"
                elif createlogfile == "False":
                    enableordisable = "enable"
                    towrite = "True"
                else:
                    print "Your config-file is corrupted and deleted now, please restart the script to create a new config-file"
                    os.remove(configfilepath)
                    sys.exit()
                yesorno = raw_input("Would you like to " + enableordisable + " logfiles? <y/n>\n")
                if yesorno == 'y':
                    write_line_in_file(configfilepath, LOGFILELINE, towrite)
                    print "Successfully updated the config file"
                    if enableordisable == "enable":
                        print "You can now find the logfile here: " + path.join(
                            os.path.dirname(os.path.realpath(sys.argv[0])), LOGFILENAME)
                elif yesorno == 'n':
                    print "Aborted\n"
                else:
                    print "Invalid input\n"
            sys.exit()
        elif paraminput[1] == "-r":
            if not os.path.exists(configfilepath):
                print "This option is not availible, as you have no settings to reset. To create a config file to hold your settings, please restart this script without a command line parameter\n"
            else:
                yesorno = raw_input("Are you sure you want to irreversibly reset all your settings? <y/n>\n")
                if yesorno == 'y':
                    os.remove(configfilepath)
                    print "Successfully deleted the config file\n"
                elif yesorno == 'n':
                    print "Aborted\n"
                else:
                    print "Invalid input\n"
            sys.exit()
        elif paraminput[1] == "-s":
            if not os.path.exists(configfilepath):
                print "This option is only availible if you have already chosen a service. Please restart the script without a command line parameter"
            else:
                wheretosave = read_line_in_file(configfilepath, WHERETOSAVELINE)
                if wheretosave == "Local":
                    nameofservice = "storing on your local drive"
                elif wheretosave == "Google Drive":
                    nameofservice = "Google Drive service"
                elif wheretosave == "OneDrive":
                    nameofservice = "OneDrive service"
                elif wheretosave == "Dropbox":
                    nameofservice = "Dropbox service"
                yesorno = raw_input(
                    "You are currently using the " + nameofservice + ". Would you like to change your service?<y/n>\n")
                if yesorno == 'y':
                    wheretosave_input = raw_input(
                        "Where should I save your downloaded files? <l/o/g/d>\n - on local harddrive (l)\n - on OneDrive (o)\n - on Google Drive (g)\n - in your Dropbox (d)\n")
                    if wheretosave_input == 'l':
                        wheretosave = "Local"
                        write_line_in_file(configfilepath, WHERETOSAVELINE, wheretosave)
                        save_path = read_directory_from_console()
                        write_line_in_file(configfilepath, LOCALSAVEPATHLINE, save_path)
                        print "Successfully changed your service to storing on your local drive"
                    elif wheretosave_input == 'g':
                        wheretosave = "Google Drive"
                        pathtodrivejson = path.join(appdatapath, DRIVESJSONNAME)
                        with open(pathtodrivejson, "wb") as json:
                            json.write(JSONTEXT)
                        write_line_in_file(configfilepath, WHERETOSAVELINE, wheretosave)
                        install_and_import_package('google-api-python-client')
                        install_and_import_package('httplib2')
                        drive_service = get_drive_service_from_console()
                        save_path = read_drive_directory_from_console(drive_service)
                        write_line_in_file(configfilepath, DRIVESAVEPATHLINE, save_path)
                        print "Successfully changed your service to storing on Google Drive"
                    elif wheretosave_input == 'o':
                        wheretosave = "OneDrive"
                        write_line_in_file(configfilepath, WHERETOSAVELINE, wheretosave)
                        install_and_import_package("onedrivesdk")
                        from onedrivesdk.helpers import GetAuthCodeServer
                        onedriveclient = get_onedrive_client_from_console(True)
                        save_path = read_onedrive_directory_from_console(onedriveclient)
                        write_line_in_file(configfilepath, ONEDRIVESAVEPATHLINE, save_path)
                        print "Successfully changed your service to storing on OneDrive"
                    elif wheretosave_input == 'd':
                        wheretosave = "Dropbox"
                        write_line_in_file(configfilepath, WHERETOSAVELINE, wheretosave)
                        install_and_import_package('dropbox')
                        dropboxkey = read_dropbox_key_from_console()
                        dropboxclient = dropbox.client.DropboxClient(dropboxkey)
                        write_line_in_file(configfilepath, DROPBOXKEYLINE, dropboxkey)
                        save_path = read_dropbox_directory_from_console(dropboxclient)
                        write_line_in_file(configfilepath, DROPBOXSAVEPATHLINE, save_path)
                        print "Successfully changed your service to storing in your Dropbox"
                    else:
                        print "Invalid input"
                    sys.exit()
                elif yesorno == 'n':
                    print "Aborted\n"
                else:
                    print "Invalid input\n"
            sys.exit()
        elif paraminput[1] == "-d":
            if not os.path.exists(configfilepath):
                print "This option is not available, since you haven't chosen any service yet. Please restart the script without a command line parameter"
            else:
                wheretosave = read_line_in_file(configfilepath, WHERETOSAVELINE)
                if not wheretosave == "Dropbox":
                    print "You can't change your Dropbox user account, since you currently use another service and not the Dropbox service. To change your service, use the -s parameter"
                else:
                    yesorno = raw_input("Would you like to change your Dropbox user account?<y/n>\n")
                    if yesorno == 'y':
                        install_and_import_package('dropbox')
                        dropboxkey = read_dropbox_key_from_console()
                        dropboxclient = dropbox.client.DropboxClient(dropboxkey)
                        write_line_in_file(configfilepath, DROPBOXKEYLINE, dropboxkey)
                        print "Successfully changed your Dropbox account. Note that if you want to change the directory in your Dropbox, where the downloaded files are stored, you have to use the -c parameter"
                    elif yesorno == 'n':
                        print "Aborted\n"
                    else:
                        print "Invalid input\n"
            sys.exit()
        elif paraminput[1] == "-g":
            if not os.path.exists(configfilepath):
                print "This option is not available, since you haven't chosen any service yet. Please restart the script without a command line parameter"
            else:
                wheretosave = read_line_in_file(configfilepath, WHERETOSAVELINE)
                if not wheretosave == "Google Drive":
                    print "You can't change your Google Drive user account, since you currently use another service and not the Google Drive service. To change your service, use the -s parameter"
                else:
                    yesorno = raw_input("Would you like to change your Google Drive user account?<y/n>\n")
                    if yesorno == 'y':
                        install_and_import_package('google-api-python-client')
                        install_and_import_package('httplib2')
                        drive_service = get_drive_service_from_console()
                        print "Successfully changed your Google Drive account. Note that if you want to change the directory on your Google Drive, where the downloaded files are stored, you have to use the -c parameter"
                    elif yesorno == 'n':
                        print "Aborted\n"
                    else:
                        print "Invalid input\n"
            sys.exit()
        elif paraminput[1] == "-o":
            if not os.path.exists(configfilepath):
                print "This option is not available, since you haven't chosen any service yet. Please restart the script without a command line parameter"
            else:
                wheretosave = read_line_in_file(configfilepath, WHERETOSAVELINE)
                if not wheretosave == " OneDrive":
                    print "You can't change your OneDrive user account, since you currently use another service and not the  OneDrive service. To change your service, use the -s parameter"
                else:
                    yesorno = raw_input("Would you like to change your OneDrive user account?<y/n>\n")
                    if yesorno == 'y':
                        install_and_import_package('onedrivesdk')
                        from onedrivesdk.helpers import GetAuthCodeServer
                        onedriveclient = get_onedrive_client_from_console(True)
                        print "Successfully changed your OneDrive account. Note that if you want to change the directory on your OneDrive, where the downloaded files are stored, you have to use the -c parameter"
                    elif yesorno == 'n':
                        print "Aborted\n"
                    else:
                        print "Invalid input\n"
            sys.exit()
        elif paraminput[1] == "-n":
            if not os.path.exists(configfilepath):
                print "This option is not availible, until you restart the script without a command line argument"
            else:
                enableordisable = ""
                towrite = ""
                notify = read_line_in_file(configfilepath, NOTIFICATIONLINE)
                if notify == "True":
                    enableordisable = "disable"
                    towrite = "False"
                elif notify == "False":
                    enableordisable = "enable"
                    towrite = "True"
                else:
                    print "Your config-file is corrupted and deleted now, please restart the script to create a new config-file"
                    os.remove(configfilepath)
                    sys.exit()
                yesorno = raw_input("Would you like to " + enableordisable + " notification via Pushbullet? <y/n>\n")
                if yesorno == 'y':
                    if notify == "False":
                        install_and_import_package("pushbullet")
                        while pushbulletkey == "":
                            try:
                                pushbulletkey = raw_input("Please enter your Pushbullet API-access-token. If you haven't set one yet, visit 'https://www.pushbullet.com/#settings/account' \n")
                                pushbullet.Pushbullet(pushbulletkey)
                            except pushbullet.InvalidKeyError:
                                print "The access-token you entered is invalid."
                                pushbulletkey = ""
                        write_line_in_file(configfilepath, PUSHBULLETKEYLINE, pushbulletkey)
                    write_line_in_file(configfilepath, NOTIFICATIONLINE, towrite)
                    print "Successfully updated the config file"
                elif yesorno == 'n':
                    print "Aborted\n"
                else:
                    print "Invalid input\n"
            sys.exit()
        elif paraminput[1] == "-h":
            print_help()
            sys.exit()
        else:
            print "Unknown command line parameter, here are the available parameters:\n"
            print_help()
            sys.exit()
    elif len(paraminput) - 1 > 1:
        sys.exit()

    # Create or read the config-file
    if not os.path.exists(appdatapath):
        os.makedirs(appdatapath)
    if not os.path.exists(configfilepath):
        print "\nIt seems that you run this script for the first time\n"
        wheretosave_input = raw_input(
            "Where should I save your downloaded files? <l/o/g/d>\n - on local harddrive (l)\n - on OneDrive (o)\n - on Google Drive (g)\n - in your Dropbox (d)\n")
        if wheretosave_input == 'l':
            wheretosave = "Local"
        elif wheretosave_input == 'g':
            pathtodrivejson = path.join(appdatapath, DRIVESJSONNAME)
            with open(pathtodrivejson, "wb") as json:
                json.write(JSONTEXT)
            wheretosave = "Google Drive"
            install_and_import_package('google-api-python-client')
            install_and_import_package('httplib2')
            drive_service = get_drive_service_from_console()
        elif wheretosave_input == 'o':
            wheretosave = "OneDrive"
            install_and_import_package('onedrivesdk')
            from onedrivesdk.helpers import GetAuthCodeServer
            onedriveclient = get_onedrive_client_from_console(True)
        elif wheretosave_input == 'd':
            wheretosave = "Dropbox"
            install_and_import_package('dropbox')
            dropboxkey = read_dropbox_key_from_console()
            dropboxclient = dropbox.client.DropboxClient(dropboxkey)
        else:
            print "Invalid input"
            sys.exit()

        touch_file(configfilepath, COUNT_DATA_STORED_IN_CONFIG)

        write_line_in_file(configfilepath, WHERETOSAVELINE, wheretosave)
        if wheretosave == 'Local':
            save_path = read_directory_from_console()
            write_line_in_file(configfilepath, LOCALSAVEPATHLINE, save_path)
        elif wheretosave == 'Google Drive':
            save_path = read_drive_directory_from_console(drive_service)
            write_line_in_file(configfilepath, DRIVESAVEPATHLINE, save_path)
        elif wheretosave == 'OneDrive':
            save_path = read_onedrive_directory_from_console(onedriveclient)
            write_line_in_file(configfilepath, ONEDRIVESAVEPATHLINE, save_path)
        elif wheretosave == 'Dropbox':
            write_line_in_file(configfilepath, DROPBOXKEYLINE, dropboxkey)
            save_path = read_dropbox_directory_from_console(dropboxclient)
            write_line_in_file(configfilepath, DROPBOXSAVEPATHLINE, save_path)
        overwrite = read_overwrite_from_console()
        write_line_in_file(configfilepath, OVERWRITELINE, overwrite)
        username = read_username_from_console()
        write_line_in_file(configfilepath, USERNAMELINE, username)
        password = read_password_from_console()
        write_line_in_file(configfilepath, PASSWORDLINE, base64.b64encode(password))
        write_line_in_file(configfilepath, LOGFILELINE, DEFAULTWRITELOGFILE)
        write_line_in_file(configfilepath, NOTIFICATIONLINE, DEFAULTNOTIFICATIONLINE)
    else:  # Read from config-file
        num_lines = sum(1 for line in open(configfilepath))
        if num_lines != COUNT_DATA_STORED_IN_CONFIG:
            print "Your config-file is corrupted and deleted now, please restart the script to create a new config-file\n"
            os.remove(configfilepath)
            sys.exit()
        wheretosave = read_line_in_file(configfilepath, WHERETOSAVELINE)
        if wheretosave == "Local":
            save_path = read_line_in_file(configfilepath, LOCALSAVEPATHLINE)
        elif wheretosave == "Google Drive":
            install_and_import_package('google-api-python-client')
            install_and_import_package('httplib2')
            store = oauth2client.file.Storage(path.join(appdatapath, DRIVECREDENTIALSNAME))
            credentials = store.get()
            http = credentials.authorize(httplib2.Http())
            drive_service = discovery.build('drive', 'v3', http=http)
            if not credentials or credentials.invalid:
                print "Invalid Google-Drive credentials. To change your Google Drive account, please use the -g parameter\n"
                sys.exit()
            save_path = read_line_in_file(configfilepath, DRIVESAVEPATHLINE)
        elif wheretosave == "OneDrive":
            install_and_import_package('onedrivesdk')
            from onedrivesdk.helpers import GetAuthCodeServer
            onedriveclient = get_onedrive_client_from_console(False)
            save_path = read_line_in_file(configfilepath, ONEDRIVESAVEPATHLINE)
        elif wheretosave == "Dropbox":
            install_and_import_package('dropbox')
            dropboxclient = dropbox.client.DropboxClient(read_line_in_file(configfilepath, DROPBOXKEYLINE))
            save_path = read_line_in_file(configfilepath, DROPBOXSAVEPATHLINE)
        username = read_line_in_file(configfilepath, USERNAMELINE)
        password_encrypted = read_line_in_file(configfilepath, PASSWORDLINE)
        password = base64.b64decode(password_encrypted)
        createlogfile = read_line_in_file(configfilepath, LOGFILELINE)
        notification = read_line_in_file(configfilepath, NOTIFICATIONLINE)
        if notification == "True":
            pushbulletkey = read_line_in_file(configfilepath, PUSHBULLETKEYLINE)
        overwrite = read_line_in_file(configfilepath, OVERWRITELINE)

    # Send requests to get the following cookies: cookie_seminar_session, cookie_shibstate

    try:
        r = requests.get("http://studip.uni-passau.de/studip/")
        cookie_seminar_session = r.cookies
        r = requests.get("https://studip.uni-passau.de/studip/index.php?again=yes&sso=shib",
                         cookies=cookie_seminar_session, allow_redirects=False)
        location = r.headers['location']
        r = requests.get(location, allow_redirects=False)
        cookie_shibstate = r.cookies
        # Send request to get the following cookies: sibboleth_cookies (consisting of cookie_jsessionid and cookie_idp_authn_lc_key)
        location = r.headers['location']
        r = requests.get(location, cookies=cookie_seminar_session, allow_redirects=True)

        # Extract the two sibboleth-cookies from request
        two_sibboleth_cookies = r.request.headers['Cookie']
        index = two_sibboleth_cookies.find(';')
        cookie_jsessionid = two_sibboleth_cookies[:index]
        index_jsession = cookie_jsessionid.find('=')
        cookie_jsessionid_name = cookie_jsessionid[:index_jsession]
        cookie_jsessionid_value = cookie_jsessionid[index_jsession + 1:]
        cookie_idp_authn_lc_key = two_sibboleth_cookies[index + 2:]
        index_idp_authn = cookie_idp_authn_lc_key.find('=')
        cookie_idp_authn_lc_key_name = cookie_idp_authn_lc_key[:index_idp_authn]
        cookie_idp_authn_lc_key_value = cookie_idp_authn_lc_key[index_idp_authn + 1:]

        sibboleth_cookies_string = '{"' + cookie_jsessionid_name + '":"' + cookie_jsessionid_value + '", "' + cookie_idp_authn_lc_key_name + '":"' + cookie_idp_authn_lc_key_value + '"}'
        sibboleth_cookies = eval(sibboleth_cookies_string)

        # Send post-request with username and password to get the following cookie: cookie_idp_session
        payload = {'j_username': username, 'j_password': password}
        r = requests.post("https://sso.uni-passau.de/idp/Authn/UserPassword", cookies=sibboleth_cookies, data=payload,
                          allow_redirects=False)
        cookie_idp_session = r.cookies

        # Combine cookie_idp_session and sibboleth_cookies
        cookie_session_name = str(cookie_idp_session.keys())
        cookie_session_name = cookie_session_name.replace("['", "")
        cookie_session_name = cookie_session_name.replace("']", "")
        cookie_session_value = str(cookie_idp_session.values())
        cookie_session_value = cookie_session_value.replace("['", "")
        cookie_session_value = cookie_session_value.replace("']", "")
        sibboleth_and_idp_session_cookies_string = '{"' + cookie_jsessionid_name + '":"' + cookie_jsessionid_value + '", "' + cookie_idp_authn_lc_key_name + '":"' + cookie_idp_authn_lc_key_value + '", "' + cookie_session_name + '":"' + cookie_session_value + '"}'
        sibboleth_and_idp_session_cookies = eval(sibboleth_and_idp_session_cookies_string)
    except Exception, e:
        handle_error(e)

    # Send request to receive the html file that contains the Javascript 'Continue'-Button
    try:
        location = r.headers['location']
        r = requests.get(location, cookies=sibboleth_and_idp_session_cookies)
        javascripttext = r.text
    except Exception, e:
        handle_error(e)
    try:
        # Extract the two variables 'relay-state' and 'saml-response', that must be sent back to the server in a post-request
        indexstart = javascripttext.find('name="RelayState" value="')
        indexend = javascripttext.find('"/>', indexstart)
        relaystate = javascripttext[indexstart + len('name="RelayState" value="'):indexend]

        parser = HTMLParser.HTMLParser()

        relaystate = parser.unescape(relaystate)

        indexstart = javascripttext.find('name="SAMLResponse" value="')
        indexend = javascripttext.find('"/>', indexstart)
        samlresonse = javascripttext[indexstart + len('name="SAMLResponse" value="'):indexend]
        samlresonse = parser.unescape(samlresonse)

        # Send post-request with 'relay-state' and 'saml-response' to get the following cookie: shibsession
        payload = {'RelayState': relaystate, 'SAMLResponse': samlresonse}
        r = requests.post("https://studip.uni-passau.de/Shibboleth.sso/SAML2/POST", cookies=cookie_shibstate,
                          data=payload, allow_redirects=False)
        shibsession = r.cookies

        # Send requests to receive the StudIP start website
        location = r.headers['location']
        r = requests.get(location, cookies=shibsession, allow_redirects=False)
        location = r.headers['location']
        cookies_seminar_session_and_shibsession = cookie_seminar_session.copy()
        cookies_seminar_session_and_shibsession.update(shibsession)
        r = requests.get(location, cookies=cookies_seminar_session_and_shibsession, allow_redirects=False)
        r = requests.get("https://studip.uni-passau.de/studip/dispatch.php/start",
                         cookies=cookies_seminar_session_and_shibsession, allow_redirects=False)

        # Send requests to receive the StudIP courses website
        reload(sys)
        sys.setdefaultencoding('utf-8')
        r = requests.get("https://studip.uni-passau.de/studip/dispatch.php/my_courses",
                         cookies=cookies_seminar_session_and_shibsession, allow_redirects=False)
        html = r.text

        index_id_my_seminars = html.find('id="my_seminars"')
        index_tbody_open = html.find('</thead>', index_id_my_seminars)
        index_tbody_close = html.find('</table>', index_tbody_open)
        if (index_tbody_open >= 0 and index_tbody_close >= 0):
            tbody = html[index_tbody_open:index_tbody_close]
            index_tr_open = tbody.find('<tr>')
            index_tr_close = tbody.find('</tr>')
            counter = 0
            aretherenewfiles = False
            bushbulletbody = ""
            while index_tr_open >= 0:
                counter += 1
                tr = tbody[index_tr_open:index_tr_close]
                index_temp = tr.find('<td style="text-align: left">')
                index_temp = tr.find('<a href="', index_temp)
                index_coursename_start = tr.find('>', index_temp + len('<a href="'))
                index_coursename_end = tr.find('</a>', index_coursename_start)
                if (index_coursename_start >= 0 and index_coursename_end >= 0):
                    coursename = tr[index_coursename_start + len('>'):index_coursename_end]
                    coursename = ' '.join(coursename.split())
                if tr.find('https://studip.uni-passau.de/studip/assets/images/icons/red/new/files.svg') >= 0:
                    aretherenewfiles = True
                    print_and_log("\nThere are new files for the course " + coursename)
                    index_temp = tr.find('title="Teilnehmende"')
                    index_href_start = tr.find('<a href="', index_temp)
                    index_href_start = index_href_start + len('<a href="')
                    index_href_end = tr.find('"', index_href_start)
                    linktonewfiles = tr[index_href_start:index_href_end]
                    linktonewfiles = parser.unescape(linktonewfiles)
                    if len(linktonewfiles) > 0:
                        r = requests.get(linktonewfiles, cookies=cookies_seminar_session_and_shibsession,
                                         allow_redirects=True)
                        coursefileshtml = r.text
                        tempindex = coursefileshtml.find('id="main_content"')
                        index_downloadlink_start = coursefileshtml.find('<a class="button" href="', tempindex)
                        index_downloadlink_start = index_downloadlink_start + len('<a class="button" href="')
                        index_downloadlink_end = coursefileshtml.find('"', index_downloadlink_start)
                        downloadlink = coursefileshtml[index_downloadlink_start:index_downloadlink_end]
                        downloadlink = 'https://studip.uni-passau.de/studip/folder.php?' + downloadlink
                        downloadlink = parser.unescape(downloadlink)
                        bushbulletbody += "- " + coursename + ":\n"
                        print "Downloading files for " + coursename + "..."
                        r = requests.get(downloadlink, cookies=cookies_seminar_session_and_shibsession,
                                         allow_redirects=True)
                        sc = set(FORBIDDEN_CHARS)
                        coursename = ''.join([c for c in coursename if c not in sc])
                        pathtozip = path.join(appdatapath, coursename + ".zip")
                        pathtoextractzip = path.join(appdatapath, coursename)
                        with open(pathtozip, "wb") as code:
                            code.write(r.content)
                        print "Done"
                        if not path.exists(pathtoextractzip):
                            os.makedirs(pathtoextractzip)
                        zip = zipfile.ZipFile(pathtozip, 'r')
                        numberoffiles = len(zip.infolist())
                        for file in zip.infolist():
                            filename = file.filename
                            tosave = path.join(pathtoextractzip, filename)
                            outputfile = open(tosave, "wb")
                            shutil.copyfileobj(zip.open(filename), outputfile)
                            outputfile.close()
                        zip.close()
                        if os.path.exists(pathtozip):
                            os.remove(pathtozip)
                        files = os.listdir(pathtoextractzip)
                        numberoffiles = len(files) - 1
                        progress = 0
                        drawProgressBar("Saving files: ", progress * (1.0 / numberoffiles))
                        for file in files:
                            filepath = path.join(pathtoextractzip, file)
                            if not os.path.isdir(filepath):
                                if not filepath.endswith('dateiliste.csv'):
                                    newfile = open(filepath, 'rb')
                                    bushbulletbody += "\t- " + os.path.basename(newfile.name) + "\n"
                                    savefile(coursename, newfile)
                                    newfile.close()
                                    progress += 1
                            drawProgressBar("Saving files: ", progress * (1.0 / numberoffiles))
                        print "\nDone"
                        shutil.rmtree(pathtoextractzip)
                index_tr_open = tbody.find('<tr>', index_tr_open + len('<tr>'))
                index_tr_close = tbody.find('</tr>', index_tr_close + len('</tr>'))
            if not aretherenewfiles:
                print_and_log("There are no new files for you")
            else:
                if notification == "True":
                    try:
                        install_and_import_package("pushbullet")
                        pb = pushbullet.Pushbullet(pushbulletkey)
                        pb.push_note("New StudIP files", bushbulletbody)
                    except Exception, e:
                        print_and_log("Failed to send notification via Pushbullet")
                print_and_log("\nFinished")
        else:
            print_and_log("Error: tbody-tags could not be found")

        # Logout
        r = requests.get("https://studip.uni-passau.de/studip/logout.php?sso=shib",
                         cookies=cookies_seminar_session_and_shibsession, allow_redirects=True,
                         headers={'Connection': 'close'})
        r.connection.close()
        write_to_logfile("Script finished")
    except Exception, e:
        handle_error(e)

if __name__ == "__main__":
    main()
