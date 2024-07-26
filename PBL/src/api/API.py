import threading
from flask import Flask, jsonify, request, render_template
import re
from model.Clock import Clock
import impl.Clock_impl as Clock_impl
import impl.Election_impl as Election_impl
import impl.Berkeley_impl as Berkeley_impl


app = Flask(__name__, template_folder='templates')
clock = Clock()


@app.route('/ready_for_connection', methods=['GET'])
def ready_for_connection():
    """
    Adiciona os IPs dos relógios da lista no armazenamento e testa a 
    conexão com eles. Depois ordena a lista com os IPs e inicia o processo 
    de decisão do líder.

    :param clock: Dados do relógio.
    :type clock: object
    :param list_clocks: IPs dos relógios.
    :type list_clocks: list
    """
    response = Clock_impl.ready_for_connection(clock)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404


@app.route('/leader_is_elected', methods=['GET'])
def leader_is_elected():
    """
    Verifica se o líder foi eleito.

    :param clock: Dados do relógio.
    :type clock: object
    """
    response = Election_impl.leader_is_elected(clock)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404


@app.route('/claim_leadership', methods=['POST'])
def claim_leadership():
    """
    Elege o líder entre os relógios.

    :param clock: Dados do relógio.
    :type clock: object
    :param data: Dados para eleição do líder.
    :type data: dict
    """
    data = request.json
    response = Election_impl.claim_leadership(clock, data)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404


@app.route('/request_time', methods=['GET'])
def request_time():
    """
    Requisita o tempo do relógio.

    :param clock: Dados do relógio.
    :type clock: object
    :param data: Dados para requisição do tempo.
    :type data: dict
    """
    data = request.json
    response = Berkeley_impl.request_time(clock, data)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404


@app.route('/problem_alert_leadership', methods=['POST'])
def problem_alert_leadership():
    """
    Verifica se houve algum problema com o líder.

    :param clock: Dados do relógio.
    :type clock: object
    :param data: Dados do problema.
    :type data: dict
    """
    data = request.json
    response = Election_impl.receive_problem_alert(clock, data)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404


@app.route('/regulate_time', methods=['POST'])
def regulate_time():
    """
    Regula o tempo dos relógios com base nos relógios conectados, que foram recebeidos.

    :param clock: Dados do relógio.
    :type clock: object
    :param data: Dados para regulação do tempo.
    :type data: dict
    """
    data = request.json
    response = Berkeley_impl.receive_regulate_time(clock, data)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404


@app.route('/change_time', methods=['PATCH'])
def change_time():
    """
    Muda o tempo do relógio para o tempo especificado.

    :param clock: Dados do relógio.
    :type clock: object
    :param data: Dados para mudança do tempo.
    :type data: dict
    """
    data = request.json
    response = Clock_impl.change_time(clock, data)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404

@app.route('/')
def home_page():
    """
    Renderiza a página inicial.
    """
    return render_template('index.html')

@app.route('/get_clock', methods=['GET'])
def get_clock():
    """
    Obtém o horário atual, o líder e o IP do relógio.

    :param clock: Dados do relógio.
    :type clock: object
    """
    try:
        current_time = clock.get_current_time()
        leader= clock.ip_leader
        ip = clock.ip_clock
        return jsonify(time=current_time,leader= leader, ip=ip), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/update_time', methods=['POST'])
def update_time():
    """
    Atualiza o tempo do relógio.

    :param clock: Dados do relógio.
    :type clock: object
    :param data: Dados para atualização do tempo.
    :type data: dict
    """
    data = request.get_json()
    new_time = data.get('time')
    if clock.set_time_interface(new_time):
        return jsonify(success=True)
    else:
        return jsonify(success=False)

@app.route('/update_drift', methods=['POST'])
def update_drift():
    """
    Atualiza o drift do relógio na classe Clock.

    :param clock: Dados do relógio.
    :type clock: object
    :param data: Dados para atualização do drift.
    :type data: dict
    """
    data = request.get_json()
    new_drift = data.get('drift')
    if clock.set_drift_interface(new_drift):
        return jsonify(success=True)
    else:
        return jsonify(success=False)


def start():

    print("\nIP atual: ", clock.ip_clock)

    try:
        quantity_clocks = int(input("\nQuantidade de relógios: "))

        list_clocks = []
        print()
        for i in range (quantity_clocks):

            ip_clock = input("IP do relógio: ")
            if (not (re.match(r'^(\d{1,3}\.){3}\d{1,3}$', ip_clock))):
                raise ValueError
            list_clocks.append(ip_clock)

        list_clocks.remove(clock.ip_clock)
        print()
        
        threading.Thread(target=Clock_impl.start_count, args=(clock,)).start()  
        threading.Thread(target=Election_impl.periodic_leadership_check, args=(clock,)).start()   
        threading.Thread(target=Clock_impl.add_clocks,args=(clock, list_clocks,)).start()
        app.run(host='0.0.0.0', port=2500)

    except ValueError:
        print("\nDado inválido.")
