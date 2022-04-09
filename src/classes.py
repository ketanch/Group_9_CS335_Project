class Node:
    def __init__(self,name='',value='',type='',ast_node='',children=[],idName=''):
        self.name=name
        self.value=value
        self.type=type
        self.ast_node=ast_node
        self.children=[]
        self.idName=idName
        self.place = ""
        self.code = ""
        self.offset = 0