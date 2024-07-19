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
        self.time = 5
        self.drift = 1.0

        self.leader_is_elected = False
        self.ip_leader = None
        self.time_without_leader_request = 0
        self.problem_detected = False

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
            print("\nTentando reconexão com ", ip_clock, ": ", boolean)


    def set_time(self, time: int):
        with self.lock:
            self.time = time
            print("\nTempo atual: ", self.time)


    def set_drift(self, drift: float):
        with self.lock:
            self.drift = drift
            print("\nDrift atual: ", self.drift)

    
    def set_ready_for_connection(self, ready_for_connection: bool):
        with self.lock:
            self.ready_for_connection = ready_for_connection
            print("\nPronto para conexão: ", ready_for_connection)

    
    def set_leader_is_elected(self, leader_is_elected: bool):
        with self.lock:
            self.leader_is_elected = leader_is_elected
            print("\nLíder está eleito: ", leader_is_elected)

    
    def set_ip_leader(self, ip_leader: str):
        with self.lock:
            self.ip_leader = ip_leader
            print("\nIP do líder: ", ip_leader)


    def set_time_without_leader_request(self, time_without_leader_request: int):
        with self.lock:
            self.time_without_leader_request = time_without_leader_request
            print("\nTempo sem requisição do líder: ", self.time_without_leader_request)


    def set_problem_detected(self, problem_detected: bool):
        with self.lock:
            self.problem_detected = problem_detected
            print("\nProblema detectado: ", problem_detected)


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


    def reset_atributes_leadership(self):
        with self.lock:
            self.leader_is_elected = False
            self.ip_leader = None
            print("\nResetei coisas do líder\n")
    