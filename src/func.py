class Node:
    def __init__(self):
        pass

class Function(Node):
    def __init__(self,requiredFromStack,outToStack,funcDefinition,globalPosition = None,globalNeed = None,funcName=None):
        self.requiredFromStack = requiredFromStack
        self.outToStack = outToStack
        self.funcDefinition = funcDefinition
        self.globalPosition = globalPosition
        self.globalNeed = globalNeed
        self.funcName = funcName

