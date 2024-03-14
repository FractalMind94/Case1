import functools


def print_decorator(name='unknown'):
    def add_function(function):
        @functools.wraps(function)
        def decorator(*args, **kwargs):
            print()
            print(f'--------------------------')
            print(f'{name}:')
            return_values = function(*args, **kwargs)
            print(f'--------------------------')
            print()
            return return_values
        return decorator
    return add_function


@print_decorator('Test logging')
def test_logging():
    def log_decorator(function):
        log_path = r"./log2.txt"

        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            with open(log_path, mode='a') as logger:
                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={repr(v)}" for k, v in kwargs.items()]
                signature = ", ".join(args_repr + kwargs_repr)

                logger.write(f'{function.__name__}({signature})')
                try:
                    value = function(*args, **kwargs)
                    logger.write(f' returned {repr(value)}\n')
                except Exception as exception:
                    logger.write(f' \tERROR: {exception}\n')
                    raise exception

                return value

        return wrapper

    @log_decorator
    def test_function(*args):
        print('this is test function')
        val = 1
        for arg in args:
            val += arg
        return val

    try:
        test_function(1, 2, 3, 1)
        test_function(1, 7, 3, 6)
        test_function(1, 2, 3, 4)
        test_function(1, 2, 3, "a")
    except Exception as e:
        print(e)


@print_decorator('Test __str__')
def test_to_string():

    class A:
        def __init__(self):
            self.a = 'val a'
            self.b = 'val b'

        def __str__(self):
            return f'a: {self.a}, b: {self.b}'

    class B:
        def __init__(self):
            self.a = 'val a'
            self.b = 'val b'

    a = A()
    b = B()
    print('a')
    print(a)
    print(repr(A))
    print()
    print('b')
    print(b)
    print(repr(B))


@print_decorator('test_dict_list_empty')
def test_dict_list_empty():
    a = dict()
    b = list()
    if a:
        print('a not false')
    else:
        print('a is false')

    if b:
        print('b not false')
    else:
        print('b is false')

    a['v'] = 'a'
    b.append('b')
    if a:
        print('a not false')
    else:
        print('a is false')

    if b:
        print('b not false')
    else:
        print('b is false')

@print_decorator('test type')
def test_type():
    a = list()
    b = 'value'
    print(type(a) is list)
    print(type(b) is list)

@print_decorator('for dict')
def test_dict():
    a = {'a':'1', 'b': '2'}
    for k, v in a.items():
        print(f'{k} {v}')

@print_decorator('list comprehension')
def test_comprehension():
    def a(nu):
        n = 0
        while n< nu:
            yield n
            n += 1

    b = a(10)
    c = [bv for bv in b]
    print(c)



if __name__ == '__main__':

    a = '1'
    b = 1

    if not '':
        print('Empty is false')
    else:
        print('empty is not false')

    c = None
    d = str(c)
    print(c)
    print(d)

    c = ''
    d = str(c)
    print(c)
    print(d)


    b = [1, 1, 1, 1, 1, 1]
    for count, v in enumerate(b):
        print(count)

    test_logging()

    test_to_string()

    test_dict_list_empty()

    test_type()

    test_dict()

    test_comprehension()

    print('End')
