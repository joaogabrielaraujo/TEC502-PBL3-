import requests
import threading
import time
from utils.Utils import loop_recconection, create_result_structure, send_request
from impl.Berkeley_impl import syncronize_clocks


def election(clock: object):
    print("\nVoltei pro início\n")
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

                    threading.Thread(target=syncronize_clocks, args=(clock,)).start()
                        
        time.sleep(2)

    print("Saí do loop!")

#Função para encontrar o próximo relógio
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
                    threading.Thread(target=loop_recconection, args=(clock, clock.list_clocks[i],)).start()
        
    return None

# Função para encontrar o relógio de maior prioridade
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
                    threading.Thread(target=loop_recconection, args=(clock, clock.list_clocks[i],)).start()


def leader_is_elected(clock: object):

    response = {"Bem sucedido": clock.leader_is_elected, "IP líder": clock.ip_leader}
    return response


def claim_leadership(clock: object, data: dict):

    if clock.problem_detected == False:

        if clock.leader_is_elected == False:
            clock.set_leader_is_elected(True)
            clock.set_ip_leader(data["IP líder"])
        else:
            threading.Thread(target=problem_detected_leadership, args=(clock,)).start()    

    response = {"Bem sucedido": True}
    return response


#Fazer detecção de falha
def problem_detected_leadership(clock: object):
    print("\nDetectei um problema\n")
    loop = True
    while loop == True:
        first_clock = find_first_clock(clock) 

        #if first_clock == clock.ip_clock:
        if first_clock == clock.port:
            #threading.Thread(target=treat_problem_leadership, args=(clock, "",)).start() 
            threading.Thread(target=treat_problem_leadership, args=(clock, "",)).start() 
            loop = False

        else:
            try:
                #data = {"Lidar com o problema": True, "IP remetente": clock.ip_clock}
                data = {"Lidar com o problema": True, "IP remetente": clock.port}
                #url = (f"http://{first_clock}:2500/problem_alert_leadership")
                url = (f"http://{clock.ip_clock}:{first_clock}/problem_alert_leadership")

                status_code = requests.post(url, json=data, timeout=5).status_code

                if status_code == 200: 
                    threading.Thread(target=wait_blocking_time, args=(clock,)).start()    

                loop = False         

            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                clock.set_trying_recconection(first_clock, True)
                threading.Thread(target=loop_recconection, args=(clock, first_clock,)).start()


def receive_problem_alert(clock: object, data: dict):
    print("\nMe avisaram do problema\n")
    if data["Lidar com o problema"] == True:
        if clock.problem_detected == True:
            response = {"Bem sucedido": False}
            return response
        else: 
            threading.Thread(target=treat_problem_leadership, args=(clock, data["IP remetente"],)).start() 

    else:  
        threading.Thread(target=wait_blocking_time, args=(clock,)).start()  

    response = {"Bem sucedido": True}
    return response


def treat_problem_leadership(clock: object, ip_sender: str):
    print("\nTo tratando\n")
    clock.reset_atributes_leadership()
    clock.set_problem_detected(True)  

    clocks_on = clock.get_clocks_on()
    if ip_sender == "":
        quantity = len(clocks_on)
    else:
        if len(clocks_on) != 0:
            quantity = len(clocks_on) - 1
    
    result_dict = create_result_structure(quantity)

    index = 0
    for i in range(len(clocks_on)):
        if clocks_on[i] != ip_sender:

            #url = (f"http://{clocks_on[i]}:2500/problem_alert_leadership")
            url = (f"http://{clock.ip_clock}:{clocks_on[i]}/problem_alert_leadership")

            all_data_request = {"URL": url, 
                                "IP do relógio": clocks_on[i], 
                                "Dados": {"Lidar com o problema": False}, 
                                "Método HTTP": "POST", 
                                "Dicionário de resultados": result_dict, 
                                "Índice": index}
        
            threading.Thread(target=send_request, args=(clock, all_data_request,)).start()

            index += 1

    loop = True
    while loop:
        loop = False
        for key in result_dict.keys():
            if result_dict[key]["Terminado"] == False:
                loop = True

    wait_blocking_time(clock)


def wait_blocking_time(clock: object):
    print("\nTo aguardando....\n")
    clock.reset_atributes_leadership()
    clock.set_problem_detected(True) 
    time.sleep(5)
    clock.set_problem_detected(False)
    election(clock)


def periodic_leadership_check(clock: object):
    while True:

        #if clock.problem_detected == False and clock.ip_leader != clock.ip_clock  and clock.leader_is_elected == True:
        if clock.problem_detected == False and clock.ip_leader != clock.port and clock.leader_is_elected == True:
            clock.set_time_without_leader_request(clock.time_without_leader_request + 1)

            if clock.time_without_leader_request > 10:
                try:
                    #url = (f"http://{clock.ip_leader}:2500/leader_is_elected")
                    url = (f"http://{clock.ip_clock}:{clock.ip_leader}/leader_is_elected")

                    response = requests.get(url, timeout=5)
                    status_code = response.status_code
                    response = response.json()

                    if status_code == 200:
                        clock.set_time_without_leader_request(0)
                        #print("\nAinda ta ativo!!\n")
                    else:
                        raise requests.exceptions.ConnectionError

                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                    clock.set_trying_recconection(clock.ip_leader, True)
                    threading.Thread(target=loop_recconection, args=(clock, clock.ip_leader,)).start()
                    threading.Thread(target=problem_detected_leadership, args=(clock,)).start()   
                    clock.reset_atributes_leadership()
                    clock.set_problem_detected(True) 

        time.sleep(1)
