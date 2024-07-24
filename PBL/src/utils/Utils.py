""" 
Módulo contendo as funções úteis para a implementação do sistema, entre elas, funções 
relacionadas ao envio de múltiplas requisições por threads, e a função de checagem de 
reconexão.
"""

import threading
import requests


def create_result_structure(quantity: int):
    """
    Cria estrutura relacionada ao envio de múltiplas requisições utilizando threads.

    :param quantity: Quantidade de requisições que serão feitas.
    :type quantity: int
    :return: Estrutura que vai conter os dados das requisições após seu envio.
    :rtype: dict
    """

    result_dict = {}
    for i in range(quantity):
        result_dict[i] = {"Terminado": False, "Resposta": None}
    
    return result_dict


def send_request(clock: object, data_request: dict):
    """
    Envio de uma requisição. É adaptada para o método HTTP de envio. Após o envio são 
    armazenados os dados de resposta da requisição e a indicação que ela foi finalizada 
    na estrutura de controle. Se a requisição não puder ser enviada, é iniciado o loop 
    de reconexão com o relógio (função: loop_recconection).

    :param clock: Dados do relógio.
    :type clock: object
    :param data_request: Dados da requisição.
    :type data_request: dict
    """

    try:
        if data_request["Método HTTP"] == "GET":
            response = requests.get(data_request["URL"], json=data_request["Dados"], timeout=5)
        elif data_request["Método HTTP"] == "POST":
            response = requests.post(data_request["URL"], json=data_request["Dados"], timeout=5)
        elif data_request["Método HTTP"] == "PATCH":
            response = requests.patch(data_request["URL"], json=data_request["Dados"], timeout=5)

        if data_request["URL"] == (f"http://{data_request['IP do relógio']}:2500/ready_for_connection") and response.status_code != 200:
        #if data_request["URL"] == (f"http://{clock.ip_clock}:{data_request['IP do relógio']}/ready_for_connection") and response.status_code != 200:
            raise requests.exceptions.ConnectionError    

    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        if clock.trying_recconection[data_request["IP do relógio"]] == False:
            clock.set_trying_recconection(data_request["IP do relógio"], True)
        threading.Thread(target=loop_recconection, args=(clock, data_request["IP do relógio"],)).start()
        response = {"Bem sucedido": False, "Justificativa": "Banco desconectado"}

    data_request["Dicionário de resultados"][data_request["Índice"]]["Resposta"] = response
    data_request["Dicionário de resultados"][data_request["Índice"]]["Terminado"] = True


def loop_recconection(clock: object, ip_clock: str):
    """
    Envio periódico de mensagem para testar conexão com um relógio. Esse loop é
    encerrado quando a conexão com o relógio é confirmada.

    :param clock: Dados do relógio.
    :type clock: object
    :param ip_clock: IP do relógio que deve ser reconectado.
    :type ip_clock: str
    """

    loop = True
    while loop:
        try:
            url = (f"http://{ip_clock}:2500/ready_for_connection")
            #url = (f"http://{clock.ip_clock}:{ip_clock}/ready_for_connection")
            status_code = requests.get(url, timeout=5).status_code

            if status_code == 200:
                loop = False
                clock.set_trying_recconection(ip_clock, False)
                
            else:
                raise requests.exceptions.ConnectionError
        
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
            pass
    
    