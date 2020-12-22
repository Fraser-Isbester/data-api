"""
Input:
    - Entity Defintinos
    - Access Patterns
Output:
    - DynamoDB Specification
"""

def lambda_handler(event, context):

    event = Event(event)


class Event:

    def __init__(self, event):
        self.event = event
        self._validate()

    def _validate(self):
        """Validate event structure"""
        pass
