import threading
from flask import Flask, jsonify, request, render_template
from model.Clock import Clock
import impl.Clock_impl as Clock_impl
import impl.Election_impl as Election_impl
import impl.Berkeley_impl as Berkeley_impl


app = Flask(__name__, template_folder='templates', static_folder='static')
clock = Clock()

#Rota para verificar se o relógio está pronto para conexão chamando a função do Clock_impl
@app.route('/ready_for_connection', methods=['GET'])
def ready_for_connection():

    response = Clock_impl.ready_for_connection(clock)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404

#Rota para verificar se o lider foi eleito chamando a função do Election_impl
@app.route('/leader_is_elected', methods=['GET'])
def leader_is_elected():

    response = Election_impl.leader_is_elected(clock)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404

#Rota resposável por eleger o lider chamando a função do Election_impl
@app.route('/claim_leadership', methods=['POST'])
def claim_leadership():

    data = request.json
    response = Election_impl.claim_leadership(clock, data)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404

#Rota resposável por requerir o tempo do relógio chamando a função do Berkeley_impl
@app.route('/request_time', methods=['GET'])
def request_time():

    data = request.json
    response = Berkeley_impl.request_time(clock, data)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404

#Rota resposável por verifiar se houve algum problema com o lider chamando a função do Election_impl
@app.route('/problem_alert_leadership', methods=['POST'])
def problem_alert_leadership():

    data = request.json
    response = Election_impl.receive_problem_alert(clock, data)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404


@app.route('/regulate_time', methods=['POST'])
def regulate_time():

    data = request.json
    response = Berkeley_impl.receive_regulate_time(clock, data)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404


@app.route('/change_time', methods=['PATCH'])
def change_time():

    data = request.json
    response = Clock_impl.change_time(clock, data)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404

@app.route('/')
def home_page():
    return render_template('index.html')

@app.route('/get_clock', methods=['GET'])
def get_clock():
    try:
        current_time = clock.get_current_time()
        return jsonify(time=current_time), 200
    except Exception as e:
        return jsonify(error=str(e)), 500

@app.route('/update_time', methods=['POST'])
def update_time():
    data = request.get_json()
    new_time = data.get('time')
    if clock.set_time_interface(new_time):
        return jsonify(success=True)
    else:
        return jsonify(success=False)

@app.route('/update_drift', methods=['POST'])
def update_drift():
    data = request.get_json()
    new_drift = data.get('drift')
    if clock.set_drift_interface(new_drift):
        return jsonify(success=True)
    else:
        return jsonify(success=False)

def start():
    list_clocks = ["2501","2500","2503","2502"]
    list_clocks.remove(clock.port)
    print("Lista de relógios: ", list_clocks)
    
    threading.Thread(target=Clock_impl.start_count, args=(clock,)).start()  
    threading.Thread(target=Election_impl.periodic_leadership_check, args=(clock,)).start()   
    Thread_Add_Clocks = threading.Thread(target=Clock_impl.add_clocks,args=(clock, list_clocks,)).start()
    app.run(host=clock.ip_clock, port=int(clock.port))

if __name__ == '__main__':
    start()