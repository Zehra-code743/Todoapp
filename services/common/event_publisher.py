"""
Event Publisher Utility for Dapr Pub/Sub
Provides a standardized way to publish events across services
"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
import logging

from dapr.clients import DaprClient

# Configure logging
logger = logging.getLogger(__name__)

class EventType(Enum):
    """Enumeration of all possible event types in the system"""
    TASK_CREATED = "task.created"
    TASK_UPDATED = "task.updated"
    TASK_COMPLETED = "task.completed"
    TASK_DELETED = "task.deleted"
    REMINDER_SCHEDULED = "reminder.scheduled"
    REMINDER_TRIGGERED = "reminder.triggered"
    RECURRING_TASK_CREATED = "recurring_task.created"


class EventPublisher:
    """Utility class for publishing events via Dapr pub/sub"""

    def __init__(self, pubsub_name: str = "todo-pubsub"):
        """
        Initialize the event publisher

        Args:
            pubsub_name: Name of the Dapr pubsub component to use
        """
        self.pubsub_name = pubsub_name
        self.client = DaprClient()

    def publish_event(
        self,
        event_type: EventType,
        data: Dict[str, Any],
        topic: str = "task-events"
    ) -> bool:
        """
        Publish an event to the specified topic

        Args:
            event_type: Type of the event
            data: Event payload data
            topic: Topic to publish the event to

        Returns:
            bool: True if published successfully, False otherwise
        """
        try:
            # Create the event payload
            event_payload = {
                "event_id": str(uuid.uuid4()),
                "event_type": event_type.value,
                "timestamp": datetime.utcnow().isoformat(),
                "data": data
            }

            # Publish the event via Dapr
            self.client.publish_event(
                pubsub_name=self.pubsub_name,
                topic_name=topic,
                data=json.dumps(event_payload),
                data_content_type='application/json'
            )

            logger.info(f"Event published: {event_type.value} to topic {topic}")
            return True

        except Exception as e:
            logger.error(f"Failed to publish event {event_type.value}: {str(e)}")
            return False

    def publish_task_created(self, task_id: int, user_id: str, title: str) -> bool:
        """Publish a task created event"""
        data = {
            "task_id": task_id,
            "user_id": user_id,
            "title": title
        }
        return self.publish_event(EventType.TASK_CREATED, data)

    def publish_task_updated(self, task_id: int, user_id: str, changes: Dict[str, Any]) -> bool:
        """Publish a task updated event"""
        data = {
            "task_id": task_id,
            "user_id": user_id,
            "changes": changes
        }
        return self.publish_event(EventType.TASK_UPDATED, data)

    def publish_task_completed(self, task_id: int, user_id: str) -> bool:
        """Publish a task completed event"""
        data = {
            "task_id": task_id,
            "user_id": user_id
        }
        return self.publish_event(EventType.TASK_COMPLETED, data)

    def publish_task_deleted(self, task_id: int, user_id: str) -> bool:
        """Publish a task deleted event"""
        data = {
            "task_id": task_id,
            "user_id": user_id
        }
        return self.publish_event(EventType.TASK_DELETED, data)

    def publish_reminder_scheduled(self, task_id: int, user_id: str, scheduled_time: str, channel: str) -> bool:
        """Publish a reminder scheduled event"""
        data = {
            "task_id": task_id,
            "user_id": user_id,
            "scheduled_time": scheduled_time,
            "channel": channel
        }
        return self.publish_event(EventType.REMINDER_SCHEDULED, data, "reminders")

    def publish_reminder_triggered(self, task_id: int, user_id: str, channel: str) -> bool:
        """Publish a reminder triggered event"""
        data = {
            "task_id": task_id,
            "user_id": user_id,
            "channel": channel
        }
        return self.publish_event(EventType.REMINDER_TRIGGERED, data, "reminders")

    def publish_recurring_task_created(self, parent_task_id: int, new_task_id: int, user_id: str) -> bool:
        """Publish a recurring task created event"""
        data = {
            "parent_task_id": parent_task_id,
            "new_task_id": new_task_id,
            "user_id": user_id
        }
        return self.publish_event(EventType.RECURRING_TASK_CREATED, data)


# Global event publisher instance
# In a real application, you might want to manage this differently
event_publisher = EventPublisher()


def get_event_publisher(pubsub_name: str = "todo-pubsub") -> EventPublisher:
    """
    Get an instance of the event publisher

    Args:
        pubsub_name: Name of the Dapr pubsub component to use

    Returns:
        EventPublisher: An instance of the event publisher
    """
    return EventPublisher(pubsub_name)


# Example usage
if __name__ == "__main__":
    # Example of how to use the event publisher
    publisher = get_event_publisher()

    # Publish a sample task created event
    success = publisher.publish_task_created(
        task_id=123,
        user_id="user456",
        title="Sample Task"
    )

    if success:
        print("Event published successfully!")
    else:
        print("Failed to publish event")