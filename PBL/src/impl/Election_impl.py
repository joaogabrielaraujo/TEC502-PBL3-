import requests
import threading
import time
from utils.Utils import loop_recconection, create_result_structure, send_request
from impl.Berkeley_impl import syncronize_clocks


def election(clock: object):
    # Setando o clock atual como pronto para conexão
    clock.set_ready_for_connection(True)

    while clock.leader_is_elected == False:

        while len(clock.get_clocks_on()) == 0:
            pass

        first_clock = find_first_clock(clock)
        print("Relógio de maior prioridade: ", first_clock)

        #if first_clock == clock.ip_clock:
        if first_clock == clock.port:

            next_clock = find_next_clock(clock)
            print("Próximo relógio: ", next_clock)

            if next_clock != None:

                #url = (f"http://{next_clock}:2500/leader_is_elected")
                url = (f"http://{clock.ip_clock}:{next_clock}/leader_is_elected")

                response = requests.get(url, timeout=5)
                status_code = response.status_code
                response = response.json()

                if status_code == 200:
                    clock.set_leader_is_elected(True)
                    clock.set_ip_leader(response["IP líder"])

                else:
                    clocks_on = clock.get_clocks_on()
                    result_dict = create_result_structure(len(clocks_on))
                    
                    for i in range(len(clocks_on)):

                        #url = (f"http://{clocks_on[i]}:2500/claim_leadership")
                        url = (f"http://{clock.ip_clock}:{clocks_on[i]}/claim_leadership")

                        '''all_data_request = {"URL": url, "IP do relógio": clocks_on[i], "Dados": {"IP líder": clock.ip_clock}, "Método HTTP": "GET", "Dicionário de resultados": result_dict, "Índice": i}'''
                        all_data_request = {"URL": url, 
                                            "IP do relógio": clocks_on[i], 
                                            "Dados": {"IP líder": clock.port}, 
                                            "Método HTTP": "GET", 
                                            "Dicionário de resultados": result_dict, 
                                            "Índice": i}
                    
                        threading.Thread(target=send_request, args=(clock, all_data_request,)).start()

                    loop = True
                    while loop:
                        loop = False
                        for key in result_dict.keys():
                            if result_dict[key]["Terminado"] == False:
                                loop = True
                    
                    clock.set_leader_is_elected(True)
                    # clock.set_ip_leader(clock.ip_clock)
                    clock.set_ip_leader(clock.port)

                    threading.Thread(target=syncronize_clocks, args=(clock,)).start()
                        
        time.sleep(2)

    print("Saí do loop!")


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
                    threading.Thread(target=loop_recconection, args=(clock.list_clocks[i],)).start()
        
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
                    threading.Thread(target=loop_recconection, args=(clock.list_clocks[i],)).start()


def leader_is_elected(clock: object):

    response = {"Bem sucedido": clock.leader_is_elected, "IP líder": clock.ip_leader}
    return response


def claim_leadership(clock: object, data: dict):

    if clock.leader_is_elected == False:
        clock.set_leader_is_elected(True)
        clock.set_ip_leader(data["IP líder"])
    else:
        # FAZER O CASO DO LÍDER JÁ ESTAR ELEITO
        pass

    response = {"Bem sucedido": True}
    return response


#Fazer detecção de falha
def problem_detected_leadership(clock: object):
    first_clock = find_first_clock(clock) 

