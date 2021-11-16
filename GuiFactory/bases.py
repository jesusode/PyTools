#Clases baes para GuiFactory

class GUIElementBase:
    '''
    Clase base para GUIElement.
    ---------------------------
    Debe implementar los siguientes campo:
    class_ : public
    name : public
    elements : public
    properties : public
    '''

    def __init__(class_,name,elements,properties):
        raise "Virtual Class. Must be subclassed."


    def render(renderer):
        raise "Virtual Method. Must be implemented."


class GUIElement:
    '''
    Implementación de GUIElement
    ----------------------------
    class_ : public
    name : public
    elements : public
    properties : public
    '''
    
    def __init__(self,class_,name,elements,properties):
        self.class_=class_
        self.name=name
        self.elements=elements
        assert type(self.elements)==list
        self.properties=properties
        assert type(self.properties)==dict


    def __repr__(self):
        return "<<class GUIElement class_ : {0} , name : {1} , elements : {2} , properties : {3} >>".format(self.class_,self.name,self.elements,self.properties)


    def render(self,renderer,render_childs=True):
        parts=[]
        parts.append(renderer.render(self))#render_childs??
        if render_childs==True :
            for item in self.elements:
                parts.append(renderer.render(item))

        return parts


class GUIElementRendererBase:
    '''
    Clase base para GUIElementRenderer
    ----------------------------------
    '''

    def __init__(self):
        raise "Virtual Class. Must be subclassed."

    def render(renderer):
        raise "Virtual Method. Must be implemented."


class EventRendererBase:
    '''
    Clase base para EventRenderer
    -----------------------------
    '''

    def __init__(self):
        raise "Virtual Class. Must be subclassed."

    def render(event_descriptors):
        raise "Virtual Method. Must be implemented."
    
class MenuRendererBase:
    '''
    Clase base para MenuRenderer
    -----------------------------
    '''

    def __init__(self):
        raise "Virtual Class. Must be subclassed."

    def render(event_descriptors):
        raise "Virtual Method. Must be implemented."