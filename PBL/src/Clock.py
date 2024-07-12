class Clock:

    def __init__(self):
        list_clocks = []
        time = 0
        drift = 0

        ready_for_connection = False

    def add_clock(self, ip_clock: str):
        self.list_clocks.append(ip_clock)
    
    