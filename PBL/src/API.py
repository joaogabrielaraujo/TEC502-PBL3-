from flask import Flask, jsonify, request
from Clock import Clock
import Election
import Clock_impl

app = Flask(__name__)
clock = Clock()

@app.route('/ready_for_connection', methods=['GET'])
def ready_for_connection():

    response = Clock_impl.ready_for_connection(clock)
      
    if response["Bem sucedido"] == True:
        return jsonify(response), 200
    else:
        return jsonify(response), 404
    

