from concurrent.futures import ThreadPoolExecutor
import subprocess
import socket


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

network = get_local_ip().rsplit(".", 1)[0] + "."

def ping(ip):
    r = subprocess.run(["ping", "-n", "1", "-w", "40", ip],
                       stdout=subprocess.DEVNULL)
    return ip if r.returncode == 0 else None

def get_service(ip, port):
    try:
        s = socket.socket()
        s.settimeout(0.8)
        s.connect((ip, port))

        # HTTP DETECTION        
        if port == 80:
            s.send(b"HEAD / HTTP/1.0\r\nHost: test\r\n\r\n")
            data = s.recv(1024).decode(errors="ignore")

            server = ""
            for line in data.split("\r\n"):
                if "Server:" in line:
                    server = line
                    break

            return f"HTTP → {server if server else 'Unknown Web Server'}"
        
        # HTTPS (basic hint only)
        if port == 443:
            return "HTTPS → Encrypted Service (no banner without TLS lib)"

        
        # SSH BANNER
        if port == 22:
            s.send(b"\n")
            data = s.recv(1024).decode(errors="ignore")
            return f"SSH → {data.strip()}"

        
        #SMB (very basic hint)        
        if port == 445:            
            return "SMB → Windows File Sharing (version unknown) Eternalblue smb"        
        try:
            data = s.recv(1024).decode(errors="ignore")
            return f"Service Banner → {data[:50]}"
        except:
            return f"Open port {port} (no banner)"

    except:
        return None
    finally:
        s.close()

def scan_ports(ip):
    ports = [22, 80, 443, 445]
    openp = []
    
    for p in ports:
        s = socket.socket()
        s.settimeout(0.2)

        if s.connect_ex((ip, p)) == 0:
            service = get_service(ip, p)
            openp.append((p, service))

        s.close()

    return openp


def worker(ip):
    if ping(ip):
        ports = scan_ports(ip)
        return ip, ports


def scan():
    ips = [network + str(i) for i in range(1, 255)]

    with ThreadPoolExecutor(max_workers=120) as ex:
        results = ex.map(worker, ips)

    return [r for r in results if r]