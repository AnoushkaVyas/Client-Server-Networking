import os, sys, hashlib, time
import socket
import subprocess
import struct

#Need subprocess for timestamp based indexing in IndexGet

HOST = 'localhost'
PORT = 5000
UDP_port=9999
#Initialise a socket at the port specified
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print ('Server Created')
except socket.error as msg :
    print ('Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()

try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
print ('Socket bind complete')

s.listen(1)
print ('Server listening')

# Now main functions after server is live and listening
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


while(True):
    conn, addr = s.accept()
    print ('Connected with ' + addr[0] + ' at ' + str(addr[1]))
    sys.stdout.write('Server -> ')
    sys.stdout.flush()
    req = recv_one_message(conn).decode()
    print ('Client sent %s'%(req))
    request = req.split(' ')
    if (req == 'quit'):
        print('Quitting server...')
        break
    elif (req == 'ls'):
        listoffiles = ""
        path = os.getcwd()
        dirs = os.listdir(path)
        for f in dirs:
            listoffiles+=f+"\n"
        conn.send(listoffiles.encode('utf-8'))

    elif (request[1]=='shortlist'):
        if(len(request)==5):
            if(request[4]=='*.txt'):
                cmd_a=  "echo " + request[2] + " | sed 's/_/ /g'"
                tmp_a=subprocess.check_output(cmd_a,shell=True).strip()
                tmp_a=tmp_a.decode('utf-8')
                a = '"'+tmp_a+'"'
                cmd_b=  "echo " + request[3] + " | sed 's/_/ /g'"
                tmp_b=subprocess.check_output(cmd_b,shell=True).strip()
                tmp_b=tmp_b.decode('utf-8')
                b = '"'+tmp_b+'"'
                c = '"*.txt"'
                cmd="find . -type f -name " + c + " -newermt " + a + " ! -newermt " + b + " 2>/dev/null -exec ls -lh \{\} \; | cut -d' '  -f5,6,7,8,9"
                listoffiles=subprocess.check_output(cmd,shell=True)
                conn.send(listoffiles)
            elif(request[4]=='*.pdf'):
                cmd_a=  "echo " + request[2] + " | sed 's/_/ /g'"
                tmp_a=subprocess.check_output(cmd_a,shell=True).strip()
                tmp_a=tmp_a.decode('utf-8')
                a = '"'+tmp_a+'"'
                cmd_b=  "echo " + request[3] + " | sed 's/_/ /g'"
                tmp_b=subprocess.check_output(cmd_b,shell=True).strip()
                tmp_b=tmp_b.decode('utf-8')
                b = '"'+tmp_b+'"'
                c = '"*.pdf"'
                cmd="find . -type f -name " + c + " -newermt " + a + " ! -newermt " + b + " 2>/dev/null -exec ls -lh \{\} \; | cut -d' '  -f5,6,7,8,9"
                listoffiles=subprocess.check_output(cmd,shell=True)
                conn.send(listoffiles)
        elif(len(request)==4):
            cmd_a=  "echo " + request[2] + " | sed 's/_/ /g'"
            tmp_a=subprocess.check_output(cmd_a,shell=True).strip()
            tmp_a=tmp_a.decode('utf-8')
            a = '"'+tmp_a+'"'
            cmd_b=  "echo " + request[3] + " | sed 's/_/ /g'"
            tmp_b=subprocess.check_output(cmd_b,shell=True).strip()
            tmp_b=tmp_b.decode('utf-8')
            b = '"'+tmp_b+'"'
            cmd="find . -type f -newermt " + a + " ! -newermt " + b + " 2>/dev/null -exec ls -lh \{\} \; | cut -d' '  -f5,6,7,8,9"
            listoffiles=subprocess.check_output(cmd,shell=True)
            conn.send(listoffiles)
        else:
            print('Incorrect Input Format')
    elif (request[1]=='longlist'):
        if(len(request)==4):
            if(request[2]=='*.txt'):
                listoffiles=[]
                cmd = "find . -type f -name '*.txt' 2>/dev/null | sed 's|^./||' | xargs grep -w -l "+"'"+ request[3]+"'"
                tmp_listoffiles = subprocess.check_output(cmd,shell=True)
                tmp_listoffiles = tmp_listoffiles.decode('utf-8')
                lines=tmp_listoffiles.splitlines()
                for line in lines:
                    tmp_cmd = "ls -l | grep " + line + " | awk '{print $5, $6, $7, $8, $9}'"
                    tmp2_listoffiles = subprocess.check_output(tmp_cmd,shell=True)
                    listoffiles.append(tmp2_listoffiles)
                blist=b''.join(listoffiles)
                conn.send(blist)
        elif(len(request)==2):
            cmd = "ls -l . | awk '{print $5, $6, $7, $8, $9}'"
            listoffiles=subprocess.check_output(cmd,shell=True)
            conn.send(listoffiles)
        else:
            print('Incorrect Input Format')

    elif (request[0] == 'FileHash'):
        if(request[1]== 'verify'):
            filehash = md5sum(request[2])
            if filehash is None:
                print('Requested file not available')
                conn.send(b'None')
                conn.send(b'None')    
            else:
                filelastmod = time.ctime(os.stat(request[2]).st_mtime)
                print('Hash at server -> ',filehash)
                print('Last Modified ->',filelastmod)
                conn.send(filehash.encode('utf-8'))
                conn.send(str(filelastmod).encode('utf-8'))
            
        elif (request[1] == 'checkall'):
            path = os.getcwd()
            dirs = os.listdir(path)
            for f in dirs:
                send_one_message(conn, f.encode('utf-8'))
                f_hash = md5sum(f)
                if f_hash is None:
                    print('Requested file not available')
                    send_one_message(conn,b'None')
                    send_one_message(conn,b'None')
                else:    
                    f_lastmod = time.ctime(os.stat(f).st_mtime)
                    print('Accessing -> ',f)
                    print('Hash -> ',f_hash)
                    print('Last Modified -> ',f_lastmod)
                    print('------------------------')
                    send_one_message(conn, f_hash.encode('utf-8'))
                    send_one_message(conn, f_lastmod.encode('utf-8'))
            print('List complete')

    else:
        request = req.split(' ')
        if(len(request) > 1):
            request_file = request[1]
            if (request[0] == 'FileUpload'):
                if request[2]=='UDP':
                    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    udp.bind((HOST,UDP_port))
                    BigC = open(request_file, "wb")
                    ClientBData, clientbAddr = udp.recvfrom(4096)
                    try: 
                        while ClientBData:
                            BigC.write(ClientBData)
                            udp.settimeout(5)
                            ClientBData, clientbAddr = udp.recvfrom(4096)
                    except socket.timeout:
                        udp.close()
                        BigC.close()
                    print("File Downloaded using UDP")
                    
                else:
                    savefile = open(request_file,'wb')
                    rem_req = request[2:]
                    
                    for rems in rem_req:
                        rems+=" "
                        if isinstance(rems,str):
                            savefile.write(rems.encode())
                        elif isinstance(rems,bytes):
                            savefile.write(rems)

                    while(True):
                        data = recv_one_message(conn)
                        if data is None:
                            print('Transfer Complete')
                            break
                        else:
                            if(isinstance(data,str)):
                                savefile.write(data.encode())
                            elif(isinstance(data,bytes)):
                                savefile.write(data)

                    savefile.close()
                    print('Uploaded Successfully with TCP')
                    
            elif (request[0] == 'FileDownload'):
                if os.path.isfile(request_file) is False:
                    print('WARNING -> File requested Does not exist.')
                else:    
                    if request[2]=='UDP':
                        udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        sizeS = os.stat(request_file)
                        sizeSS = sizeS.st_size
                        NumS = int(sizeSS / 4096)
                        NumS = NumS + 1
                        tillSS = str(NumS)
                        tillSSS = tillSS.encode('utf8')
                        udp.sendto(tillSSS, (HOST,UDP_port))
                        udp.sendto(str(sizeSS).encode('utf8'), (HOST,UDP_port))
                        filetime = time.ctime(os.stat(request_file).st_mtime)
                        udp.sendto(str(filetime).encode('utf8'), (HOST,UDP_port))
                        udp.sendto(str(md5sum(request_file)).encode('utf-8'), (HOST,UDP_port))
                        check = int(NumS)
                        GetRunS = open(request_file, "rb")
                        while check != 0:
                            RunS = GetRunS.read(4096)
                            udp.sendto(RunS,(HOST,UDP_port))
                            check -= 1
                        GetRunS.close()
                        print("Sent from Server using UDP")
                        udp.close()
                    
                    else:
                        filesize = os.stat(request_file).st_size
                        filetime = time.ctime(os.stat(request_file).st_mtime)
                        print('Request for Downloading %s'%request_file+' of size ->%s B'%filesize + ' Last modified at %s'%filetime)
                        send_one_message(conn, str(filesize).encode('utf-8'))
                        send_one_message(conn, str(filetime).encode('utf-8'))
                        send_one_message(conn, str(md5sum(request_file)).encode('utf-8'))
                        with open(request_file, 'rb') as sendfile:
                            for data in sendfile:
                                conn.send(data)
                        print ('File Sent')
                    
    conn.close()
s.close()