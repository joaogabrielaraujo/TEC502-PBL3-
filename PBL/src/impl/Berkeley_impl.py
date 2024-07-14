from model.Clock import Clock
from utils.Utils import loop_recconection, create_result_structure, send_request
import time
import threading


def colect_times(Clock: list[Clock]):
    list_times = []
    for i in range(len(Clock)):
        list_times.append(Clock[i].time)
    return list_times

def colect_drifts(Clock: list[Clock]):
    list_drifts = []
    for i in range(len(Clock)):
        list_drifts.append(Clock[i].drift)
    return list_drifts

def getAvarageClockTime(Clock: list[Clock]):
    list_times = colect_times(Clock)
    return sum(list_times)/len(list_times)


def seconds_to_hms(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    remaining_seconds = seconds % 60
    return hours, minutes, remaining_seconds

def hms_to_seconds(hours, minutes, seconds):
    return hours*3600 + minutes*60 + seconds
   
def syncronizeClocks(local_clock, average_time, sync_interval):
    #lógica que está voltando no tempo
    time_difference = average_time - local_clock.time

    required_drift = time_difference/sync_interval

    original_drift = local_clock.drift
    local_clock.drift = required_drift

    for _ in range(sync_interval):
        local_clock.time.update_time(local_clock.drift)
        time.sleep(1)
    local_clock.drift = original_drift  # Restaurando o valor original do drift


#######
def syncronize_clocks(clock: object):

    #while clock.ip_leader == clock.ip_clock:
    while clock.ip_leader == clock.port:

        dict_times = request_times(clock)
        print("Dicionário de tempos: ", dict_times)

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
    
    

#######