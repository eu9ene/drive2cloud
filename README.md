**Drive2Cloud**
 
 Uploads files from network/local drive to cloud for backup.
 It does not sync files from cloud to drive - it is just downloading provided by all cloud drives.

 Supported protocols:
 - FTP
 - Samba (TODO)
 - Local file system
 
 Supported clouds:
 - Dropbox
 - Google Drive (TODO)

 Features:
 - uploads the specified directory to cloud directory
 - indexes all uploaded files to not upload them again
 - finds new files and directories on the drive
 - reads initial state from cloud to build index
 - sync scheduling
 - resumes processing after interruption
 - Docker support


  !!! It never deletes anything from cloud !!!
  
  If there are files in the cloud and there's no such file/directories on drive, 
  it just writes about it in  logs.
  
  
  **Usage**
  
  Manual run mode:
  
  to rebuild local files index `python3 drive2cloud.py --reindex True`
  
  to use local file index `python3 drive2cloud.py --reindex False`
  
  Server mode:
  
  `python3 drive2cloud.py --reindex True --interval-hours 24`
  
  or with Docker
  `bash docker_run.sh`
  
  




