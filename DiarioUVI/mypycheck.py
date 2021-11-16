#Usa mypy en runtime para comprobar tipos segun typing.
import mypy.api

#Es lenta!!
def check_type(value, typ):
    '''
    From StackOverflow (of course)
    '''
    program_text = 'from typing import *; v: {} = {}'.format(typ, repr(value))
    normal_report, error_report, exit_code = mypy.api.run(['-c', program_text])
    return exit_code == 0


if __name__ == '__main__':
    int_ = 1
    str_ = 'a'
    list_str_ = ['a']
    list_int_ = [1]
    tuple_int_ = (1,)

    assert check_type(int_, 'int')
    assert not check_type(str_, 'int')
    assert check_type(list_int_, 'List[int]')
    assert not check_type(list_str_, 'List[int]')
    assert check_type(list_int_, 'List[Any]')
    assert check_type(tuple_int_, 'Tuple[int]')
    print("Tessts OK.")