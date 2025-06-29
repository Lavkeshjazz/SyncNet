import socket

def get_ip_address():
    try:
        # Create a dummy socket connection to determine the IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google's public DNS; no real traffic is sent
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        return "Unavailable"
