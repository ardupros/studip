#StudIP File Downloader

##Description
This script is written for **Python 2.7.11** and is compatible with **Windows**, **Mac OS X** and **Linux**.<br />
It may also work for Python 2.7.9 and greater.<br />
The purpose of this script is to check for new files on the StudIP-Website of the University of Passau, which are then downloaded and saved in your desired destination folder.<br />
You can currently select one of the following services for storing the downloaded files:
- Saving on your local drive
- Saving on:
  - Dropbox
  - Google Drive
  - OneDrive

##Required modules
Required modules (depending on which service you choose):
- Required for all services: *requests*
- Required for Dropbox: *dropbox*
- Required for Google Drive: *google-api-python-client* and *httplib2*
- Required for OneDrive: *onedrivesdk*

These modules will be installed automatically as soon as they are needed. Therefore the script has to be started with administrator privileges.

##Usage
Download the script, navigate to its directory and execute the script with `python request.py`

####Optional parameters:
Use: `python request.py -[parameter]`. `-[parameter]` can be one of the following:

| Parameter | Description |
| --- | --- |
| -h [help] | Prints out the help |
| -s [service] | Change the service you want to use to save the downloaded files |
| -d [dropbox] | Change your Dropbox account |
| -g [google drive] | Change your Google Drive account |
| -o [onedrive] | Change your OneDrive account |
| -c [change directory] | Change the directory where the downloaded files are stored |
| -u [username] | Change the username, that is used for the studip login |
| -p [password] | Change the password, that is used for the studip login |
| -f [force override] | Forces to override files that already exist |
| -l [logfile] | Enables or disables logfiles |
| -r [reset] | Resets all your settings |
