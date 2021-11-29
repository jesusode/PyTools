#Funciones de utilidad para Streams e Iterators

def  iterConsume(iter,times):
    '''
    Llama a next del iterable times veces.
    '''
    for i in range(times):
        if iter.hasNext() :
            iter.next()
    return iter


def iterToCSV(iter, path, sep="," ,encoding="utf-8", first_line=[]):
    '''
    Convierte lo que sale de un iterable
    en un archivo CSV.
    '''
    f= open(path,"w",encoding)
    if first_line!=[] :
        f.write("\n".join([x.strip() for x in first_line]))
    for line in iter.toList():
        f.write("\n".join([x.strip() for x in line]))
    f.close()
