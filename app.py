from flask import Flask, request, jsonify
import os
from mvrp_service.worker.vehicleRouting import mvrp

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/mvrp', methods=['POST'])
def upload_file():

    # Check if the POST request has the file part
    if 'mvrpFile' not in request.files:
        return jsonify({'error': 'No mvrpFile part'}), 400

    file = request.files['mvrpFile']

    # If user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        return jsonify({'error': 'No selected mvrpFile'}), 400

    if file:
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        total_distance_without_allocating_vehicles, total_demand_without_allocating_vehicles, \
        total_time_serving_without_allocating_vehicles, route_served_List_return, \
        route_not_served_List_return, total_demand_served, \
        total_distance_served, total_time_serving_served = mvrp(file_path)
        return jsonify({
                        'total_distance_without_allocating_vehicles': total_distance_without_allocating_vehicles, 
                        'total_demand_without_allocating_vehicles': total_demand_without_allocating_vehicles, 
                        'total_time_serving_without_allocating_vehicles': total_time_serving_without_allocating_vehicles,
                        'total_distance_served': total_distance_served,
                        'total_demand_served': total_demand_served,
                        'total_time_serving_served': total_time_serving_served,
                        'route_served_List_return': route_served_List_return,
                        'route_not_served_List_return': route_not_served_List_return
        }), 200

if __name__ == '__main__':
    app.run(debug=True)
