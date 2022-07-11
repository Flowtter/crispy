import logging

from utils.arguments import args

l = logging.getLogger()

print("Welcome to crispy!")

l.info("Starting the program crispy")

l.debug(f"Arguments: {args}")
