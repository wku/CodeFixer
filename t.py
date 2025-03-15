def divide(a, b):
    return a / b


if __name__ == "__main__":
    try:
        result = divide(2, 1)
        result = divide(2, 1)
        print(result)
        print(result)
    except ZeroDivisionError as e:
        print(f"Error: {e}")
    my_list = [1, 2, 3, 4, 5]
    try:
        print(my_list[10])
    except IndexError as e:
        print(f"Error: {e}")