import pytest
from app import check_device_status

class TestDeviceFunctions:
    
    def setup_method(self):
        """Initialize test data"""
        # Valid IP addresses
        self.valid_ip_1 = "192.168.1.1"
        self.valid_ip_2 = "10.0.0.1"
        
        # Invalid IP addresses
        self.invalid_ip_1 = "999.999.999.999"
        self.invalid_ip_2 = "not_an_ip"
        self.invalid_ip_3 = ""

        # Expected valid statuses
        self.valid_statuses = ["Up", "Down"]
        
    def test_check_device_status_with_valid_ip(self):
        """Test with valid IP addresses"""
        result1 = check_device_status(self.valid_ip_1)
        result2 = check_device_status(self.valid_ip_2)
        
        assert result1 in self.valid_statuses
        assert result2 in self.valid_statuses
    
    def test_check_device_status_with_invalid_ip(self):
        """Test that invalid IP addresses raise ValueError"""
        with pytest.raises(ValueError):
            check_device_status(self.invalid_ip_1)
        
        with pytest.raises(ValueError):
            check_device_status(self.invalid_ip_2)
        
        with pytest.raises(ValueError):
            check_device_status(self.invalid_ip_3)