import socket
import os, sys
import hashlib
import tqdm
import struct


#server name goes in HOST
HOST = 'localhost'
PORT = 2000 
cache_dict={}
cache_size=3
listoffile=os.listdir("./Cachefolder/")


def IndexGet(command):
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.connect((HOST, PORT))
    comm = command.split(' ')
    if comm[1] == 'shortlist':
        send_one_message(sckt, command.encode('utf-8'))
        rec = sckt.recv(1024)
        rec=rec.decode('utf-8')
        recvd = rec.split('\n')
        for filename in recvd:
            print (filename)

    elif (comm[1]=='longlist'):
        send_one_message(sckt, command.encode('utf-8'))
        filelist = sckt.recv(1024)
        filelist=filelist.decode('utf-8')
        filelist=filelist.split("\n")
        for i in range(0,len(filelist)):
            print(filelist[i])
    sckt.close()
    return

def listdirServer(command):
    sckt=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.connect((HOST, PORT))
    send_one_message(sckt, command.encode('utf-8'))
    listoffiles = sckt.recv(1024).decode('utf-8')
    listoffiles = listoffiles.split("\n")
    for filename in listoffiles:
        print(filename)
    sckt.close()
    return

def upload(command):
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.connect((HOST, PORT))
    send_one_message(sckt, command.encode('utf-8'))
    comm = command.split(' ')
    filename = comm[1]
    with open(filename, 'rb') as sendfile:
        for data in sendfile:
            print(data)
            send_one_message(sckt, data)
    print ('Upload Finished')
    sckt.close()
    return

def cacheshow():
    listoffile=os.listdir("./Cachefolder/")
    if len(listoffile) ==0 :
        print("Cache Folder is empty")
    else:
        for files in listoffile:
            filesize = os.stat(files).st_size
            print("Filename: ", files, " Filesize: ", filesize)

def cacheverify(command):
    comm = command.split(' ')
    filename = comm[2]
    if filename in cache_dict.keys():
        cache_dict[filename]['count']=cache_dict[filename]['count']+1
        print("File already present in cache")
        print("Filename: ",filename," File size: ",cache_dict[filename]['Filesize'])
    else:
        filesize=download('FileDownload'+' '+filename,'cache')
        no_of_items=len(cache_dict)
        if no_of_items==cache_size:
            l1=list(cache_dict.keys())[0]
            l2=list(cache_dict.keys())[1]
            l3=list(cache_dict.keys())[2]
            num1=cache_dict[l1]['count']
            num2=cache_dict[l2]['count']
            num3=cache_dict[l3]['count']
            min_count=min(num1,num2,num3)
            if min_count==num1:
                cache_dict.pop(l1)
                os.remove('./Cachefolder/'+ l1)
            elif min_count==num2:
                cache_dict.pop(l2)    
                os.remove('./Cachefolder/'+ l2)
            elif min_count==num3:
                cache_dict.pop(l3)
                os.remove('./Cachefolder/'+ l3)
                
        cache_dict[filename]={'Filesize': filesize, 'count':1}

def download(command,flag='normaldownload'):
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.connect((HOST, PORT))
    send_one_message(sckt, command.encode('utf-8'))
    comm = command.split(' ')
    filename = comm[1]
    filesize = recv_one_message(sckt)
    filesize = filesize.decode()
    filetime = recv_one_message(sckt)
    filetime = filetime.decode()
    print('Downloading %s'%filename + ' of size -> %s B'%filesize+' Last modified at -> %s'%filetime)
    filehash = recv_one_message(sckt)
    filehash = filehash.decode()
    print('MD5SUM => ',filehash)
    if flag=='cache':
        with open('./Cachefolder/'+filename, 'wb') as savefile:
            while True:
                data = sckt.recv(1024)
                if not data:
                    break
                savefile.write(data)
        savefile.close()
    else:
        with open(filename, 'wb') as savefile:
            while True:
                data = sckt.recv(1024)
                if not data:
                    break
                savefile.write(data)
        savefile.close()
    print ('Download Finished')
    sckt.close()
    return filesize

def md5sum(filename, blocksize=65536):
    hash = hashlib.md5()
    if os.path.isfile(filename):
        with open(filename, "rb") as f:
            for block in iter(lambda: f.read(blocksize), b""):
                hash.update(block)
        return hash.hexdigest()
    else:
        return None


def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)

def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def recv_one_message(sock):
    lengthbuf = recvall(sock, 4)
    if isinstance(lengthbuf,type(None)):
        return None
    length, = struct.unpack('!I', lengthbuf)
    return recvall(sock, length)


def Verify(command):
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.connect((HOST, PORT))
    send_one_message(sckt, command.encode('utf-8'))
    comm = command.split(' ')
    filename = comm[2]
    server_hash = sckt.recv(1024).decode('utf-8')
    client_hash = md5sum(filename)
    if client_hash is None:
        print('Requested filename unavailable')
        sckt.close()
        return None
    lastmod = sckt.recv(1024).decode('utf-8')
    print('Hash from server = %s'%(server_hash))
    print('Hash from client = %s'%(client_hash))
    print('Last Modified ->',lastmod)
    if server_hash == client_hash:
        print('Matched')
    else:
        print('Not Matched')
    sckt.close()
    return filename+' '+server_hash+' '+lastmod


def Checkall(command):
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.connect((HOST, PORT))
    send_one_message(sckt, command.encode('utf-8'))
    comm = command.split(' ')
    storage = []
    while True:
        f = recv_one_message(sckt)
        if f is None:
            print('Completed')
            break
        f_hash_client = md5sum(f)
        if f_hash_client is None:
            print('WARNING -> Requested file missing')
        f_hash_server = recv_one_message(sckt)
        f_hash_server = f_hash_server.decode()
        f_last_mod = recv_one_message(sckt)
        f_last_mod = f_last_mod.decode()
        print('Filename -> ',f)
        print('Hash from server = %s'%(f_hash_server))
        print('Hash from client = %s'%(f_hash_client))
        print('Last Modified =>',f_last_mod)
        if f_hash_server == f_hash_client:
            print('Matched')
        else:
            print('Not Matched')
        print('-----------------------------------------------')
        storage.append(f.decode()+' '+f_hash_server+' '+f_last_mod)
    sckt.close()
    return storage

def FileHash(command):
    comm = command.split(' ')
    if comm[1] == 'verify':
        return Verify(command)
    elif comm[1] == 'checkall':
        return Checkall(command)



def quit(command):
    sckt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sckt.connect((HOST, PORT))
    send_one_message(sckt, command.encode('utf-8'))
    sckt.close()
    return



name = input('Enter your name :-')
print('Welcome to FTP. This is client. Start server first.')
historylist=[]
while(True):
    sys.stdout.write('%s -> ' %name)
    sys.stdout.flush()
    command = sys.stdin.readline().strip()
    historylist.append(command)
    if (command == 'quit'):
        quit(command) 
        break
    elif(command=='history'):
        for hist in historylist:
            print(hist)
    elif (command == 'lc'):
        path = os.getcwd()
        dirs = os.listdir(path)
        for f in dirs:
            print(f)
    elif (command == 'ls'):
        listdirServer(command)
    else:
        ip = command.split()
        if (ip[0]=='IndexGet'):
            IndexGet(command)
            pass
        elif (ip[0]=='FileHash'):
            filehashdata = FileHash(command)
        elif (ip[0]=='FileUpload'):
            upload(command)
        elif (ip[0]=='FileDownload'):
            download(command)
        elif (ip[0]=='Cache'):
            if (ip[1]=='verify'):
                cacheverify(command)
            elif (ip[1]=='show'):
                cacheshow()