from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
from tensorflow.keras.models import load_model
import random
import threading
from scapy.all import sniff, IP, TCP
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

# Load pre-trained models and preprocessing objects
model = load_model('hybrid_aclr_model.h5')
with open('scaler.pkl', 'rb') as scaler_file:
    scaler = pickle.load(scaler_file)

encoders = {}
for col in ['proto', 'service']:
    with open(f'{col}_encoder.pkl', 'rb') as encoder_file:
        encoders[col] = pickle.load(encoder_file)

with open('attack_cat_encoder.pkl', 'rb') as attack_cat_file:
    attack_cat_encoder = pickle.load(attack_cat_file)

live_capture_running = False

# Function to preprocess user input
def preprocess_user_input(user_input):
    for col in ['proto', 'service']:
        if col in user_input and user_input[col] in encoders[col].classes_:
            user_input[col] = encoders[col].transform([user_input[col]])[0]
        else:
            user_input[col] = 0  # Default encoding for unknown values

    input_array = np.array([list(user_input.values())])
    input_scaled = scaler.transform(input_array)
    input_reshaped = np.expand_dims(input_scaled, axis=-1)
    return input_scaled, input_reshaped

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/live_capture')
def live_capture():
    return render_template('live_capture.html')

def capture_packets():
    global live_capture_running
    live_capture_running = True

    def process_packet(packet):
        if not live_capture_running:
            return

        try:
            user_input = {}

            if IP in packet:
                user_input["proto"] = str(packet.proto)  
                user_input["sbytes"] = len(packet)  
                user_input["dbytes"] = len(packet.payload)  
                user_input["sttl"] = packet.ttl  

            if TCP in packet:
                user_input["swin"] = packet[TCP].window  
                user_input["dwin"] = packet[TCP].window if hasattr(packet[TCP], "window") else 0
            else:
                user_input["swin"] = 0
                user_input["dwin"] = 0

            user_input["rate"] = 1  
            user_input["smean"] = user_input["sbytes"]  
            user_input["dmean"] = user_input["dbytes"]  

            input_scaled, input_reshaped = preprocess_user_input(user_input)

            prediction = model.predict([input_scaled, input_reshaped, input_reshaped, input_reshaped])
            attack_category = attack_cat_encoder.inverse_transform([np.argmax(prediction, axis=1)])[0]

            # Send the data to the frontend via WebSocket
            socketio.emit('new_packet', {
                "proto": user_input["proto"],
                "sbytes": user_input["sbytes"],
                "dbytes": user_input["dbytes"],
                "sttl": user_input["sttl"],
                "attack_type": attack_category
            })

        except Exception as e:
            print(f"Error processing packet: {e}")

    sniff(filter="ip", prn=process_packet, store=0)

@app.route('/start_live_capture')
def start_live_capture():
    thread = threading.Thread(target=capture_packets)
    thread.start()
    return jsonify({"message": "Live capture started..."})

@app.route('/stop_live_capture')
def stop_live_capture():
    global live_capture_running
    live_capture_running = False
    return jsonify({"message": "Live capture stopped."})

if __name__ == '__main__':
    socketio.run(app, debug=True)
