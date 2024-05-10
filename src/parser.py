import ply.yacc as yacc
from lexer import tokens
from func import Function

globalPointer = 0
globalPointerAuxiliar = 0
globalPointerWhile = 0

def p_statement(p):
    'statement : expressions'
    global globalPointer
    parser.codeAux += p[1]
    parser.code = "pushi 0\n" * globalPointer
    parser.code += "start\n" + parser.codeAux + "stop\n"
    for key,value in parser.functions.items():
        parser.code += "\n" + key + ":\n"
        for i in range(1,value.requiredFromStack+1):
            parser.code += "pushfp\n" + "load " + str(-value.requiredFromStack-1+i) + "\n"
        for elem in value.funcDefinition:
            parser.code += elem + "\n"
        for i in range(value.globalPosition,value.globalPosition+value.outToStack)[::-1]:
            parser.code += f"storeg {i}\n"
        parser.code += "return\n"
    return p

def p_expressions(p):
    """
    expressions : expressions word
                | word
    """
    if len(p)==2:
        p[0] = p[1]
    else:
        p[0] = p[1] + p[2]
    return p

def p_word(p):
    """
    word    : function
            | operator
            | function_definition
    """
    p[0] = p[1]
    return p

def p_function(p):
    'function  : STRING'
    global globalPointer
    if (p[1] in parser.functions):
        if(not haveOperands(parser.functions[p[1]].requiredFromStack,parser.functions[p[1]].outToStack)):
            print(f"Função {p[1]} não encontra elementos suficientes na stack!",parser.lineNumber)
        if parser.functions[p[1]].requiredFromStack < 1:
            p[0] = f'pusha {p[1]}\ncall\n'
        else:
            p[0] = f"pusha {p[1]}\ncall\npop {parser.functions[p[1]].requiredFromStack}\n"
        for i in range(parser.functions[p[1]].globalPosition,parser.functions[p[1]].globalPosition+parser.functions[p[1]].outToStack):
            p[0] += f'pushg {i}\n'
    else:
        print(f"Função {p[1]} não está definida!",parser.lineNumber)
    return p

def p_function_definition(p):
    'function_definition : ":" STRING operators ";"'
    if(p[2] not in parser.functions): #Se a função ainda não estiver definida
        global globalPointer
        operators = []
        spi = p[3][0].requiredFromStack
        spa = spi
        spo = 0
        for elem in p[3]: # [2,1,bool,bool,vm]
            if elem.requiredFromStack > spa:
                spi += elem.requiredFromStack - spa
                spa += elem.requiredFromStack - spa
            spo += elem.requiredFromStack - elem.outToStack
            spa += (elem.outToStack - elem.requiredFromStack)
            operators.append(elem.funcDefinition)
        spo = spi - spo
        parser.functions[p[2]] = Function(spi,spo,operators,globalPointer)
        globalPointer += spo
        p[0] = ""
    return p

def p_operator(p):
    """
    operator    : aritmetic
                | dot
                | oneOne
                | swap
                | drop
                | dup
                | over
                | rot
                | print
                | number
                | condition
    """
    global globalPointerWhile

    if not haveOperands(p[1].requiredFromStack,p[1].outToStack):
        print("Operação \"" + p[1].funcName + "\" não encontra elementos suficientes na stack!",parser.lineNumber)
    p[0] = p[1].funcDefinition + "\n" #Apenas interessa o campo com o vm_code
    return p

def p_operator_do(p):
    'operator   : do'
    global globalPointerWhile
    globalPointerWhile += 2*parser.cyclesglobal
    parser.cyclesglobal = 0
    if(parser.iteratorflag):
        print(f"Operação \"J\" não encontra iterador externo!",parser.lineNumber)

    if not haveOperands(p[1].requiredFromStack,p[1].outToStack):
        print("Operação \"" + p[1].funcName + "\" não encontra elementos suficientes na stack!",parser.lineNumber)

    p[0] = p[1].funcDefinition + "\n" #Apenas interessa o campo com o vm_code
    return p

def p_operators_rec(p):
    """
    operators   : operators aritmetic
                | operators dot
                | operators oneOne
                | operators swap
                | operators drop
                | operators dup
                | operators over
                | operators rot
                | operators print
                | operators number
                | operators condition
    """

    p[0] = p[1] + [p[2]]
    return p

def p_operators_rec_do(p):
    'operators   : operators do'

    global globalPointerWhile
    globalPointerWhile += 2*parser.cyclesglobal
    parser.cyclesglobal = 0
    if(parser.iteratorflag):
        print(f"Operação \"J\" não encontra iterador externo!",parser.lineNumber)

    p[0] = p[1] + [p[2]]
    return p

def p_operators(p):
    """
    operators   : aritmetic
                | dot
                | oneOne
                | swap
                | drop
                | dup
                | over
                | rot
                | print
                | number
                | condition
    """
    p[0] = [p[1]]
    return p

def p_operators_do(p):
    'operators  : do'

    global globalPointerWhile
    globalPointerWhile += 2*parser.cyclesglobal
    parser.cyclesglobal = 0
    if(parser.iteratorflag):
        print(f"Operação \"J\" não encontra iterador externo!",parser.lineNumber)

    p[0] = [p[1]]
    return p

def p_aritmetic(p):
    """
    aritmetic   : OPERATORS
                | MOD
    """
    if   p[1] == '+':
        vm_code = 'add'
    elif p[1] == '-':
        vm_code = 'sub'
    elif p[1] == '*':
        vm_code = 'mul'
    elif p[1] == '/':
        vm_code = 'div'
    elif p[1] == '>':
        vm_code = 'sup'
    elif p[1] == '>=':
        vm_code = 'supeq'
    elif p[1] == '<':
        vm_code = 'inf'
    elif p[1] == '<=':
        vm_code = 'infeq'
    elif p[1] == '=':
        vm_code = 'equal'
    else:
        vm_code = 'mod'
    p[0] = Function(2,1,vm_code,funcName=p[1])
    return p

def p_print_string(p):
    "print : DOT"
    if p[1][2] != " ":
        print("Missing space after print string opening",parser.lineNumber)

    # [3:-1:] -> contéudo da string
    # [start:stop:]
    vm_code = f'pushs "{p[1][3:-1:]}"\nwrites'
    p[0] = Function(0,0,vm_code)
    return p

def p_print_emit(p):
    "print : EMIT"
    vm_code = "writechr"
    p[0] = Function(1,0,vm_code,funcName=p[1])
    return p

def p_print_char(p):
    "print : CHAR"
    args = p[1].split()
    if len(args) == 1:
        print("Missing statement after char function call",parser.lineNumber)
    vm_code = f'pushs "{args[1]}"\nchrcode'
    p[0] = Function(0,1,vm_code)
    return p

def p_print_spaces(p):
    "print : SPACES"
    if p[1][-1].lower() == "s":
        print("Função spaces não implementada",parser.lineNumber)
    vm_code = f'pushs " "\nwrites'
    p[0] = Function(0,0,vm_code)
    return p

def p_print_cr(p):
    "print : CR"
    vm_code = "writeln"
    p[0] = Function(0,0,vm_code)
    return p

def p_res_dup(p):
    'dup    : DUP'
    if p[1].upper() == "DUP":
        vm_code = 'dup 1'
        p[0] = Function(1,2,vm_code,funcName=p[1])
    else:
        vm_code = 'pushsp\nload-1\npushsp\nload-1'
        p[0] = Function(2,4,vm_code,funcName=p[1])
    return p

def p_cond(p):
    'condition   : if'
    p[0] = p[1]
    return p

def p_if1(p):
    'if     : IF operators else'
    vm_code = f"jz else{parser.ifcount}\n"
    (spi,spo,vm_code) = defineSpiSpo(p[2],vm_code)
    vm_code += f"jump endif{parser.ifcount}\n" + p[3].funcDefinition
    if(spo-spi == p[3].outToStack-p[3].requiredFromStack):
        p[0] = Function(max(spi,p[3].requiredFromStack)+1,spo,vm_code,funcName="Condicional")
    else:
        print("Numero de elementos na stack após Condicional difere nas duas condições!",parser.lineNumber)
        if(spo-spi < p[3].outToStack-p[3].requiredFromStack):
            p[0] = Function(max(spi,p[3].requiredFromStack)+1,spo,vm_code,funcName="Condicional")
        else:
            p[0] = Function(max(spi,p[3].requiredFromStack)+1,p[3].outToStack,vm_code,funcName="Condicional")
    parser.ifcount += 1
    return p

def p_if2(p):
    'if     : IF else'
    if (p[2].outToStack-p[2].requiredFromStack < 0):
        print("Numero de elementos na stack após Condicional difere nas duas condições!",parser.lineNumber)
    vm_code = f"jz else{parser.ifcount}\n" + f"jump endif{parser.ifcount}\n" + p[2].funcDefinition
    p[0] = Function(p[2].requiredFromStack,p[2].outToStack,vm_code,funcName="Condicional")
    parser.ifcount += 1
    return p

def p_if3(p):
    'if     : IF operators THEN'
    vm_code = f"jz endif{parser.ifcount}\n"
    (spi,spo,vm_code) = defineSpiSpo(p[2],vm_code)
    vm_code += f"endif{parser.ifcount}:"
    if(spo<spi):
        print("Numero de elementos na stack após Condicional difere nas duas condições!",parser.lineNumber)
    if(spo-spi<0):
        p[0] = Function(spi+1,spo,vm_code,funcName="Condicional")
    else:
        p[0] = Function(spi+1,0,vm_code,funcName="Condicional")
    parser.ifcount += 1
    return p
def p_if4(p):
    'if     : IF THEN'
    p[0] = Function(0,0,"",funcName="Condicional")
    return p

def p_else1(p):
    'else     : ELSE operators THEN'
    vm_code = f"else{parser.ifcount}:\n"
    (spi,spo,vm_code) = defineSpiSpo(p[2],vm_code)
    vm_code += f"endif{parser.ifcount}:"
    p[0] = Function(spi,spo,vm_code,funcName="Condicional")
    return p
def p_else2(p):
    'else     : ELSE THEN'
    p[0] = Function(0,0,f"else{parser.ifcount}:\nendif{parser.ifcount}:",funcName="Condicional")
    return p


def p_iterator(p):
    """
    Iterator  : ITERATOR
    """
    global globalPointerWhile
    if p[1].upper() == 'I':
        p[0] = Function(0,1,f"pushg {globalPointerWhile}",funcName="Iterador Interno")
    else:
        p[0] = Function(0,1,None,funcName="Iterador Externo")
    return p

def p_do_operators(p):
    """
    do_operators    : do_operators aritmetic
                    | do_operators dot
                    | do_operators oneOne
                    | do_operators swap
                    | do_operators drop
                    | do_operators dup
                    | do_operators over
                    | do_operators rot
                    | do_operators print
                    | do_operators number
                    | do_operators condition
                    | do_operators do
                    | do_operators Iterator
    """
    global globalPointerWhile
    if(p[2].funcName == "DO LOOP"):
        parser.iteratorflag = False
    p[0] = p[1] + [p[2]]
    return p

def p_do_ops1(p):
    """
    do_operators    : aritmetic
                    | dot
                    | oneOne
                    | swap
                    | drop
                    | dup
                    | over
                    | rot
                    | print
                    | number
                    | condition
                    | do
                    | Iterator
    """
    global globalPointerWhile
    if(p[1].funcName == "DO LOOP"):
        parser.iteratorflag = False
    p[0] = [p[1]]
    return p

def p_do_while(p):
    'do       : DO do_operators LOOP'
    global globalPointer
    global globalPointerWhile
    parser.whilecount += 1
    parser.cyclesglobal += 2
    if(globalPointerWhile == 0):
        globalPointer += 2
    else:
        globalPointerWhile -=2
    vm_code = f"storeg {parser.cyclesglobal-2}\nstoreg {parser.cyclesglobal-1}\nwhile{parser.whilecount}:\npushg {parser.cyclesglobal-1}\npushg {parser.cyclesglobal-2}\nsub\njz endwhile{parser.whilecount}\n"
    spi = p[2][0].requiredFromStack
    spa = spi
    spo = 0
    for elem in p[2]:
        if elem.requiredFromStack > spa:
            spi += elem.requiredFromStack - spa
            spa += elem.requiredFromStack - spa
        spo += elem.requiredFromStack - elem.outToStack
        spa += (elem.outToStack - elem.requiredFromStack)
        if(elem.funcName == "Iterador Externo"):
            elem.funcDefinition = f"pushg {parser.cyclesglobal}"
            parser.iteratorflag = True
        elif(elem.funcName == "Iterador Interno"):
            elem.funcDefinition = f"pushg {parser.cyclesglobal-2}"
        vm_code += elem.funcDefinition + "\n"

    spo = spi - spo
    vm_code += f"pushg {parser.cyclesglobal-2}\npushi 1\nadd\nstoreg {parser.cyclesglobal-2}"
    vm_code += f"\njump while{parser.whilecount}\nendwhile{parser.whilecount}:"
    p[0] = Function(2+spi,spo,vm_code,funcName="DO LOOP")
    return p

def p_one_in_one_out(p):
    """
    oneOne   : ONEONE
    """
    if   p[1] == '1+':
        vm_code = 'pushi 1\nadd'
    elif p[1] == '1-':
        vm_code = 'pushi 1\nsub'
    elif p[1] == '2*':
        vm_code = 'pushi 2\nmul'
    elif p[1] == '2/':
        vm_code = 'pushi 2\ndiv'
    p[0] = Function(1,1,vm_code,funcName=p[1])
    return p

def p_drop(p):
    'drop : DROP'
    if p[1].upper() == "DROP":
        vm_code = 'pop 1'
        p[0] = Function(1,0,vm_code,funcName=p[1])
    else:
        vm_code = 'pop 2'
        p[0] = Function(2,0,vm_code,funcName=p[1])
    return p

def p_rot(p):
    'rot : ROT'
    global globalPointer
    global globalPointerAuxiliar
    if p[1].upper() == "ROT":
        if globalPointerAuxiliar < 1:
            globalPointer += 1
            globalPointerAuxiliar = 1
        vm_code = f'storeg 0\nswap\npushg 0\nswap'
        p[0] = Function(3,3,vm_code,funcName=p[1])
    return p

def p_swap(p):
    'swap : SWAP'
    global globalPointer
    global globalPointerAuxiliar
    if p[1].upper() == "SWAP":
        if globalPointerAuxiliar < 1:
            vm_code = 'swap'
            p[0] = Function(2,2,vm_code,funcName=p[1])
    else:
        if globalPointerAuxiliar < 2:
            globalPointer += 2-globalPointerAuxiliar
            globalPointerAuxiliar = 2
        vm_code = "storeg 0\nstoreg 1\nswap\npushg 0\npushg 1"
        p[0] = Function(4,4,vm_code,funcName=p[1])
    return p

def p_over(p):
    'over : OVER'
    if p[1].upper() == "OVER":
        vm_code = 'pushsp\nload-1'
        p[0] = Function(2,3,vm_code,funcName=p[1])
    else:
        vm_code = 'pushsp\nload-3\npushsp\nload-3'
        p[0] = Function(4,6,vm_code,funcName=p[1])
    return p

def p_res_print(p):
    'dot     : "."'
    p[0] = Function(1,0,"writei",funcName=p[1])
    return p

def p_termo(p):
    'number   : NUMBER'
    p[0] = Function(0,1,f"pushi {p[1]}")
    return p

def haveOperands(n,m):
    "n = nr de elementos necessarios na stack, m = nr de elementos a remover da stack"
    out = True
    if(parser.sp<n):
        out = False
    else:
        parser.sp += m
        parser.sp -= n
    return out
def defineSpiSpo(func,vm_code):
    spi = func[0].requiredFromStack
    spa = spi
    spo = 0
    for elem in func:
        if elem.requiredFromStack > spa:
            spi += elem.requiredFromStack - spa
            spa += elem.requiredFromStack - spa
        spo += elem.requiredFromStack - elem.outToStack
        spa += (elem.outToStack - elem.requiredFromStack)
        vm_code += elem.funcDefinition + "\n"
    spo = spi - spo
    return(spi,spo,vm_code)


def p_error(p):
    print('Erro Sintático!',p)
    parser.exito = False

parser = yacc.yacc()
parser.exito = True
parser.sp = 0
parser.functions = {}
parser.error = None
parser.code = ""
parser.codeAux = ""
parser.lineNumber = 1
parser.ifcount = 0
parser.whilecount = 0
parser.iteratorflag = False
parser.cyclesglobal = 0
