from django.shortcuts import render
import requests

def device_dashboard(request):
    # Call Flask API
    try:
        response = requests.get('http://flask_api:8000/devices')
        
        devices = response.json() # Pull JSON body of response

        # Add a simple flag if any device is down
        has_error = any(device['status'] == 'Down' for device in devices)

    except Exception as e:
        devices = []  # Empty list if API fails
        has_error = False  # Set even if backend API fails
        print(f"API Error: {e}")  # For debugging
    
    return render(request, 'device_dashboard.html', {
            'devices': devices, 
            'has_error': has_error
        })

