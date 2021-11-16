#Flat para listas


def flat(lst):
    '''
    Convierte una lista con posibles sublistas en
    una lista de un solo nivel
    '''
    flatted=[]
    for el in lst:
        if type(el)==list or isinstance(el,list):
            for item in flat(el):
                flatted.append(item)
        else:
            flatted.append(el)
    return flatted