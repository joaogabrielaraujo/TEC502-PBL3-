from utils.Utils import create_result_structure, send_request
import threading


def ready_for_connection(clock: object):

    response = {"Bem sucedido": clock.ready_for_connection}
    return response


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
                
    print("Dicionário de resultados: ", result_dict)



    







