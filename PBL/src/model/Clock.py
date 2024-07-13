import socket
import threading


class Clock:


    def __init__(self):
        self.ip_clock = socket.gethostbyname(socket.gethostname())
        #
        self.port = "2503"
        #
        #self.list_clocks = [self.ip_clock]
        self.list_clocks = [self.port]
        self.trying_recconection = {}
        self.time = 10
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
            print("Tentando reconexão com ", ip_clock, ": ", boolean)

    
    def set_ready_for_connection(self, ready_for_connection: bool):
        with self.lock:
            self.ready_for_connection = ready_for_connection
            print("Pronto para conexão: ", ready_for_connection)

    
    def set_leader_is_elected(self, leader_is_elected: bool):
        with self.lock:
            self.leader_is_elected = leader_is_elected
            print("Líder está eleito: ", leader_is_elected)

    
    def set_ip_leader(self, ip_leader: str):
        with self.lock:
            self.ip_leader = ip_leader
            print("IP do líder: ", ip_leader)


    def get_clocks_on(self):
        list_clocks = []
        for key in self.trying_recconection.keys():
            #if key != self.ip_clock and self.trying_recconection[key] == False:
            if key != self.port and self.trying_recconection[key] == False:
                list_clocks.append(key)
        
        return list_clocks

    
    def sort_list_clocks(self):
        for i in range(1, len(self.list_clocks)):
            insert_index = i
            current_value = self.list_clocks.pop(i)
            for j in range(i - 1, -1, -1):
                if int(self.list_clocks[j].replace(".","")) > int(current_value.replace(".","")):
                    insert_index = j
            self.list_clocks.insert(insert_index, current_value)

    