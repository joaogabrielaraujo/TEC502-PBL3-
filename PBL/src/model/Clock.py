import socket
import threading


class Clock:


    def __init__(self):
        self.ip_clock = socket.gethostbyname(socket.gethostname())
        #
        self.port = "2501"
        #
        #self.list_clocks = [self.ip_clock]
        self.list_clocks = [self.port]
        self.trying_recconection = {}
        self.time = 0
        self.drift = 0

        self.leader_is_elected = False
        self.ip_leader = None

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

    
    def get_quantity_clocks_on(self):
        count = 0
        for key in self.trying_recconection.keys():
            #if key != self.ip_clock and self.trying_recconection[key] == False:
            if key != self.port and self.trying_recconection[key] == False:
                count += 1
        
        return count

    
    def sort_list_clocks(self):
        for i in range(1, len(self.list_clocks)):
            insert_index = i
            current_value = self.list_clocks.pop(i)
            for j in range(i - 1, -1, -1):
                if int(self.list_clocks[j].replace(".","")) > int(current_value.replace(".","")):
                    insert_index = j
            self.list_clocks.insert(insert_index, current_value)

    