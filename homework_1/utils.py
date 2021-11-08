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


def test(func):
    def func_with_name_and_docstring(*args, **kwargs):
        print("\n")
        print(f"{terminal.BOLD} => {func.__name__} {terminal.END}")
        print(f"{terminal.DARKCYAN}{func.__doc__}{terminal.END}")
        func(*args, **kwargs)

    return func_with_name_and_docstring