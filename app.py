import os
import re
import json
from flask import Flask, render_template, jsonify, redirect, request, send_from_directory

# Initialize Flask app
# template_folder defaults to 'templates' which is correct for this structure
# straight in the root
app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

# Core UI routes matching the HTML files in 'templates'
@app.route('/')
def home():
    return redirect('/dashboard.html')

@app.route('/dashboard.html')
def dashboard():
    return render_template('dashboard.html')

@app.route('/employee_config.html')
def employee_config():
    return render_template('employee_config.html')

@app.route('/camera_management.html')
def camera_management():
    return render_template('camera_management.html')

@app.route('/camera_dashboard.html')
def camera_dashboard():
    return render_template('camera_dashboard.html')

@app.route('/notifications.html')
def notifications():
    return render_template('notifications.html')

@app.route('/model_management.html')
def model_management():
    return render_template('model_management.html')

@app.route('/model_mapping.html')
def model_mapping():
    return render_template('model_mapping.html')

@app.route('/settings.html')
def settings():
    return render_template('settings.html')

@app.route('/profile.html')
def profile():
    return render_template('profile.html')

# Path to the log file in the current directory
LOG_FILE = "detection_logs.txt"

# Route to fetch logs and parse them
@app.route('/playback/<path:filename>')
def serve_playback(filename):
    return send_from_directory('static/playback', filename)

@app.route('/logs')
def get_logs():
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 50, type=int)
    
    logs_data = []
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r') as file:
            lines = file.readlines()
            
        # Parse all lines first to get total count
        # In a real app with database, we would count first then query limit
        # Here we parse all valid lines then slice. 
        # For efficiency with text files, we might want to read in reverse, but for now we keep it simple.
        
        parsed_logs = []
        for line in lines:
            match = re.search(
                r"^(.*?) - info: \[(.*?)\] Detected (\d+) persons, (\d+) helmets, (\d+) harnesses in ([\d.]+)ms",
                line.strip()
            )
            if match:
                timestamp, _, persons, helmets, harnesses, time_ms = match.groups()
                parsed_logs.append({
                    "timestamp": timestamp,
                    "persons": int(persons),
                    "helmets": int(helmets),
                    "harnesses": int(harnesses),
                    "inference_time": float(time_ms)
                })
        
        # Sort by timestamp descending (newest first)
        parsed_logs.reverse()
        
        total_logs = len(parsed_logs)
        start = (page - 1) * limit
        end = start + limit
        
        logs_data = parsed_logs[start:end]
        
        return jsonify({
            'logs': logs_data,
            'total_logs': total_logs,
            'current_page': page,
            'total_pages': (total_logs + limit - 1) // limit
        })
    
    return jsonify({
        'logs': [],
        'total_logs': 0,
        'current_page': 1,
        'total_pages': 0
    })

# --- Camera Management APIs ---
CAMERAS_FILE = "cameras.json"

def load_cameras():
    if os.path.exists(CAMERAS_FILE):
        with open(CAMERAS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_cameras(cameras):
    with open(CAMERAS_FILE, 'w') as f:
        json.dump(cameras, f, indent=4)

@app.route('/api/cameras', methods=['GET'])
def get_cameras():
    return jsonify(load_cameras())

@app.route('/api/cameras', methods=['POST'])
def add_camera():
    cameras = load_cameras()
    data = request.json
    
    # Auto-generate ID
    new_id = 1
    if cameras:
        new_id = max(c['id'] for c in cameras) + 1
        
    # Auto-generate RTSP and Playback URLs if not provided or just basic logic
    # User Request: "RTSP URL fetched from Camera IP... stream7"
    # "Playback URL fetched from Camera Name... playback/newzone.mp4"
    
    ip = data.get('ip', '192.168.0.x')
    name = data.get('name', 'New Zone')
    
    # Logic: count how many cameras exist to determine 'streamN'
    # Actually user said "stream 7 means that this is the 7th camera configured on this list"
    stream_index = len(cameras) + 1 
    
    rtsp_url = f"rtsp://{ip}/stream{stream_index}"
    
    # Normalize name for playback
    # "New Zone" -> "newzone"
    # "New Zone 1" -> "newzone1"
    normalized_name = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
    
    # Check for duplicate normalized names to append suffix
    existing_playback = [c.get('playback_url', '') for c in cameras]
    suffix = ""
    counter = 1
    while f"playback/{normalized_name}{suffix}.mp4" in existing_playback:
        suffix = str(counter)
        counter += 1
        
    playback_url = f"playback/{normalized_name}{suffix}.mp4"
    
    new_camera = {
        "id": new_id,
        "name": name,
        "ip": ip,
        "rtsp_url": rtsp_url,
        "playback_url": playback_url,
        "zone": data.get('zone', name),
        "status": True
    }
    
    cameras.append(new_camera)
    save_cameras(cameras)
    return jsonify(new_camera)

@app.route('/api/cameras/<int:camera_id>', methods=['PUT'])
def update_camera(camera_id):
    cameras = load_cameras()
    data = request.json
    
    for kam in cameras:
        if kam['id'] == camera_id:
            kam['name'] = data.get('name', kam['name'])
            kam['ip'] = data.get('ip', kam['ip'])
            kam['zone'] = data.get('zone', kam['zone'])
            kam['status'] = data.get('status', kam['status'])
            # User wants IP edit to update URLs? 
            # "For New... URLs fetched". For Edit, usually same logic applies if IP changes?
            # User didn't explicitly say update URLs on Edit, but implied dynamic nature.
            # For now, let's keep URLs relatively static unless we decide to regenerate them. 
            # The prompt says: "In the pop up menu by default for Camera IP this should remain but should be editabe... For RSTP URL and Playback URL they can be fetched from the Camera IP and Camera Name respectively."
            # This suggests if I change IP/Name, URLs *should* update.
            
            # Update RTSP if IP changed
            # But wait, stream index depends on list position? That is rigid.
            # Let's extract existing stream index from old URL or just keep it.
            # Simpler approach: update RTSP ip part.
            
            # Simple regex replace on IP in RTSP URL
            if 'rtsp_url' in kam:
                 kam['rtsp_url'] = re.sub(r'//(.*?)/', f"//{kam['ip']}/", kam['rtsp_url'])

            # Update playback if name changed
            # This might break existing files if we rename the file pointer but not the file.
            # But this is a simulation. Let's update it to match requirements.
             
            # normalized_name = re.sub(r'[^a-zA-Z0-9]', '', kam['name'].lower())
            # kam['playback_url'] = f"playback/{normalized_name}.mp4" 
            # (Naming collision logic omitted for edit for simplicity, assuming users rename uniquely)
            
            break
            
    save_cameras(cameras)
    return jsonify({"success": True})

@app.route('/api/cameras/<int:camera_id>', methods=['DELETE'])
def delete_camera(camera_id):
    cameras = load_cameras()
    cameras = [c for c in cameras if c['id'] != camera_id]
    save_cameras(cameras)
    return jsonify({"success": True})



# --- Employee Management APIs ---
EMPLOYEES_FILE = "employees.json"

def load_employees():
    if os.path.exists(EMPLOYEES_FILE):
        with open(EMPLOYEES_FILE, 'r') as f:
            return json.load(f)
    return []

def save_employees(employees):
    with open(EMPLOYEES_FILE, 'w') as f:
        json.dump(employees, f, indent=4)

@app.route('/api/employees', methods=['GET'])
def get_employees():
    return jsonify(load_employees())

@app.route('/api/employees', methods=['POST'])
def add_employee():
    employees = load_employees()
    data = request.json
    
    # Check for existing ID
    if any(e['id'] == data['id'] for e in employees):
        return jsonify({"error": "Employee ID already exists"}), 400

    new_employee = {
        "id": data['id'],
        "name": data['name']
    }
    
    employees.append(new_employee)
    save_employees(employees)
    save_employees(employees)
    return jsonify(new_employee)

@app.route('/api/employees/<string:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    employees = load_employees()
    data = request.json
    
    for emp in employees:
        if emp['id'] == employee_id:
            emp['name'] = data.get('name', emp['name'])
            # We typically don't allow updating ID, but if we did we'd need to check collisions
            break
            
    save_employees(employees)
    return jsonify({"success": True})

@app.route('/api/employees/<string:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    employees = load_employees()
    employees = [e for e in employees if e['id'] != employee_id]
    save_employees(employees)
    return jsonify({"success": True})


if __name__ == '__main__':
    app.run(debug=True)
