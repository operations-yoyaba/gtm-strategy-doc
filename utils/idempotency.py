import os
import logging
from typing import Set
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# In-memory storage for idempotency keys (in production, use Redis or database)
_idempotency_keys: Set[str] = set()
_key_timestamps: dict[str, datetime] = {}

def check_idempotency(idempotency_key: str) -> bool:
    """
    Check if a request with this idempotency key is already being processed
    
    Returns True if the key exists (duplicate request), False otherwise
    """
    # Clean up old keys (older than 1 hour)
    _cleanup_old_keys()
    
    if idempotency_key in _idempotency_keys:
        logger.info(f"Duplicate request detected for key: {idempotency_key}")
        return True
    
    return False

def store_idempotency_key(idempotency_key: str) -> None:
    """
    Store an idempotency key to prevent duplicate processing
    """
    _idempotency_keys.add(idempotency_key)
    _key_timestamps[idempotency_key] = datetime.utcnow()
    logger.info(f"Stored idempotency key: {idempotency_key}")

def remove_idempotency_key(idempotency_key: str) -> None:
    """
    Remove an idempotency key after processing is complete
    """
    if idempotency_key in _idempotency_keys:
        _idempotency_keys.remove(idempotency_key)
        if idempotency_key in _key_timestamps:
            del _key_timestamps[idempotency_key]
        logger.info(f"Removed idempotency key: {idempotency_key}")

def _cleanup_old_keys() -> None:
    """
    Remove idempotency keys older than 1 hour
    """
    cutoff_time = datetime.utcnow() - timedelta(hours=1)
    keys_to_remove = []
    
    for key, timestamp in _key_timestamps.items():
        if timestamp < cutoff_time:
            keys_to_remove.append(key)
    
    for key in keys_to_remove:
        remove_idempotency_key(key)
    
    if keys_to_remove:
        logger.info(f"Cleaned up {len(keys_to_remove)} old idempotency keys")

# For production, you would implement these with Redis or a database:
# def check_idempotency_redis(idempotency_key: str) -> bool:
#     """Redis-based idempotency check"""
#     redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))
#     return redis_client.exists(f"idempotency:{idempotency_key}") > 0
#
# def store_idempotency_key_redis(idempotency_key: str) -> None:
#     """Store idempotency key in Redis with 1-hour expiration"""
#     redis_client = redis.Redis.from_url(os.getenv("REDIS_URL"))
#     redis_client.setex(f"idempotency:{idempotency_key}", 3600, "1") 