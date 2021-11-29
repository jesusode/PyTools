#Clases para crear componentes web renderizables
from typing import *
import io



#Interfaz renderizable
class IRenderizable:
    '''
    Solo un metodo: render
    '''
    def render(self):
        raise Exception("Method render is virtual. Must be implemented.")


class WebElement(IRenderizable):
    '''
    Clase que reporesenta un elemento web, 
    con contenido, estilos y codigo para eventos.
    Es un composite ya que puede tener como contenido
    otros WebElement.
    '''
    def __init__(self,id: str,
                tag: str,contents : List[Union["WebElement",str]],
                properties: Dict[str,str],
                styles: List[Union["StyleElement",str]]):
        self._id = id
        self._tag = tag #Comprobar que sea un tag valido??
        self._contents = contents
        self._properties = properties
        self._styles = styles
        self._buffer = None

    def getContents(self):
        return self._contents

    def getProperties(self):
        return self._properties

    def getStyles(self):
        return self._styles
    
    def render(self):
        print( f"rendering {self._id}...")
        self._buffer = io.StringIO()
        self._buffer.write(f"<{self._tag} id='{self._id}'")
        if self._properties!={}:
            for item in self._properties:
                self._buffer.write(f" {item}='{self._properties[item]}' ")
        self._buffer.write(">\n")
        #styles??
        for elem in self._contents:
            if type(elem) == str:
                self._buffer.write(elem)
            else:
                self._buffer.write(elem.render())
        self._buffer.write(f"</{self._tag}>\n")
        return self._buffer.getvalue()
    
    def __add__(self,other:"WebElement"):
        '''
        La suma mete todo lo del segundo WebElement en el primero.
        '''
        self._contents.extend(other.getContents())
        self._properties.update(other.getProperties())
        self._styles.extend(other.getStyles())
        return self



class StyleElement:
    '''
    Clase que representa un estilo.
    Es un composite ya que puede tener como contenido
    otros StyleElement.
    '''
    pass


if __name__ == '__main__':
    span1 = WebElement("span1","span",["texto 1 para s1","texto2 para s1"],{"class":"cls23","onclick":"{alert('Hola');}"},[])
    span2 = WebElement("span2","span",["texto 1 para s2","texto2 para s2"],{},[])
    div = WebElement("root","div",["Texto del div",span1,span2],{},[])
    div2 = WebElement("inner_div","div",["inner div"],{},[])
    div = div + div2
    print(div.render())

