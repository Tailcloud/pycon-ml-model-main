#!/usr/bin/env python3
"""
Simple Flask server for flight delay prediction dashboard
"""
import json
import os
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Add current directory to Python path for importing
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class FlightDelayHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        if path == '/':
            self.serve_dashboard()
        elif path == '/predict':
            self.handle_predict(query_params)
        elif path == '/airports':
            self.handle_airports()
        elif path == '/api/stats':
            self.handle_stats()
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Flight Delay Prediction Dashboard</title>

    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(45deg, #2196F3, #21CBF3);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .main-content {
            padding: 30px;
        }
        
        .prediction-form {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        .form-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            background: white;
        }
        
        .form-group select:focus {
            outline: none;
            border-color: #2196F3;
        }
        
        .predict-btn {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .predict-btn:hover {
            transform: translateY(-2px);
        }
        
        .results-section {
            display: none;
            margin-top: 30px;
        }
        
        .results-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 30px;
        }
        
        .prediction-result {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
        }
        
        .probability-display {
            font-size: 3rem;
            font-weight: bold;
            margin: 15px 0;
        }
        
        .on-time { color: #4CAF50; }
        .delayed { color: #f44336; }
        
        .chart-container {
            background: white;
            padding: 20px;
            border-radius: 10px;
            border: 1px solid #eee;
        }
        
        .visual-chart {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
            position: relative;
        }
        
        .donut-chart {
            position: relative;
            width: 150px;
            height: 150px;
        }
        
        .donut-chart .circle {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            position: relative;
            background: conic-gradient(
                #4CAF50 0deg var(--on-time-angle),
                #f44336 var(--on-time-angle) 360deg
            );
        }
        
        .donut-chart .circle::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 80px;
            height: 80px;
            background: white;
            border-radius: 50%;
            transform: translate(-50%, -50%);
        }
        
        .donut-chart .center-text {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            font-weight: bold;
            z-index: 1;
        }
        
        .chart-legend {
            margin-top: 20px;
            display: flex;
            justify-content: center;
            gap: 20px;
        }
        
        .legend-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .legend-color {
            width: 16px;
            height: 16px;
            border-radius: 50%;
        }
        
        .legend-color.on-time { background: #4CAF50; }
        .legend-color.delayed { background: #f44336; }
        
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .stat-card {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 2rem;
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            font-style: italic;
            color: #666;
        }
        
        @media (max-width: 768px) {
            .results-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✈️ Flight Delay Prediction Dashboard</h1>
            <p>Get real-time predictions for flight delays based on airport and day of week</p>
        </div>
        
        <div class="main-content">
            <div class="prediction-form">
                <h2>Make a Prediction</h2>
                <form id="predictionForm">
                    <div class="form-group">
                        <label for="airport">Select Airport:</label>
                        <select id="airport" required>
                            <option value="">Loading airports...</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="dayOfWeek">Day of Week:</label>
                        <select id="dayOfWeek" required>
                            <option value="">Select day</option>
                            <option value="1">Monday</option>
                            <option value="2">Tuesday</option>
                            <option value="3">Wednesday</option>
                            <option value="4">Thursday</option>
                            <option value="5">Friday</option>
                            <option value="6">Saturday</option>
                            <option value="7">Sunday</option>
                        </select>
                    </div>
                    
                    <button type="submit" class="predict-btn">🔮 Predict Flight Status</button>
                </form>
            </div>
            
            <div id="loadingIndicator" class="loading" style="display: none;">
                Making prediction...
            </div>
            
            <div id="resultsSection" class="results-section">
                <div class="results-grid">
                    <div class="prediction-result">
                        <h3>On-Time Probability</h3>
                        <div id="onTimeProb" class="probability-display on-time">--</div>
                        <p>Likelihood of arriving on schedule</p>
                    </div>
                    
                    <div class="prediction-result">
                        <h3>Delay Probability</h3>
                        <div id="delayProb" class="probability-display delayed">--</div>
                        <p>Likelihood of being delayed</p>
                    </div>
                </div>
                
                <div class="chart-container">
                    <h3 style="text-align: center; margin-bottom: 20px;">Flight Status Prediction</h3>
                    <div class="visual-chart">
                        <div class="donut-chart">
                            <div class="circle" id="donutChart"></div>
                            <div class="center-text" id="centerText">
                                <div style="font-size: 14px; color: #666;">Prediction</div>
                            </div>
                        </div>
                    </div>
                    <div class="chart-legend">
                        <div class="legend-item">
                            <div class="legend-color on-time"></div>
                            <span id="onTimeLegend">On-Time</span>
                        </div>
                        <div class="legend-item">
                            <div class="legend-color delayed"></div>
                            <span id="delayedLegend">Delayed</span>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-number" id="totalPredictions">0</div>
                    <div>Total Predictions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="avgDelayProb">0%</div>
                    <div>Avg Delay Probability</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="mostUsedAirport">N/A</div>
                    <div>Most Queried Airport</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let stats = { predictions: 0, totalDelayProb: 0, airports: {} };

        // Load airports on page load
        async function loadAirports() {
            try {
                const response = await fetch('/airports');
                const data = await response.json();
                const select = document.getElementById('airport');
                select.innerHTML = '<option value="">Select an airport</option>';
                
                data.airports.forEach(airport => {
                    const option = document.createElement('option');
                    option.value = airport.id;
                    option.textContent = airport.name;
                    select.appendChild(option);
                });
            } catch (error) {
                console.error('Error loading airports:', error);
                document.getElementById('airport').innerHTML = '<option value="">Error loading airports</option>';
            }
        }

        // Handle form submission
        document.getElementById('predictionForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const airportId = document.getElementById('airport').value;
            const dayOfWeek = document.getElementById('dayOfWeek').value;
            
            if (!airportId || !dayOfWeek) {
                alert('Please select both airport and day of week');
                return;
            }
            
            // Show loading
            document.getElementById('loadingIndicator').style.display = 'block';
            document.getElementById('resultsSection').style.display = 'none';
            
            try {
                const response = await fetch(`/predict?airport_id=${airportId}&day_of_week=${dayOfWeek}`);
                const data = await response.json();
                
                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }
                
                // Update display
                updatePredictionDisplay(data);
                updateStats(airportId, data.delayed);
                
            } catch (error) {
                console.error('Error making prediction:', error);
                alert('Error making prediction. Please try again.');
            } finally {
                document.getElementById('loadingIndicator').style.display = 'none';
            }
        });

        function updatePredictionDisplay(data) {
            const onTimePercent = (data.confident_not_delayed * 100).toFixed(1);
            const delayPercent = (data.delayed * 100).toFixed(1);
            
            document.getElementById('onTimeProb').textContent = onTimePercent + '%';
            document.getElementById('delayProb').textContent = delayPercent + '%';
            
            // Update donut chart
            const onTimeAngle = data.confident_not_delayed * 360;
            const chart = document.getElementById('donutChart');
            chart.style.setProperty('--on-time-angle', onTimeAngle + 'deg');
            
            // Update center text
            const centerText = document.getElementById('centerText');
            const isOnTime = data.confident_not_delayed > data.delayed;
            centerText.innerHTML = `
                <div style="font-size: 12px; color: #666;">Most Likely</div>
                <div style="font-size: 16px; font-weight: bold; color: ${isOnTime ? '#4CAF50' : '#f44336'};">
                    ${isOnTime ? 'On-Time' : 'Delayed'}
                </div>
                <div style="font-size: 12px; color: #666;">${isOnTime ? onTimePercent : delayPercent}%</div>
            `;
            
            // Update legend
            document.getElementById('onTimeLegend').textContent = `On-Time (${onTimePercent}%)`;
            document.getElementById('delayedLegend').textContent = `Delayed (${delayPercent}%)`;
            
            document.getElementById('resultsSection').style.display = 'block';
        }

        function updateStats(airportId, delayProb) {
            stats.predictions++;
            stats.totalDelayProb += delayProb;
            stats.airports[airportId] = (stats.airports[airportId] || 0) + 1;
            
            document.getElementById('totalPredictions').textContent = stats.predictions;
            document.getElementById('avgDelayProb').textContent = 
                (stats.totalDelayProb / stats.predictions * 100).toFixed(1) + '%';
            
            // Find most used airport
            let mostUsed = Object.keys(stats.airports).reduce((a, b) => 
                stats.airports[a] > stats.airports[b] ? a : b
            );
            document.getElementById('mostUsedAirport').textContent = mostUsed || 'N/A';
        }

        // Load airports when page loads
        loadAirports();
    </script>
</body>
</html>
        '''
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def handle_predict(self, query_params):
        """Handle prediction requests"""
        try:
            # Extract parameters
            airport_id = query_params.get('airport_id', [None])[0]
            day_of_week = query_params.get('day_of_week', [None])[0]
            
            if not airport_id or not day_of_week:
                self.send_json_response({
                    'error': "Missing required query parameters: 'airport_id' and 'day_of_week'"
                }, 400)
                return
            
            airport_id = int(airport_id)
            day_of_week = int(day_of_week)
            
            # Load model and make prediction
            try:
                import joblib
                model = joblib.load('model.pkl')
                input_data = [[day_of_week, airport_id]]
                prediction = model.predict_proba(input_data)
                confident_not_delayed, delayed = prediction[0].tolist()
                
                response = {
                    'confident_not_delayed': confident_not_delayed,
                    'delayed': delayed,
                    'airport_id': airport_id,
                    'day_of_week': day_of_week
                }
                
            except Exception as model_error:
                # Fallback to mock prediction if model fails
                import random
                random.seed(airport_id + day_of_week)
                delayed = random.uniform(0.1, 0.4)
                confident_not_delayed = 1.0 - delayed
                
                response = {
                    'confident_not_delayed': confident_not_delayed,
                    'delayed': delayed,
                    'airport_id': airport_id,
                    'day_of_week': day_of_week,
                    'note': 'Using mock prediction due to model loading error'
                }
            
            self.send_json_response(response)
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_airports(self):
        """Handle airports list request"""
        try:
            airports = []
            if os.path.exists('origin_airport.csv'):
                with open('origin_airport.csv', 'r') as f:
                    lines = f.read().splitlines()
                    # Skip header
                    for line in lines[1:]:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            airports.append({
                                'id': int(parts[0]),
                                'name': parts[1]
                            })
                
                # Sort alphabetically
                airports.sort(key=lambda x: x['name'])
            else:
                # Fallback airports
                airports = [
                    {'id': 15304, 'name': 'Tampa International'},
                    {'id': 14122, 'name': 'Pittsburgh International'},
                    {'id': 14747, 'name': 'Seattle/Tacoma International'},
                    {'id': 13930, 'name': "Chicago O'Hare International"},
                    {'id': 12478, 'name': 'John F. Kennedy International'}
                ]
            
            self.send_json_response({'airports': airports})
            
        except Exception as e:
            self.send_json_response({'error': str(e)}, 500)
    
    def handle_stats(self):
        """Handle statistics request"""
        response = {
            'total_predictions': 0,
            'average_delay_probability': 0.2,
            'most_queried_airport': 'Tampa International'
        }
        self.send_json_response(response)
    
    def send_json_response(self, data, status=200):
        """Send JSON response"""
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

def run_server(port=8000):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, FlightDelayHandler)
    print(f"Flight Delay Dashboard running at http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down the server...")
        httpd.shutdown()

if __name__ == '__main__':
    # Change to the script directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    run_server(8000)