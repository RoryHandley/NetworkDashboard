from flask import Flask, jsonify
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ExecutionTimeout
import redis
import json
import logging
import time
import random
from datetime import datetime
import re

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def connect_to_mongodb():
    """
        Connect to MongoDB and return client and db, or None if failed
        Reference - https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html
    """
    try:
        # Create DB Client object to connect to mongoDb
        client = MongoClient('mongodb://mongodb:27017/', serverSelectionTimeoutMS=3000)
        
        logger.info("MongoDB connected successfully")

        return client
    except ConnectionFailure as e:
        logger.error(f"MongoDB connection failed: {e}")
        return None
    except Exception as e:
        logger.error("Unknown error connecting to MongoDB")
        return None

def connect_to_redis():
    """
        Connect to Redis and return client, or None if failed
        Reference - https://github.com/redis/redis-py  
    """
    try:
        redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)
        # Test connection
        redis_client.ping()
        logger.info("Redis connected successfully")
        return redis_client
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return None

# Initialize connections on flask app start
database_client = connect_to_mongodb()
redis_client = connect_to_redis()

def check_device_status(ip_address):
    """Simulate real-time status check like ping or SNMP"""
    # Check the provided IP address is valid
    ip_pattern = r'^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    
    if not re.match(ip_pattern, ip_address):
        raise ValueError(f"Invalid IP address: {ip_address}")
    
    # Simulate occasional failures (10% chance down)
    return "Up" if random.random() > 0.1 else "Down"

def get_device_info():
    """Get device info from cache, or fetch from database if not cached"""
    # Start timer for logging purposes
    start_time = time.time()
    
    # If Redis was available at startup 
    if redis_client:
        try:
            # Check cache
            cached_info = redis_client.get('device_info')

            if cached_info:
                # Cache hit - log and return 
                end_time = time.time()
                duration = round((end_time - start_time) * 1000, 2)
                logger.info(f"DEVICE INFO CACHE HIT - Served from Redis in {duration}ms")
                return json.loads(cached_info)
            else: 
                logger.info("DEVICE INFO CACHE MISS - Checking if Database is available")
        except Exception as e:
            # Redis has failed since app startup
            logger.error("Error accessing Redis - Trying database")
    
    # If Database was available at startup
    # Note we only hit here if either redis isn't available, or if it is available but doesn't have cached info
    if database_client:
        try: 
            # Get Database instance for 'devices' database
            db = database_client.devices

            # Return all documents in the device_info collection, suppressing _id
            device_info = list(db.device_info.find({}, {'_id': 0}).max_time_ms(3000))

            # Try to cache it
            # Maybe we could use flags instead to avoid trying redis if we know it's down
            if redis_client:
                try:
                    redis_client.setex('device_info', 300, json.dumps(device_info))
                    logger.info("Data stored in cache")
                except:
                    logger.info("Could not cache data")
                    pass  # Cache failed, but continue

            end_time = time.time()
            duration = round((end_time - start_time) * 1000, 2)
            logger.info(f"Device info fetched from MongoDB in {duration}ms")
            return device_info
        except ExecutionTimeout:
            logger.error("MongoDB query timedout after 3 seconds")
        except Exception as e:
            logger.error("Error accessing MongoDB")
        
        # Redis and database have failed
        return None
    
    # Could not connect to redis or database on app startup
    return None

@app.route('/devices', methods=['GET'])
def get_devices():
    # Get device info from cache/database/fallback
    device_info = get_device_info() 
    
    # Get live status by "monitoring" each device
    for device in device_info:
        device['status'] = check_device_status(device['ip_address'])
        device['last_check'] = datetime.now().isoformat()
    
    return jsonify(device_info)
        

if __name__ == '__main__':
    # 0.0.0.0 so Container can listen to requests from external source
    app.run(host='0.0.0.0', port=8000, debug=True)