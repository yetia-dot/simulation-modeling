def make_message(**kwargs):
    """
    Helper function to create a message dictionary.
    """
    return {
        "type": "match_created",
        "payload": kwargs
    }
