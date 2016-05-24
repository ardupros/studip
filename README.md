#StudIP File Downloader

##Description
This script is written for **Python 2.7.11** and is compatible with **Windows**, **Mac OS X** and **Linux**.<br />
It may also work for Python 2.7.9 and greater <br />
The purpose of this script is to check for new files on the StudIP-website of the university of Passau, which are then downloaded and saved in your desired destination folder.<br />
You can currently select one of the following services for storing the downloaded files:
- Saving on your local disk
- Dropbox
- Google Drive
- OneDrive

##Required Modules
Required modules are (according wich service you choose):
- requests
- Dropbox
- Google Drive: google-api-python-client and httplib2
- OneDrive: onedrivesdk

These modules will be installed automatically as soon as they are needed. Therefore the script has to be started with administrator privileges.

##Usage
Download the script, navigate to the containing directory and execute the script with `python request.py`

######Optional Parameters:
Use: `python request.py -[parameter]`. `[parameter]` can be one of the following:

| Parameter | Description |
| --- | --- |
| h [help] | Prints out the help |
| s [service] | Change the service you want to use to save the downloaded files |
| d [dropbox] | Change your Dropbox account |
| g [google drive] | Change your Google Drive account |
| o [onedrive] | Change your OneDrive account |
| c [change directory] | Change the directory where the downloaded files are stored |
| u [username] | Change the username, that is used for the studip login |
| p [password] | Change the password, that is used for the studip login |
| l [logfile] | Enables or disables logfiles |
| r [reset] | Resets all your settings |
