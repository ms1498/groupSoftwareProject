"""A file to store algorithms with inspecific use cases."""


def quicksort(input: list[tuple[any, int]]) -> list[any]:
    """Sorts a list of items with priorities by priority, and returns a list of just the items.
    
    @param: input - a list of tuples of items and priorities.
    @returns: a list of sorted items.
    @author: Seth Mallinson
    """
    if len(input) <= 1:
        return input
    pivot = input[0]
    left = [element for element in input[1:] if element[1] <= pivot[1]]
    right = [element for element in input[1:] if element[1] > pivot[1]]
    return quicksort(left) + [pivot[1]] + quicksort(right)