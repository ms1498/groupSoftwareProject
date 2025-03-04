"""A file to store algorithms with inspecific use cases."""

def quicksort(unsorted_list: list[tuple[any, int]]) -> list[any]:
    """Sorts a list of items with priorities by priority, and returns a list of just the items.
    
    @param: input - a list of tuples of items and priorities.
    @returns: a list of sorted items.
    @author: Seth Mallinson
    """
    if len(unsorted_list) == 0:
        return []
    if len(unsorted_list) == 1:
        return [unsorted_list[0][0]]
    pivot = unsorted_list[0]
    left = [element for element in unsorted_list[1:] if element[1] <= pivot[1]]
    right = [element for element in unsorted_list[1:] if element[1] > pivot[1]]
    return quicksort(left) + [pivot[0]] + quicksort(right)
