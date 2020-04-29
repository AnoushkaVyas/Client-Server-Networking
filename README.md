# Project
File sharing protocol is implemented between a client and a server using File Transfer Protocol (FTP) which uses TCP/IP protocol to communicate between ports.

## Language and Libraries
Python 3 is used for implementing this client server architecture. Libraries used are: 
- socket
- os, sys
- hashlib
- tqdm
- struct
- time
- subprocess
- shutil

## Running
There are two files, `client.py` and `server.py`. Both the files can be put in same folder in your local machine or different folders. Open two different terminals and in the respective folder run:
``` console
python3 client.py
```
``` console
python3 server.py
```
In the client side, `Enter your name` prompt will come and upon entering a virtual terminal will be created. If the connection with the server is successful `Server bind complete` will be printed on the server side.

## Commands
``` console
ls
````
Displays the files in the folder in which `server.py` is run.

``` console
lc
```
Displays the files in the folder in which `client.py` is run.

``` console
quit
```
Quits the connection with the server

``` console
history
```
Displays the commands used in the current session.

``` console
IndexGet longlist
```
Displays the entire list of files in folder of the server with `filesize`, `timestamp`, `name` and `filetype`.

``` console
IndexGet longlist *.txt word
```
Displays the entire list of `*.txt` files with a particular `word` in it in folder of the server with `filesize`, `timestamp`, `name` and `filetype`.

``` console
IndexGet shortlist <YYYY-MM-DD_HH:MM:SS> <YYYY-MM-DD_HH:MM:SS>
```
Displays the entire list of files in folder of the server with `filesize`, `timestamp`, `name` and `filetype` between a specific set of timestamps. 

``` console
IndexGet shortlist <YYYY-MM-DD_HH:MM:SS> <YYYY-MM-DD_HH:MM:SS> *.filetype
```
Displays the list of files of type `*.txt` or `*.pdf` in folder of the server with `filesize`, `timestamp`, `name` and `filetype` between a specific set of timestamps. 

``` console
FileHash checkall
```
Displays the `filename`, `MD5 Checksum of the file on both the server and client side` and `last modified timestamp` of all the files in the server side. It checks the hash of the files on both the client and server side and prints whether they match or not.

``` console
FileHash verify filename
```
Displays the `filename`, `MD5 Checksum of the file on both the server and client side` and `last modified timestamp` of  the file in the server side. It checks the hash of the file on both the client and server side and prints whether they match or not.


``` console
FileUpload filename mode
```
Uploads file with either `TCP` or `UDP` protocols.

``` console
FileDownload filename mode
```
Downloads file from the server using `TCP` or `UDP` and displays `filename`, `filesize`, `MD5checksum` and `timestamp`.

``` console
Cache verify filename
```
The size of the cache is `3` and the cache is session specific. This commands checks the presence of file in the session cache and if it is there it prints the `Filename` and `Filesize` and if it is not it calls the FileDownload command with TCP and downloads it in the Cachefolder. If the cache is full then the file with least number of requests in the current session is removed form Cachefolder.

``` console
Cache show
```
The size of the cache is `3` and the cache is session specific. This commands displays the `Filename` and `Filesize` of all the files in the `Cachefolder`.
