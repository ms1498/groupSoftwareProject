"""A file to store algorithms with inspecific use cases."""

from app.models import Event

def get_event_search_priority(data: list[Event | str | int]) -> int:
    """Get the priority of an event (paired with a user query) for ordering search results.
    The priority passed in is modified in-place.
    
    @param: data - a list containing an event, the user's query (str) and the event's priority.
    @returns: the priority of the event as an integer, from 0-4.
    @author: Seth Mallinson
    """
    event = data[0]
    search_query = data[1]
    # if there is no search query, no ordering needs to be applied by us.
    if not search_query:
        data[2] = 0
        return 0

    society_name = event.organiser.society_name
    # Query is in event name.
    if search_query in event.name.lower():
        data[2] = 0
        return 0
    # Query is in event description.
    if search_query in event.description.lower():
        data[2] = 1
        return 1
    # True if at least one word in the user's query is in the event name.
    if any(query in event.name.lower() for query in search_query.split(" ")):
        data[2] = 2
        return 2
    # Query is in society name.
    if search_query in society_name.lower():
        data[2] = 3
        return 3
    data[2] = 4
    return 4
