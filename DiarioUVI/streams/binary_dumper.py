from struct import *
from typing import *
import binascii



class BinaryDumper:
    """
    DocString
    """
    def __init__(self, _struct : str):
        '''
        DS
        '''
        self._struct = _struct
    
    def dumpToFile(self,lst,file,offset = 0) -> int:
        """
        Escribe lst en file,
        aplicando la struct definida.
        Devuelve la posicion en la que queda el
        puntero a archivo tras escribir.
        """
        endpoint = offset
        print(f"st_size: {calcsize(self._struct)}")
        with open(file,"ab+") as fhandle:
            for item in lst:
                print(f"item: {item}")
                print(f"endpoint: {endpoint}")
                s= Struct(self._struct)
                packed_data = s.pack(*item)
                print(binascii.hexlify(packed_data))
                fhandle.seek(endpoint)
                endpoint += fhandle.write(packed_data) 
                #endpoint += fhandle.tell()
            fhandle.close()
        return endpoint







if __name__ == '__main__':

    lst = [[b"uno   ",1,1],[b"dos   ",2,2],[b"tres  ",3,3],[b"cuatro",4,4]]
    #lst = [[0.5,1,1],[0.6,2,2],[0.7,3,3],[0.8,4,4]]
    bd = BinaryDumper("6sll")
    #bd = BinaryDumper("fll")
    print("Endpoint: %s" % bd.dumpToFile(lst,"struct_file.bin"))
    size = calcsize("6sll")
    st = Struct("6sll")
    with open("struct_file.bin","rb") as fh:
        while True:
            _read = fh.read(size)
            #print(f"_read: {_read}")
            if _read != b"":
                unpacked = st.unpack(_read)
                print(unpacked)
            else:
                break
        fh.close()

    print("Ok")
