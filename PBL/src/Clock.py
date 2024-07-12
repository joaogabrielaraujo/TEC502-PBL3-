import socket
import threading


class Clock:


    def __init__(self):
        self.ip_clock = socket.gethostbyname(socket.gethostname())
        self.port = "2501"
        #self.list_clocks = [self.ip_clock]
        self.list_clocks = [self.port]
        self.trying_recconection = {}
        self.time = 0
        self.drift = 0

        self.ready_for_connection = False
        self.lock = threading.Lock()


    def add_clock(self, ip_clock: str):
        with self.lock:
            # adiciona um novo relógio a lista de relógios
            self.list_clocks.append(ip_clock)
            # adiciona o ip do relógio a lista de tentativas de reconexão, indicando que esse relógio caiu
            # False: ta conectado; True: ta tentando reconecção
            self.trying_recconection[ip_clock] = False
    

    def set_trying_recconection(self, ip_clock: str, boolean: bool):
        with self.lock:
            self.trying_recconection[ip_clock] = boolean

    
    def set_ready_for_connection(self, ready_for_connection: bool):
        with self.lock:
            self.ready_for_connection = ready_for_connection