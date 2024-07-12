import threading
import requests


def create_result_structure(quantity: int):

    result_dict = {}
    for i in range(quantity):
        result_dict[i] = {"Terminado": False, "Resposta": None}
    
    return result_dict


def send_request(clock: object, url: str, ip_clock: str, data: dict, http_method: str, result_dict: dict, index: str):
    
    try:
        if http_method == "GET":
            response = requests.get(url, json=data)
        elif http_method == "POST":
            response = requests.post(url, json=data)
        elif http_method == "PATCH":
            response = requests.patch(url, json=data)

    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout) as e:
        

def loop_recconection():


    