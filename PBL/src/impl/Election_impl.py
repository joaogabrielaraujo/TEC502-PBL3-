import requests
from utils.Utils import loop_recconection


def election(clock: object):

    clock.set_ready_for_connection(True)

    while clock.leader_is_elected == False:

        while clock.get_quantity_clocks_on() == 0:
            pass

        next_clock = find_next_clock()

        if next_clock != None:

            #url = (f"http://{next_clock}:2500/leader_is_elected")
            url = (f"http://{clock.ip_clock}:{next_clock}/leader_is_elected")

            status_code = requests.get(url, timeout=5).status_code

            if status_code == 200:
                


            '''
            first_clock = find_first_clock(clock)

            #if first_clock == clock.ip_clock:
            if first_clock == clock.port:
                pass
            '''


def find_next_clock(clock: object):

    for i in range(len(clock.list_clocks)):

        #if clock.list_clocks[i] != clock.ip_clock:
        if clock.list_clocks[i] != clock.port:
        
            if clock.trying_recconection[clock.list_clocks[i]] == False:

                try:
                    #url = (f"http://{clock.list_clocks[i]}:2500/ready_for_connection")
                    url = (f"http://{clock.ip_clock}:{clock.list_clocks[i]}/ready_for_connection")

                    status_code = requests.get(url, timeout=5).status_code

                    if status_code == 200:
                        return clock.list_clocks[i]

                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                    clock.set_trying_recconection(clock.list_clocks[i], True)
                    threading.Thread(target=loop_reconnection, args=(clock.list_clocks[i],)).start()
        
    return None


def find_first_clock(clock: object):

    for i in range(len(clock.list_clocks)):

        #if clock.list_clocks[i] == clock.ip_clock:
        if clock.list_clocks[i] == clock.port:
            #return clock.ip_clock
            return clock.port 
        
        else:

            if clock.trying_recconection[clock.list_clocks[i]] == False:

                try:
                    #url = (f"http://{clock.list_clocks[i]}:2500/ready_for_connection")
                    url = (f"http://{clock.ip_clock}:{clock.list_clocks[i]}/ready_for_connection")

                    status_code = requests.get(url, timeout=5).status_code

                    if status_code == 200:
                        return clock.list_clocks[i]

                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                    clock.set_trying_recconection(clock.list_clocks[i], True)
                    threading.Thread(target=loop_reconnection, args=(clock.list_clocks[i],)).start()


def leader_is_elected(clock: object):

    response = {"Bem sucedido": clock.leader_is_elected, "IP líder": ip_leader}
    return response
