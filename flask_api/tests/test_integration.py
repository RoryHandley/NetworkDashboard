import pytest
import subprocess
import time
from app import get_device_info, app

class TestAPIIntegration:
    
    def setup_method(self):
        """Initialize test data for integration tests"""
        # Initialize valid test data
        self.valid_fields = ["id", "name", "ip_address"]

    
    def test_get_cached_device_info_returns_data_valid(self):
        """Test that get_cached_device_info always returns device data"""
        result = get_device_info()
        
        assert isinstance(result, list)
        
        for device in result:
            for field in self.valid_fields:
                assert field in device
    
    def test_devices_endpoint_returns_success(self):
        """Test /devices endpoint returns 200 and valid data"""
        with app.test_client() as client: # Use Flask test_client method to create test client
            response = client.get('/devices')
            
            assert response.status_code == 200
            
            data = response.get_json()
            assert isinstance(data, list)
    
    def test_devices_endpoint_has_required_fields(self):
        """Test /devices endpoint returns devices with all required fields"""
        with app.test_client() as client:
            response = client.get('/devices')
            data = response.get_json()
            
            for device in data:
                for field in self.valid_fields:
                    assert field in device

    def test_get_device_info_with_redis_down(self):
        """Test function works when Redis is unavailable"""
        # Stop Redis container
        subprocess.run(['docker', 'stop', 'network_redis'], capture_output=True)
        
        try:
            result = get_device_info()
            
            # Should still return fallback data
            assert isinstance(result, list)
            
            # Verify it has fallback device data
            device_names = [device['name'] for device in result]
            assert 'Router1' in device_names
            assert 'Switch1' in device_names
            assert 'Firewall1' in device_names
            
        finally:
            # Always restart Redis after test
            subprocess.run(['docker', 'start', 'network_redis'], capture_output=True)
            time.sleep(2)  # Give Redis time to start before next test
    
    def test_get_device_info_with_mongodb_down(self):
        """Test function returns fallback data when MongoDB is unavailable"""
        # Stop MongoDB container
        subprocess.run(['docker', 'stop', 'network_mongodb'], capture_output=True)
        
        try:
            result = get_device_info()
            
            # Should return fallback data
            assert isinstance(result, list)
            
            # Verify fallback data structure
            for device in result:
                assert 'id' in device
                assert 'name' in device
                assert 'ip_address' in device
                
        finally:
            # Always restart MongoDB after test
            subprocess.run(['docker', 'start', 'network_mongodb'], capture_output=True)
            time.sleep(3)  # Give MongoDB time to start

    def test_get_device_info_with_redis_and_mongodb_down(self):
        """Test function works when Redis and Database are unavailable"""
        # Stop Redis container
        subprocess.run(['docker', 'stop', 'network_redis'], capture_output=True)
        # Stop MongoDB container
        subprocess.run(['docker', 'stop', 'network_mongodb'], capture_output=True)
        
        try:
            result = get_device_info()
            
            # Should still return fallback data
            assert isinstance(result, list)
            
            # Verify it has fallback device data
            device_names = [device['name'] for device in result]
            assert 'Router1' in device_names
            assert 'Switch1' in device_names
            assert 'Firewall1' in device_names
            
        finally:
            # Always restart containers after test
            subprocess.run(['docker', 'start', 'network_redis'], capture_output=True)
            subprocess.run(['docker', 'start', 'network_mongodb'], capture_output=True)
            time.sleep(2)  # Give containers to start before next test