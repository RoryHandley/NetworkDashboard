db = db.getSiblingDB('devices');

db.device_info.insertMany([
  {"id": 1, "name": "Router1", "ip_address": "192.168.1.1"},
  {"id": 2, "name": "Switch1", "ip_address": "192.168.1.2"},
  {"id": 3, "name": "Firewall1", "ip_address": "192.168.1.3"}
]);
