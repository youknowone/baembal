import ast
import _ast

import baembal

orig = _ast.AST
        
class ASTType(type):
    def __instancecheck__(self, instance):
        return isinstance(instance, (orig, baembal.unlocated_ast.AST))

class AST(ast.AST, metaclass=ASTType):
    pass
    
ast.AST = AST
