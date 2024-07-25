""" 
Módulo contendo as funções relacionadas à implementação base do relógio.
"""

from impl.Election_impl import election
from utils.Utils import create_result_structure, send_request
import threading
import time


def ready_for_connection(clock: object):
    """
    Retorna se o relógio atual está pronto para conexão.

    :param clock: Dados do relógio.
    :type clock: object
    :return: Informação de conexão do relógio atual.
    :rtype: dict
    """

    response = {"Bem sucedido": clock.ready_for_connection}
    return response


def start_count(clock: object):
    """
    Contagem periódica do tempo. É contado a partir da diminuição de 
    uma contadora medida em relação ao drift atual. A cada 0.01 segundos, 
    essa contadora é reduzida e quando chega em 1, deve ser somado 1 segundo
    no tempo do relógio. Se estiver em estado de regulação de tempo, é 
    usada uma contadora base de regulação na contagem.

    :param clock: Dados do relógio.
    :type clock: object
    """

    count = clock.drift * 100
    actual_drift = clock.drift

    while True:

        if clock.regulating_time == False:

            if clock.drift != actual_drift:
                actual_drift = clock.drift
                count = clock.drift * 100
                clock.set_time(clock.time + 1)

            count -= 1
            if count <= 0:
                clock.set_time(clock.time + 1)
                count = clock.drift * 100

        else:

            if clock.regulate_base_count != 0:

                count -= 1
                if count <= 0:
                    clock.set_time(clock.time + 1)
                    count = clock.regulate_base_count

            else:
                count = clock.drift * 100
                clock.set_regulating_time(False)

        time.sleep(0.01)


def add_clocks(clock: object, list_clocks: list):
    """
    Adiciona os IPs dos relógios da lista no armazenamento e testa a 
    conexão com eles. Depois ordena a lista com os IPs e inicia o processo 
    de decisão do líder.

    :param clock: Dados do relógio.
    :type clock: object
    :param list_clocks: IPs dos relógios.
    :type list_clocks: list
    """
    
    quantity_clocks = len(list_clocks)
    result_dict = create_result_structure(quantity_clocks)

    for i in range(quantity_clocks):

        clock.add_clock(list_clocks[i])

        url = (f"http://{list_clocks[i]}:2500/ready_for_connection")

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

    election(clock)
