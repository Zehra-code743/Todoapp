"""
Kafka producer configuration for the Advanced Todo application.
Sets up Kafka producer for sending events to Kafka topics.
"""
try:
    from kafka import KafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    # Kafka is optional, so if it's not available, we'll disable the functionality
    KafkaProducer = None
    KAFKA_AVAILABLE = False

import json
import os
from typing import Dict, Any
from contextlib import contextmanager
from datetime import datetime


# Kafka configuration
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "localhost:9092")
KAFKA_TASK_EVENTS_TOPIC = os.getenv("KAFKA_TASK_EVENTS_TOPIC", "task-events")
KAFKA_REMINDERS_TOPIC = os.getenv("KAFKA_REMINDERS_TOPIC", "reminders")


class KafkaProducerManager:
    def __init__(self):
        self._producer = None

    def get_producer(self):
        if not KAFKA_AVAILABLE:
            return None

        if self._producer is None:
            self._producer = KafkaProducer(
                bootstrap_servers=KAFKA_BROKERS.split(','),
                value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
                acks='all',  # Wait for all replicas to acknowledge
                retries=3,
                linger_ms=5,  # Small delay to allow batching
                batch_size=16384  # Batch size in bytes
            )
        return self._producer

    def close(self):
        if self._producer:
            self._producer.close()
            self._producer = None


# Global instance
producer_manager = KafkaProducerManager()


@contextmanager
def get_kafka_producer():
    """
    Context manager for Kafka producer.
    Ensures proper cleanup of Kafka producer resources.
    """
    producer = producer_manager.get_producer()
    try:
        yield producer
    finally:
        # Don't close the producer here since it's a shared instance
        pass


def send_task_event(event_type: str, task_data: Dict[str, Any]):
    """
    Send a task-related event to the Kafka task-events topic.

    Args:
        event_type: Type of the event (e.g., "task.created", "task.completed")
        task_data: Dictionary containing task information
    """
    if not KAFKA_AVAILABLE:
        # Log that Kafka is not available if needed for debugging
        print(f"Kafka not available, skipping event: {event_type}")
        return

    producer = producer_manager.get_producer()
    if producer is None:
        print(f"Kafka producer not available, skipping event: {event_type}")
        return

    event = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": task_data
    }

    producer.send(KAFKA_TASK_EVENTS_TOPIC, value=event)
    # Flush to ensure the message is sent
    producer.flush()


def send_reminder_event(event_type: str, reminder_data: Dict[str, Any]):
    """
    Send a reminder-related event to the Kafka reminders topic.

    Args:
        event_type: Type of the event (e.g., "reminder.scheduled", "reminder.sent")
        reminder_data: Dictionary containing reminder information
    """
    if not KAFKA_AVAILABLE:
        # Log that Kafka is not available if needed for debugging
        print(f"Kafka not available, skipping event: {event_type}")
        return

    producer = producer_manager.get_producer()
    if producer is None:
        print(f"Kafka producer not available, skipping event: {event_type}")
        return

    event = {
        "event_type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "data": reminder_data
    }

    producer.send(KAFKA_REMINDERS_TOPIC, value=event)
    # Flush to ensure the message is sent
    producer.flush()