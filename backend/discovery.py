import socket
import threading
import time

class PeerDiscovery:
    def __init__(self, port, on_peer_discovered):
        self.port = port
        self.on_peer_discovered = on_peer_discovered
        self.running = True
        self.peers = set()

        self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.broadcast_thread = threading.Thread(target=self.broadcast_loop, daemon=True)

        self.listen_thread.start()
        self.broadcast_thread.start()

    def listen_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", 9999))
        while self.running:
            try:
                data, addr = sock.recvfrom(1024)
                peer_url = data.decode()
                if peer_url not in self.peers:
                    self.peers.add(peer_url)
                    self.on_peer_discovered(peer_url)
            except:
                continue

    def broadcast_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        message = f"http://{self.get_ip()}:{self.port}".encode()
        while self.running:
            sock.sendto(message, ("<broadcast>", 9999))
            time.sleep(5)

    def get_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't need to connect, just gets your IP
            s.connect(("10.255.255.255", 1))
            IP = s.getsockname()[0]
        except:
            IP = "127.0.0.1"
        finally:
            s.close()
        return IP

    def stop(self):
        self.running = False
