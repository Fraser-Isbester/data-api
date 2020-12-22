"""
Input:
    - Entity Defintinos
        type: json-schema
    - Access Patterns
        type: json-custom
Output:
    - DynamoDB Specification
"""

def lambda_handler(event, context):

    event = Event(event)


class Event:
    """
    {
        body: {
            entities: [],
            access_patterns: []
        }
    }
    """

    def __init__(self, event):
        self.event = event
        self._validate()

    def _validate(self):
        """Validate event structure"""
        pass
