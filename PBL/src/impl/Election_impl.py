""" 
Módulo contendo as funções relacionadas à implementação do sistema do líder.
"""

import requests
import threading
import time
from utils.Utils import loop_recconection, create_result_structure, send_request
from impl.Berkeley_impl import syncronize_clocks


def election(clock: object):
    """
    Estado inicial do relógio, em que se espera o líder ser eleito. 
    É setado que o relógio atual está pronto para conexão. É iniciado 
    um loop que se repete até que o líder seja eleito. Caso tenha mais 
    algum relógio online além do atual, é buscado o relógio que tem 
    maior prioridade para ser líder (menor IP). Se o de maior prioridade 
    for o relógio atual, ele pergunta ao próximo relógio do sistema se 
    já tem um líder eleito, se já tiver, ele seta seus dados, se não, 
    o relógio atual reivindica sua liderança avisando aos outros relógios 
    e inicia a função de sincronização do sistema. Se o relógio atual 
    não for o de maior prioridade na sua checagem, o loop continua.

    :param clock: Dados do relógio.
    :type clock: object
    """

    clock.set_ready_for_connection(True)

    while clock.leader_is_elected == False:

        while len(clock.get_clocks_on()) == 0:
            pass

        first_clock = find_first_clock(clock)

        if first_clock == clock.ip_clock:

            next_clock = find_next_clock(clock)

            if next_clock != None:

                url = (f"http://{next_clock}:2500/leader_is_elected")

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

                        url = (f"http://{clocks_on[i]}:2500/claim_leadership")
                        
                        all_data_request = {"URL": url, 
                                            "IP do relógio": clocks_on[i], 
                                            "Dados": {"IP líder": clock.ip_clock}, 
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
                    clock.set_ip_leader(clock.ip_clock)

                    threading.Thread(target=syncronize_clocks, args=(clock,)).start()
                        
        time.sleep(2)


def find_next_clock(clock: object):
    """
    Busca pelo relógio no sistema que tem IP maior que o atual. É 
    testada a conexão com cada relógio e vai ser retornado o IP do 
    próximo relógio no sistema que for possível fazer conexão.

    :param clock: Dados do relógio.
    :type clock: object
    :return: IP do próximo relógio.
    :rtype: str
    """

    for i in range(len(clock.list_clocks)):

        if clock.list_clocks[i] != clock.ip_clock:
        
            if clock.trying_recconection[clock.list_clocks[i]] == False:

                try:
                    url = (f"http://{clock.list_clocks[i]}:2500/ready_for_connection")

                    status_code = requests.get(url, timeout=5).status_code

                    if status_code == 200:
                        return clock.list_clocks[i]

                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                    clock.set_trying_recconection(clock.list_clocks[i], True)
                    threading.Thread(target=loop_recconection, args=(clock, clock.list_clocks[i],)).start()
        
    return None


def find_first_clock(clock: object):
    """
    Busca pelo relógio de maior prioridade no sistema (menor IP). 
    É testada a conexão com os relógios em ordem e o de menor IP que 
    tiver conexão será retornado, podendo ser o próprio relógio atual.

    :param clock: Dados do relógio.
    :type clock: object
    :return: IP do relógio de maior prioridade.
    :rtype: str
    """

    for i in range(len(clock.list_clocks)):

        if clock.list_clocks[i] == clock.ip_clock:
            return clock.ip_clock
        
        else:

            if clock.trying_recconection[clock.list_clocks[i]] == False:

                try:
                    url = (f"http://{clock.list_clocks[i]}:2500/ready_for_connection")

                    status_code = requests.get(url, timeout=5).status_code

                    if status_code == 200:
                        return clock.list_clocks[i]

                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                    clock.set_trying_recconection(clock.list_clocks[i], True)
                    threading.Thread(target=loop_recconection, args=(clock, clock.list_clocks[i],)).start()


def leader_is_elected(clock: object):
    """
    Retorna informação se o líder está eleito e o seu IP. 

    :param clock: Dados do relógio.
    :type clock: object
    :return: Indicação se o líder está eleito e o seu IP.
    :rtype: dict
    """

    response = {"Bem sucedido": clock.leader_is_elected, "IP líder": clock.ip_leader}
    return response


def claim_leadership(clock: object, data: dict):
    """
    Recebimento de uma reivindicação de liderança. É checado se já tem 
    um líder eleito, se tiver, é chamada a função de detecção de problema 
    na liderança.

    :param clock: Dados do relógio.
    :type clock: object
    :param data: Dados da reivindicação.
    :type data: dict
    :return: Resposta relacionada a requisição.
    :rtype: dict
    """

    if clock.problem_detected == False:

        if clock.leader_is_elected == False:
            clock.set_leader_is_elected(True)
            clock.set_ip_leader(data["IP líder"])
        else:
            threading.Thread(target=problem_detected_leadership, args=(clock,)).start()    

    response = {"Bem sucedido": True}
    return response


def problem_detected_leadership(clock: object):
    """
    É enviado para o relógio de maior prioridade um alerta que um 
    problema foi detectado no sistema de liderança para ele realizar 
    o tratamento. Se o relógio atual for o de maior prioridade, ele 
    realiza o tratamento.

    :param clock: Dados do relógio.
    :type clock: object
    """

    loop = True
    while loop == True:
        first_clock = find_first_clock(clock) 

        if first_clock == clock.ip_clock:
            threading.Thread(target=treat_problem_leadership, args=(clock, "",)).start() 
            loop = False

        else:
            try:
                data = {"Lidar com o problema": True, "IP remetente": clock.ip_clock}
                url = (f"http://{first_clock}:2500/problem_alert_leadership")

                status_code = requests.post(url, json=data, timeout=5).status_code

                if status_code == 200: 
                    threading.Thread(target=wait_blocking_time, args=(clock,)).start()    

                loop = False         

            except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                clock.set_trying_recconection(first_clock, True)
                threading.Thread(target=loop_recconection, args=(clock, first_clock,)).start()


def receive_problem_alert(clock: object, data: dict):
    """
    Recebimento de alerta de problema detectado no sistema de liderança.
    É verificado se o relógio atual deve tratar o problema, se for, ele 
    chama a função de tratamento, se não, inicia um estado de bloqueio 
    temporário para reiniciar o sistema de liderança.

    :param clock: Dados do relógio.
    :type clock: object
    :param data: Dados do alerta.
    :type data: dict
    :return: Resposta do recebimento do alerta.
    :rtype: dict
    """

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
    """
    Tratamento de problemas no sistema de liderança. São setados os dados 
    relacionados a detecção de um problema. É enviado para cada relógio do 
    sistema um alerta que ocorreu um problema. Depois, o relógio atual entra 
    em estado de bloqueio temporário para, posteriormente, voltar ao estado 
    inicial de decisão do líder.

    :param clock: Dados do relógio.
    :type clock: object
    :param ip_sender: IP do relógio que enviou o alerta.
    :type ip_sender: str
    """

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

            url = (f"http://{clocks_on[i]}:2500/problem_alert_leadership")

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
    """
    São resetados os atributos relacionados a liderança e é indicado 
    que ocorreu um problema no sistema. É contado um intervalo de 5 
    segundos e o relógio volta ao estado inicial de decisão da liderança.

    :param clock: Dados do relógio.
    :type clock: object
    """

    clock.reset_atributes_leadership()
    clock.set_problem_detected(True) 
    time.sleep(5)
    clock.set_problem_detected(False)
    election(clock)


def periodic_leadership_check(clock: object):
    """
    Checagem periódica de conexão com o líder. É verificada uma contadora 
    que indica a quantidade de tempo que o relógio atual ficou sem receber 
    requisições do líder. Caso o tempo limite seja ultrapassado, é enviada 
    uma mensagem ao líder perguntando se ele ainda é o líder, caso seja, a 
    contadora é reiniciada. Se ele não for o líder ou não puder ser feita a
    conexão, é iniciada a função de detecção de problemas no sistema do líder.

    :param clock: Dados do relógio.
    :type clock: object
    """

    while True:

        if clock.problem_detected == False and clock.ip_leader != clock.ip_clock  and clock.leader_is_elected == True:

            clock.set_time_without_leader_request(clock.time_without_leader_request + 1)

            if clock.time_without_leader_request > 10:
                try:
                    url = (f"http://{clock.ip_leader}:2500/leader_is_elected")

                    response = requests.get(url, timeout=5)
                    status_code = response.status_code
                    response = response.json()

                    if status_code == 200:
                        clock.set_time_without_leader_request(0)
  
                    else:
                        raise requests.exceptions.ConnectionError

                except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
                    clock.set_trying_recconection(clock.ip_leader, True)
                    threading.Thread(target=loop_recconection, args=(clock, clock.ip_leader,)).start()
                    threading.Thread(target=problem_detected_leadership, args=(clock,)).start()   
                    clock.reset_atributes_leadership()
                    clock.set_problem_detected(True) 

        time.sleep(1)
