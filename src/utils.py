"""Set of tools to install xray all-in-one
"""
import os
import random
import shutil
import string


def change_ownership(path: str, user: str) -> None:
    """Changes the ownership of all files inside a ``path`` to a ``user``

    Args:
        path (str): the path 
        user (str): the user
    """
    for root, _, files in os.walk(path):
        for filename in files:
            file_path = os.path.join(root, filename)
            shutil.chown(file_path, user)


def generate_random_email(username_len: int = 8, domain_len: int = 8) -> str:
    """generates a random email

    Args:
        username_len (int, optional): length of ``username`` to generate. Defaults to 8.
        domain_len (int, optional): length of ``domain`` to generate. Defaults to 8.

    Returns:
        str: randomly generate email address based on the provided lengths
    """
    username = "".join(random.choices(string.ascii_lowercase, k=username_len))
    domain = "".join(random.choices(string.ascii_lowercase, k=domain_len))
    email = f"{username}@{domain}.com"
    return email


def generate_random_password(use_upper: bool = True, use_digits: bool = True, password_len: bool = 16) -> str:
    """Generates a random passowrd

    Args:
        use_upper (bool, optional): if True, uppercase letters are used as well (not guaranteed). Defaults to True.
        use_digits (bool, optional): if True, digits are used as well (not guaranteed). Defaults to True.
        password_len (bool, optional): the number of characters in the generated password. Defaults to 16.

    Returns:
        str: a randomly generated password
    """

    chars = string.ascii_lowercase
    if use_upper:
        chars += string.ascii_uppercase
    if use_digits:
        chars += string.digits
    password = ''.join(random.choice(chars) for _ in range(password_len))
    return password
