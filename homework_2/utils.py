import argparse
import logging
import time
from itertools import chain


class terminal:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def flatten(list_of_lists):
    """Flatten an iterable of iterables
    Borrowed straight from itertool recipes: https://docs.python.org/3/library/itertools.html
    """
    return chain.from_iterable(list_of_lists)


def setup_logging():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-log",
        "--loglevel",
        default="warning",
        help="Provide logging level. Example --loglevel debug, default=warning",
    )
    args = parser.parse_args()
    try:
        logging.basicConfig(level=args.loglevel.upper(), format="%(message)s")
    except ValueError:
        print("Loglevel not recognized, proceeding without.")


def test(func):
    def func_with_name_and_docstring(*args, **kwargs):
        print("\n")
        print(f"{terminal.BOLD} => {func.__name__} {terminal.END}")
        print(f"{terminal.DARKCYAN}{func.__doc__}{terminal.END}")
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        print(
            f"\n{terminal.BOLD}Timed: {(end_time - start_time):0.6f} seconds {terminal.END}"
        )

    return func_with_name_and_docstring


def dprint(ddict):
    """Print a defaultdict without the type
    Slightly faster than casting to dict
    """
    print(terminal.PURPLE, end="")
    print(dict.__repr__(ddict))
    print(terminal.END)


def iprint(name, itemset, leading_new_line=False, trailing_new_line=False):
    """Print an itemset"""
    if leading_new_line:
        print("\n")
    print(f"{terminal.UNDERLINE}{name}{terminal.END}", end=": "), dprint(itemset)
    if trailing_new_line:
        print("\n")


# Print iterations progress
def progress(
    iteration,
    total,
    prefix="",
    suffix="",
    decimals=1,
    length=50,
    fill="█",
    printEnd="\r",
):
    """
    Borrowed straight from: https://stackoverflow.com/questions/3173320/text-progress-bar-in-the-console

    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()
