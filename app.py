"""
Weather Web Application
A simple Flask web app that displays weather information using OpenWeatherMap API.
"""

from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime

app = Flask(__name__)

# API Configuration
# Get free API key from https://openweathermap.org/api
WEATHER_API_KEY = "fc97243422a76b701b8430b97686a9b6"
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

@app.route('/')
def index():
    """Render the home page"""
    return render_template('index.html')

@app.route('/api/weather', methods=['POST'])
def get_weather():
    """
    Fetch weather data from API
    Expects JSON with 'city' parameter
    """
    try:
        data = request.get_json()
        city = data.get('city', '').strip()
        
        if not city:
            return jsonify({'error': 'City name is required'}), 400
        
        # Make API request
        params = {
            'q': city,
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(WEATHER_API_URL, params=params, timeout=5)
        
        if response.status_code == 404:
            return jsonify({'error': 'City not found. Please check the spelling.'}), 404
        
        if response.status_code == 401:
            return jsonify({'error': 'Invalid API key. Please contact admin.'}), 401
        
        if response.status_code != 200:
            return jsonify({'error': f'Weather service error: {response.status_code}'}), 500
        
        weather_data = response.json()
        
        # Extract relevant information
        result = {
            'city': weather_data['name'],
            'country': weather_data['sys']['country'],
            'temperature': round(weather_data['main']['temp']),
            'feels_like': round(weather_data['main']['feels_like']),
            'humidity': weather_data['main']['humidity'],
            'pressure': weather_data['main']['pressure'],
            'description': weather_data['weather'][0]['description'],
            'wind_speed': round(weather_data['wind']['speed'], 1),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return jsonify(result), 200
    
    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout. Please try again.'}), 504
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Connection error. Check your internet connection.'}), 503
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500

@app.route('/api/weather/forecast', methods=['POST'])
def get_forecast():
    """
    Get weather forecast for a city
    """
    try:
        data = request.get_json()
        city = data.get('city', '').strip()
        
        if not city:
            return jsonify({'error': 'City name is required'}), 400
        
        # Using free forecast API
        forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            'q': city,
            'appid': WEATHER_API_KEY,
            'units': 'metric'
        }
        
        response = requests.get(forecast_url, params=params, timeout=5)
        
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch forecast data'}), 500
        
        forecast_data = response.json()
        
        # Extract 5-day forecast (every 24 hours)
        forecasts = []
        for item in forecast_data['list'][::8]:  # Every 8th item = ~24 hours
            forecasts.append({
                'date': item['dt_txt'],
                'temperature': round(item['main']['temp']),
                'description': item['weather'][0]['description'],
                'humidity': item['main']['humidity']
            })
        
        return jsonify({'forecasts': forecasts}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Page not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({'error': 'Server error'}), 500

if __name__ == '__main__':
    # Check if API key is set
    if WEATHER_API_KEY == "YOUR_API_KEY_HERE":
        print("⚠️  WARNING: Please set your OpenWeatherMap API key in app.py")
        print("Get a free API key from: https://openweathermap.org/api")
    else:
        print("✅ API Key is set!")
    
    print("🌤️  Weather App is running on http://localhost:5000")
    print("Press CTRL+C to stop the server")
    app.run(debug=True, host='0.0.0.0', port=5000)
