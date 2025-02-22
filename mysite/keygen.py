import random

def generate_random_key(length:int) -> str:
    """Generates an alphanumeric key of the specified length randomly.
    @param: length - the length of the key.
    @returns: the key (str).
    @author: Seth Mallinson"""

    characters:str = "abcdefghijklmnopqrstuvwxyz0123456789"
    key:str = ""
    for i in range(length):
        key += characters[random.randint(0, len(characters)-1)]
    return key