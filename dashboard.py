import serial
import threading
import json
import time
from flask import Flask, jsonify, render_template_string

# --- CONFIGURATION ---
SERIAL_PORT = 'COM10'
BAUD_RATE = 9600

app = Flask(__name__)

# Dictionary to store the latest 6-sensor data
latest_data = {
    "p1": 0.0, "p2": 0.0, "p3": 0.0, "p4": 0.0, "p5": 0.0, "p6": 0.0,
    "diff12": 0.0, "diff23": 0.0, "diff34": 0.0, "diff45": 0.0, "diff56": 0.0
}

def read_serial_data():
    global latest_data
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2) 
        print(f"Successfully connected to Arduino on {SERIAL_PORT}")
        
        while True:
            if ser.in_waiting > 2000:
                line = ser.readline().decode('utf-8').strip()
                if line.startswith("{") and line.endswith("}"):
                    try:
                        data = json.loads(line)
                        p1, p2, p3 = data.get("p1", 0.0), data.get("p2", 0.0), data.get("p3", 0.0)
                        p4, p5, p6 = data.get("p4", 0.0), data.get("p5", 0.0), data.get("p6", 0.0)
                        
                        latest_data.update({
                            "p1": p1, "p2": p2, "p3": p3, "p4": p4, "p5": p5, "p6": p6,
                            "diff12": (p1 - p2)*10, "diff23": (p2 - p3)*10, "diff34": (p3 - p4)*10, 
                            "diff45": (p4 - p5)*10, "diff56": (p5 - p6)*10
                        })
                    except json.JSONDecodeError:
                        pass
    except Exception as e:
        print(f"\n[ERROR] Could not connect to {SERIAL_PORT}. \nError details: {e}")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Live Leak Monitor</title>
  <style>
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f1ea; text-align: center; margin: 0; padding: 20px; color: #333;}
    .manifold-container { background-color: #e1c699; border: 3px solid #c2a370; border-radius: 10px; display: inline-block; padding: 20px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); margin-bottom: 20px;}
    svg { width: 900px; height: 300px; }
    .tube { fill: none; stroke-width: 18; stroke-linecap: round; transition: stroke 0.3s ease; }
    .sensor-node { fill: #2c3e50; stroke: #ecf0f1; stroke-width: 2; transition: fill 0.3s ease;}
    .sensor-text { font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; fill: #333; }
    
    .stats-container { display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; max-width: 900px; margin: 0 auto; }
    .stat-card { background: white; padding: 15px 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); width: 120px; font-size: 1.1rem; transition: all 0.3s ease;}
    .stat-card span { font-size: 1.5rem; font-weight: bold; display: block; margin-top: 5px;}
    .safe { border-top: 5px solid #3498db; }
    .alert { border-top: 5px solid #e74c3c; color: #e74c3c; animation: pulse 1.5s infinite; }
    
    @keyframes pulse {
      0% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0.4); }
      70% { box-shadow: 0 0 0 10px rgba(231, 76, 60, 0); }
      100% { box-shadow: 0 0 0 0 rgba(231, 76, 60, 0); }
    }
  </style>
</head>
<body>

  <h2>Leakage Detector System</h2>
  
  <div class="manifold-container">
    <svg id="manifold-svg">
      <!-- Pipes -->
      <path id="tube-0" class="tube" d="M 100 250 C 160 250, 160 100, 220 100" stroke="#3498db" />
      <path id="tube-1" class="tube" d="M 220 100 C 280 100, 280 250, 340 250" stroke="#3498db" />
      <path id="tube-2" class="tube" d="M 340 250 C 400 275, 400 275, 460 280" stroke="#3498db" />
      <path id="tube-3" class="tube" d="M 460 280 C 520 275, 520 275, 580 250" stroke="#3498db" />
      <path id="tube-4" class="tube" d="M 580 250 C 640 250, 640 100, 700 100" stroke="#3498db" />
      <path id="tube-5" class="tube" d="M 700 100 C 760 100, 760 250, 820 250" stroke="#3498db" />
      <!-- Sensors Nodes -->
      <circle cx="100" cy="250" r="15" class="sensor-node"/>
      <text cx="100" cy="285" class="sensor-text" text-anchor="middle">S1: <tspan id="val-p1">--</tspan></text>

      <circle cx="220" cy="100" r="15" class="sensor-node"/>
      <text cx="220" cy="135" class="sensor-text" text-anchor="middle">S2: <tspan id="val-p2">--</tspan></text>

      <circle cx="340" cy="250" r="15" class="sensor-node"/>
      <text cx="340" cy="285" class="sensor-text" text-anchor="middle">S3: <tspan id="val-p3">--</tspan></text>

      <circle cx="580" cy="250" r="15" class="sensor-node"/>
      <text cx="580" cy="285" class="sensor-text" text-anchor="middle">S4: <tspan id="val-p4">--</tspan></text>

      <circle cx="700" cy="100" r="15" class="sensor-node"/>
      <text cx="700" cy="135" class="sensor-text" text-anchor="middle">S5: <tspan id="val-p5">--</tspan></text>
        
      <circle cx="820" cy="250" r="15" class="sensor-node"/>
      <text cx="820" cy="135" class="sensor-text" text-anchor="middle">S6: <tspan id="val-p6">--</tspan></text>
    </svg>
  </div>

  <div class="stats-container">
    <div class="stat-card safe" id="card-0">Δ (S1-S2)<span id="diff-0">--</span></div>
    <div class="stat-card safe" id="card-1">Δ (S2-S3)<span id="diff-1">--</span></div>
    <div class="stat-card safe" id="card-2">Δ (S3-S4)<span id="diff-2">--</span></div>
    <div class="stat-card safe" id="card-3">Δ (S4-S5)<span id="diff-3">--</span></div>
    <div class="stat-card safe" id="card-4">Δ (S5-S6)<span id="diff-4">--</span></div>
  </div>

  <script>
    // --- CONFIGURE YOUR LEAK TOLERANCE HERE ---
    // Make sure this number matches the real-world units you calibrated 
    // your Arduino for (e.g., if you calibrated in PSI, this is 25.0 PSI)
    const THRESHOLD = 35.0; 

    setInterval(function() {
      fetch('/data')
        .then(response => response.json())
        .then(data => {
          
          // 1. Update Absolute Pressures on the SVG
          document.getElementById('val-p1').innerText = data.p1.toFixed(1);
          document.getElementById('val-p2').innerText = data.p2.toFixed(1);
          document.getElementById('val-p3').innerText = data.p3.toFixed(1);
          document.getElementById('val-p4').innerText = data.p4.toFixed(1);
          document.getElementById('val-p5').innerText = data.p5.toFixed(1);
          document.getElementById('val-p6').innerText = data.p6.toFixed(1);

          // 2. Gather the calculated differences from the Python server
          const diffs = [
            Math.abs(data.diff12), 
            Math.abs(data.diff23), 
            Math.abs(data.diff34), 
            Math.abs(data.diff45), 
            Math.abs(data.diff56)
          ];

          // 3. Map the 5 differences to the 6 visual SVG tubes
          const tubeMapping = [
            ['tube-0'],           // S1 to S2
            ['tube-1'],           // S2 to S3
            ['tube-2', 'tube-3'], // S3 to S4 (drawn with two SVG paths)
            ['tube-4'],           // S4 to S5
            ['tube-5']            // S5 to S6
          ];

          // 4. Update the display and check for leaks
          for (let i = 0; i < 5; i++) {
            let card = document.getElementById('card-' + i);
            let diffText = document.getElementById('diff-' + i);
            
            diffText.innerText = diffs[i].toFixed(1);
            let isLeaking = diffs[i] > THRESHOLD;
            
            // Update the card UI
            card.className = isLeaking ? "stat-card alert" : "stat-card safe";
            
            // Update the mapped tube(s) UI
            tubeMapping[i].forEach(tubeId => {
              let tube = document.getElementById(tubeId);
              if (tube) {
                tube.setAttribute('stroke', isLeaking ? '#e74c3c' : '#3498db');
              }
            });
          }
        });
    }, 1000); // Requests new data every 1 second
  </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/data')
def data():
    return jsonify(latest_data)

if __name__ == '__main__':
    serial_thread = threading.Thread(target=read_serial_data, daemon=True)
    serial_thread.start()
    
    print("\nStarting Web Server...")
    print(">>> OPEN YOUR WEB BROWSER AND GO TO: http://127.0.0.1:5000 <<<\n")
    
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    
    app.run(host='0.0.0.0', port=5000)