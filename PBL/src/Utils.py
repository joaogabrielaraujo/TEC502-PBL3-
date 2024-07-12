import threading
import requests
import time


#Cria uma estrutura de dados para armazenar os resultados das requisições
def create_result_structure(quantity: int):

    result_dict = {}
    for i in range(quantity):
        result_dict[i] = {"Terminado": False, "Resposta": None}
    
    return result_dict


def send_request(clock: object, data_request: dict):
    
    try:
        if data_request["Método HTTP"] == "GET":
            response = requests.get(data_request["URL"], json=data_request["Dados"], timeout=5)
        elif data_request["Método HTTP"] == "POST":
            response = requests.post(data_request["URL"], json=data_request["Dados"], timeout=5)
        elif data_request["Método HTTP"] == "PATCH":
            response = requests.patch(data_request["URL"], json=data_request["Dados"], timeout=5)

    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        if clock.trying_recconection[data_request["IP do relógio"]] == False:
            clock.set_trying_recconection(data_request["IP do relógio"], True)
        threading.Thread(target=loop_recconection, args=(clock, data_request["IP do relógio"],)).start()
        response = {"Bem sucedido": False, "Justificativa": "Banco desconectado"}

    data_request["Dicionário de resultados"][data_request["Índice"]]["Resposta"] = response
    #Relógio terminou de responder e foi adicionado com sucesso 
    data_request["Dicionário de resultados"][data_request["Índice"]]["Terminado"] = True


#Função para tentar reconectar os relógios de tempos em tempos
def loop_recconection(clock: object, ip_clock: str):

    loop = True
    while loop:
        try:
            #descomentar a linha de baixo e comentar a linha de cima para rodar no docker
            #url = (f"http://{ip_clock}:2500/ready_for_connection")
            url = (f"http://{clock.ip_clock}:{ip_clock}/ready_for_connection")
            status_code = requests.get(url, timeout=5).status_code

            if status_code == 200:
                loop = False
                with clock.lock:
                    clock.trying_recconection[ip_clock] = False
            else:
                raise requests.exceptions.ConnectionError
        
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
            time.sleep(1)
    
    print("Reconectou: ", ip_clock)


    
    