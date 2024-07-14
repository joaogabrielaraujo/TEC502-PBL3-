from impl.Election_impl import election
from impl.Berkeley_impl import syncronize_clocks
from utils.Utils import create_result_structure, send_request
import threading
import time


def ready_for_connection(clock: object):

    response = {"Bem sucedido": clock.ready_for_connection}
    return response

def start_count(clock: object):
    counter = clock.drift * 100
    while True:
        time.sleep(0.01)
        counter -= 1
        if counter == 0:
            clock.time += 1
            counter = clock.drift * 100


def add_clocks(clock: object, list_clocks: list):
    
    quantity_clocks = len(list_clocks)
    result_dict = create_result_structure(quantity_clocks)

    for i in range(quantity_clocks):

        clock.add_clock(list_clocks[i])

        #url = (f"http://{ip_clock}:2500/ready_for_connection")
        url = (f"http://{clock.ip_clock}:{list_clocks[i]}/ready_for_connection")

        all_data_request = {"URL": url,
                            "IP do relógio": list_clocks[i],
                            "Dados": "",
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

    clock.sort_list_clocks()
    print("Lista ordenada: ", clock.list_clocks)
    print("Dicionário de resultados: ", result_dict)

    election(clock)
    #test_reinvidication(clock)
    #test_syncronize(clock)


#####################
def test_reinvidication(clock):
    clock.set_ready_for_connection(True)
    clocks_on = clock.get_clocks_on()
    result_dict = create_result_structure(len(clocks_on))
    #os comentários abaixo são para fazer a troca na hora de testar no larsid 
    for i in range(len(clocks_on)):

        #url = (f"http://{clocks_on[i]}:2500/claim_leadership")
        url = (f"http://{clock.ip_clock}:{clocks_on[i]}/claim_leadership")
        
        '''all_data_request = {"URL": url, "IP do relógio": clocks_on[i], "Dados": {"IP líder": clock.ip_clock}, "Método HTTP": "POST", "Dicionário de resultados": result_dict, "Índice": i}'''
        all_data_request = {"URL": url, 
                            "IP do relógio": clocks_on[i], 
                            "Dados": {"IP líder": clock.port}, 
                            "Método HTTP": "POST", 
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

    syncronize_clocks(clock)


def test_syncronize(clock):
    clock.set_ready_for_connection(True)
    clock.set_leader_is_elected(True)
    # clock.set_ip_leader(clock.ip_clock)
    clock.set_ip_leader(clock.port)
    syncronize_clocks(clock)

#######################





