import threading
from flask import Flask, jsonify, request
from model.Clock import Clock
import impl.Clock_impl as Clock_impl
import impl.Election_impl as Election_impl


app = Flask(__name__)
clock = Clock()

@app.route('/ready_for_connection', methods=['GET'])
def ready_for_connection():

    response = Clock_impl.ready_for_connection(clock)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404


@app.route('/leader_is_elected', methods=['GET'])
def leader_is_elected():

    response = Election_impl.leader_is_elected(clock)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404
    

def start():
    list_clocks = ["2500","2501","2502","2503"]
    list_clocks.remove(clock.port)
    print("Lista de relógios: ", list_clocks)
    
    Thread_Add_Clocks = threading.Thread(target=Clock_impl.add_clocks,args=(clock, list_clocks,)).start()
    app.run(host=clock.ip_clock, port=int(clock.port))

if __name__ == '__main__':
    start()