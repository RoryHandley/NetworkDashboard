from unittest.mock import patch, MagicMock
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

    @patch('app.redis_client')
    def test_get_device_info_with_redis_down(self, mock_redis):
        """Test function works when Redis is unavailable"""
        # Simulate Redis being down
        mock_redis.get.side_effect = Exception("Redis connection failed")
        
        result = get_device_info()
        
        # Should return a list (empty or with data from MongoDB)
        assert isinstance(result, list)
    
    @patch('app.database_client')
    def test_get_device_info_with_mongodb_down(self, mock_db):
        """Test function returns fallback data when MongoDB is unavailable"""
        # Simulate MongoDB being down
        mock_db.devices.device_info.find.side_effect = Exception("MongoDB connection failed")
        
        result = get_device_info()
        
        # Should return list from redis cache
        assert isinstance(result, list)

    @patch('app.redis_client')
    @patch('app.database_client')
    def test_get_device_info_with_both_down(self, mock_db, mock_redis):
        """Test function works when both Redis and MongoDB are unavailable"""
        # Simulate both being down
        mock_redis.get.side_effect = Exception("Redis connection failed")
        mock_db.devices.device_info.find.side_effect = Exception("MongoDB connection failed")
        
        result = get_device_info()
        
        # Should return empty list
        assert isinstance(result, list)