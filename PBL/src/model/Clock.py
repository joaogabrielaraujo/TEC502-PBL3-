"""
Módulo contendo a classe de dados do relógio.
"""

import socket
import threading


class Clock:
    """ Classe de representação do relógio."""

    ip_clock: str
    list_clocks: list
    trying_recconection: dict
    time: int
    drift: float

    leader_is_elected: bool
    ip_leader: str
    time_without_leader_request: int
    problem_detected: bool

    regulating_time: bool
    regulate_base_count: int

    ready_for_connection: bool
    lock: object

    def __init__(self):
        """
        Inicialização dos atributos base de representação dos dados do relógio. 
        Incluindo os seguintes atributos:

            - ip_clock: IP do relógio;
            - list_clocks: Lista dos relógio do sistema;
            - trying_recconection: Indica quais relógios estão desconectados;
            - time: Tempo atual do relógio;
            - drift: Drift atual do relógio;
            - leader_is_elected: Indica se o líder está eleito;
            - ip_leader: IP do líder;
            - time_without_leader_request: Tempo sem requisição do líder;
            - problem_detected: Indica se um problema foi detectado na liderança;
            - regulating_time: Indica se está sendo feita uma regulação de tempo;
            - regulate_base_count: Base da contagem na regulação de tempo;
            - ready_for_connection: Indica se o relógio está pronto para conexão;
            - lock: Usado para evitar conflito na mudança de dados;
        """

        self.ip_clock = socket.gethostbyname(socket.gethostname())
        self.list_clocks = [self.ip_clock]
        self.trying_recconection = {}
        self.time = 1
        self.drift = 1.4

        self.leader_is_elected = False
        self.ip_leader = None
        self.time_without_leader_request = 0
        self.problem_detected = False

        self.regulating_time = False
        self.regulate_base_count = 1

        self.ready_for_connection = False
        self.lock = threading.Lock()


    def add_clock(self, ip_clock: str):
        """
        Adiciona um relógio no armazenamento.

        :param ip_clock: IP do relógio que deve ser adicionado.
        :type ip_clock: str
        """

        with self.lock:
            self.list_clocks.append(ip_clock)
            self.trying_recconection[ip_clock] = False
    

    def set_trying_recconection(self, ip_clock: str, boolean: bool):
        """
        Modifica a estrutura que indica se o relógio está conectado ou não.

        :param ip_clock: IP do relógio relacionado.
        :type ip_clock: str
        :param boolean: Indicação relacionada a conexão.
        :type boolean: str
        """

        with self.lock:
            self.trying_recconection[ip_clock] = boolean


    def set_time(self, time: int):
        """
        Setagem do tempo.

        :param time: Tempo do relógio.
        :type time: int
        """

        if time >= 86400:
            time = 0

        with self.lock:
            self.time = time
        
        print("\nTempo atual: ", self.time)

    def set_drift(self, drift: float):
        """
        Setagem do drift.

        :param drift: Drift do relógio.
        :type drift: float
        """

        with self.lock:
            self.drift = drift
            print("\nDrift atual: ", self.drift)

    
    def set_regulating_time(self, regulating_time: int):
        """
        Setagem da indicação se o tempo está sendo regulado.

        :param regulating_time: Indicação de regulagem do tempo.
        :type regulating_time: int
        """

        with self.lock:
            self.regulating_time = regulating_time


    def set_regulate_base_count(self, regulate_base_count: int):
        """
        Setagem da contadora base de regulação do tempo.

        :param regulate_base_count: Valor da contadora de regulação do tempo.
        :type regulate_base_count: int
        """

        with self.lock:
            self.regulate_base_count = regulate_base_count

    
    def set_ready_for_connection(self, ready_for_connection: bool):
        """
        Setagem da indicação se o relógio está pronto para conexão.

        :param ready_for_connection: Indicação de pronto para conexão.
        :type ready_for_connection: bool
        """

        with self.lock:
            self.ready_for_connection = ready_for_connection
            #print("\nPronto para conexão: ", ready_for_connection)

    
    def set_leader_is_elected(self, leader_is_elected: bool):
        """
        Setagem da indicação se o líder está eleito.

        :param leader_is_elected: Indicação de pronto para conexão.
        :type leader_is_elected: bool
        """

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


    def set_problem_detected(self, problem_detected: bool):
        with self.lock:
            self.problem_detected = problem_detected
            #print("\nProblema detectado: ", problem_detected)


    def get_clocks_on(self):
        list_clocks = []
        for key in self.trying_recconection.keys():
            if key != self.ip_clock and self.trying_recconection[key] == False:
            #if key != self.port and self.trying_recconection[key] == False:
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
            #print("\nResetei coisas do líder\n")


    def set_time_interface(self, time: str):
        try:
            h, m, s = map(int, time.split(':'))
            new_time_seconds = h * 3600 + m * 60 + s
            self.time = new_time_seconds - self.drift
            return True
        except ValueError:
            return False
        
        
    def set_drift_interface(self, drift:str):
        try:
            self.drift = float(drift)
            return True
        except ValueError:
            return False
        

    def get_current_time(self):
        adjusted_time = self.time + self.drift
        hours, remainder = divmod(adjusted_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours) % 24:02}:{int(minutes) % 60:02}:{int(seconds) % 60:02}"
    
    