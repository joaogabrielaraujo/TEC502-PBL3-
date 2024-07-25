""" 
Módulo contendo as funções relacionadas à implementação do algoritmo de Berkeley.
"""

from utils.Utils import create_result_structure, send_request
import time
import threading


def syncronize_clocks(clock: object):
    """
    Regulação periódica dos relógios se o relógio atual for o líder. 
    É pedido o tempo de cada relógio do sistema. É calculada média 
    entre o maior e o menor tempo. A diferença dos tempos de cada 
    relógio para a média é enviada.

    :param clock: Dados do relógio.
    :type clock: object
    """

    while clock.ip_leader == clock.ip_clock:

        dict_times = request_times(clock)

        count_clocks = len(dict_times)
        if count_clocks > 1:
            
            sum_times = 0
            list_clocks = []
            list_times = []
            for key in dict_times.keys():
                sum_times += dict_times[key]
                list_clocks.append(key)
                list_times.append(dict_times[key])

            media = int((max(list_times) + min(list_times)) / 2)         

            differences = []
            all_clocks_synchronized = True
            for i in range(count_clocks):
                difference = media - dict_times[list_clocks[i]]
                differences.append(difference)

                if difference != 0:
                    all_clocks_synchronized = False
            
            result_dict = create_result_structure(count_clocks)

            for i in range(count_clocks):
                
                data = {"Diferença": differences[i], "Tudo sincronizado": all_clocks_synchronized}

                if list_clocks[i] != clock.ip_clock:

                    url = (f"http://{list_clocks[i]}:2500/regulate_time")

                    all_data_request = {"URL": url, 
                                        "IP do relógio": list_clocks[i], 
                                        "Dados": data,
                                        "Método HTTP": "POST", 
                                        "Dicionário de resultados": result_dict, 
                                        "Índice": i}
                
                    threading.Thread(target=send_request, args=(clock, all_data_request,)).start()

                else:
                    threading.Thread(target=regulate_time, args=(clock, data,)).start()
                    result_dict[i]["Terminado"] = True

            loop = True
            while loop:
                loop = False
                for key in result_dict.keys():
                    if result_dict[key]["Terminado"] == False:
                        loop = True

            time.sleep(5)
        
        else:

            from impl.Election_impl import election
            clock.reset_atributes_leadership()
            threading.Thread(target=election, args=(clock,)).start()


def request_times(clock: object):
    """
    Função de envio de requisição dos tempos dos relógios do sistema. 
    Os tempos são armazenados e retornados.

    :param clock: Dados do relógio.
    :type clock: object
    :return: Tempos dos relógios que responderam a requisição.
    :rtype: dict
    """
    
    dict_times = {}
    clocks_on = clock.get_clocks_on()
    quantity = len(clocks_on)
    result_dict = create_result_structure(quantity)

    for i in range(quantity):
        
        url = (f"http://{clocks_on[i]}:2500/request_time")

        all_data_request = {"URL": url, 
                            "IP do relógio": clocks_on[i], 
                            "Dados": {"IP líder": clock.ip_clock}, 
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

    dict_times[clock.ip_clock] = clock.time

    for ip_clock in clocks_on:
        index = clocks_on.index(ip_clock)

        if type(result_dict[index]["Resposta"]) != dict:
            result_dict[index]["Resposta"] = result_dict[index]["Resposta"].json()

        if result_dict[index]["Resposta"]["Bem sucedido"] == True:
            dict_times[ip_clock] = result_dict[index]["Resposta"]["Tempo"]

    return dict_times
        

def request_time(clock: object, data: dict):
    """
    Recebimento de uma requisição de tempo. Se não tiver um líder eleito, 
    o relógio que enviou a requisição é setado como líder. O tempo atual é 
    retornado para ele.

    :param clock: Dados do relógio.
    :type clock: object
    :param data: Dados da requisição.
    :type data: dict
    :return: Resposta da requisição.
    :rtype: dict
    """

    if clock.problem_detected == False:

        clock.set_time_without_leader_request(0)

        if clock.ip_leader == None:
            clock.set_leader_is_elected(True)
            clock.set_ip_leader(data["IP líder"])

            response = {"Bem sucedido": True, "Tempo": clock.time}
            return response

        elif data["IP líder"] == clock.ip_leader:
            response = {"Bem sucedido": True, "Tempo": clock.time}
            return response
        
        else: 
            from impl.Election_impl import problem_detected_leadership
            threading.Thread(target=problem_detected_leadership, args=(clock,)).start()
            response = {"Bem sucedido": False}
            return response
        
    else:
        response = {"Bem sucedido": False}
        return response


def receive_regulate_time(clock: object, data: dict):
    """
    Recebimento de uma requisição de regulação de tempo.

    :param clock: Dados do relógio.
    :type clock: object
    :param data: Dados da requisição.
    :type data: dict
    :return: Resposta da requisição.
    :rtype: dict
    """

    threading.Thread(target=regulate_time, args=(clock, data,)).start()

    response = {"Bem sucedido": True}
    return response


def regulate_time(clock: object, data: dict):
    """
    Função de regulação de tempo. É checado se o tempo atual está antes ou 
    depois da média. Se estiver antes da média, o relógio é acelerado 
    proporcionalmente para chegar mais próximo dela. Se estiver depois da 
    média, ele é desacelerado para que os outros relógios possam alcançá-lo. 
    É setado o atributo que indica que deve ser feita a refulação. O tempo 
    de regulação é de 5 segundos. 

    :param clock: Dados do relógio.
    :type clock: object
    :param data: Dados da regulação.
    :type data: dict
    """

    if data["Diferença"] > 0:

        if data["Diferença"] >= 5:
            clock.set_regulate_base_count(500 / data["Diferença"])

        else:
            clock.set_regulate_base_count(100 - (data["Diferença"] * 10))

            if data["Diferença"] <= 2:
                clock.set_time(clock.time + 1)

        clock.set_regulating_time(True)

    elif data["Diferença"] < 0:

        if data["Diferença"] <= -5:
            clock.set_regulate_base_count(450)

        else:
            clock.set_regulate_base_count(((-1) * (data["Diferença"] * 10)) + 100)

        clock.set_regulating_time(True)
    
    elif data["Tudo sincronizado"] == False:
        clock.set_regulate_base_count(100)

        clock.set_regulating_time(True)

    elif data["Tudo sincronizado"] == True:

        clock.set_regulate_base_count(0)
        clock.set_regulating_time(True)

    time.sleep(5)
    clock.set_regulating_time(False)
