from utils.Utils import create_result_structure, send_request
import time
import threading


def syncronize_clocks(clock: object):

    #while clock.ip_leader == clock.ip_clock:
    while clock.ip_leader == clock.port:

        #input("BLOQUEIO: ")

        dict_times = request_times(clock)
        #print("Dicionário de tempos: ", dict_times)

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
            print("\nMEDIA: ", media, "\n")        

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

                if list_clocks[i] != clock.port:

                    #url = (f"http://{list_clocks[i]}:2500/regulate_time")
                    url = (f"http://{clock.ip_clock}:{list_clocks[i]}/regulate_time")

                    '''all_data_request = {"URL": url, "IP do relógio": list_clocks[i], "Dados": {"Média": media}, "Método HTTP": "POST", "Dicionário de resultados": result_dict, "Índice": i}'''
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


def request_times(clock: object):
    
    dict_times = {}
    clocks_on = clock.get_clocks_on()
    quantity = len(clocks_on)
    result_dict = create_result_structure(quantity)

    for i in range(quantity):
        
        #url = (f"http://{clocks_on[i]}:2500/request_time")
        url = (f"http://{clock.ip_clock}:{clocks_on[i]}/request_time")

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

    # dict_times[clock.ip_clock] = clock.time
    dict_times[clock.port] = clock.time

    for ip_clock in clocks_on:
        index = clocks_on.index(ip_clock)
        #print("\nO erro vai ta aqui: ", result_dict[index], "\n")

        if type(result_dict[index]["Resposta"]) != dict:
            result_dict[index]["Resposta"] = result_dict[index]["Resposta"].json()

        if result_dict[index]["Resposta"]["Bem sucedido"] == True:
            dict_times[ip_clock] = result_dict[index]["Resposta"]["Tempo"]

    return dict_times
        

def request_time(clock: object, data: dict):

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

    threading.Thread(target=regulate_time, args=(clock, data,)).start()

    response = {"Bem sucedido": True}
    return response


def regulate_time(clock: object, data: dict):
    print("\nRegulando...\n")
    print("Diferença recebida: ", data["Diferença"])

    print("Drift: ", clock.drift)

    if data["Diferença"] > 0:

        if data["Diferença"] >= 5:

            #new_drift = (2.5 / data["Diferença"])
            clock.set_regulate_base_count(250 / data["Diferença"])

        else:

            clock.set_regulate_base_count(100 - (data["Diferença"] * 10))

            if data["Diferença"] <= 2:
                clock.set_time(clock.time + 1)

        clock.set_regulating_time(True)

    elif data["Diferença"] < 0:

        if data["Diferença"] <= -5:
            print("\nDIFERENÇA GRANDE\n")
            clock.set_regulate_base_count(450)

        else:
            print("\nDIFERENÇA PEQUENA\n")
            clock.set_regulate_base_count(((-1) * (data["Diferença"] * 10)) + 100)
            print("\nBase regulada: ", clock.regulate_base_count, "\n")

        clock.set_regulating_time(True)
    
    elif data["Tudo sincronizado"] == False:

        print("\nDIFERENÇA CENTRAL\n")
        clock.set_regulate_base_count(100)
        print("\nBase regulada: ", clock.regulate_base_count, "\n")

        clock.set_regulating_time(True)


    time.sleep(5)
    
    clock.set_regulating_time(False)
