import ply.yacc as yacc
from lexer import tokens

pos = 0
pos_aux = 0
pos_while = 0

class Node:
    def __init__(self):
        pass

class Function(Node):
    def __init__(self,required,out,func,pos = None):
        self.required = required
        self.out = out
        self.func = func
        self.pos = pos


def in_out_consume(func,vm_code):
    in_consume = func[0].required
    aux = in_consume
    out_consume = 0
    for elem in func:
        if elem.required > aux:
            in_consume += elem.required - aux
            aux += elem.required - aux
        out_consume += elem.required - elem.out
        aux += (elem.out - elem.required)
        vm_code += elem.func + "\n"
    out_consume = in_consume - out_consume
    return(in_consume,out_consume,vm_code)

def p_statement(a):
    'statement : expressions'
    global pos
    analyser.op += a[1]
    analyser.operations = "pushi 0\n" * pos
    analyser.operations += "start\n" + analyser.op + "stop\n"
    for key,value in analyser.func_dicionary.items():
        analyser.operations += "\n" + key + ":\n"
        for i in range(1,value.required+1):
            analyser.operations += "pushfp\n" + "load " + str(-value.required-1+i) + "\n"
        for elem in value.func:
            analyser.operations += elem.func + "\n" #elem.func
        for i in range(value.pos,value.pos+value.out)[::-1]:
            analyser.operations += f"storeg {i}\n"
        analyser.operations += "return\n"
    return a

def p_expressions(a):
    """
    expressions : expressions word
                | word
    """
    if len(a)==2:
        a[0] = a[1]
    else:
        a[0] = a[1] + a[2]
    return a

def p_word(a):
    """
    word    : function
            | operator
            | function_definition
    """
    a[0] = a[1]
    return a

def p_function(a):
    'function  : STRING'
    global pos
    if (a[1] in analyser.func_dicionary):
        if analyser.func_dicionary[a[1]].required < 1:
            a[0] = f'pusha {a[1]}\ncall\n'
        else:
            a[0] = f"pusha {a[1]}\ncall\npop {analyser.func_dicionary[a[1]].required}\n"
        for i in range(analyser.func_dicionary[a[1]].pos,analyser.func_dicionary[a[1]].pos+analyser.func_dicionary[a[1]].out):
            a[0] += f'pushg {i}\n'
    else:
        print(f"Função {a[1]} não está definida!",analyser.lNumb)
    return a

def p_function_definition(a):
    'function_definition : ":" STRING operators ";"'
    if(a[2] not in analyser.func_dicionary): #Se a função ainda não estiver definida
        global pos
        operators = []
        for elem in a[3]: # [2,1,bool,bool,vm]
            operators.append(elem)
        analyser.func_dicionary[a[2]] = Function(1,1,operators,pos)
        pos += 1
        a[0] = ""
    return a

def p_operator(a):
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
    global pos_while
    a[0] = a[1].func + "\n" #Apenas interessa o campo com o vm_code
    return a

def p_operator_do(a):
    'operator   : do'
    global pos_while
    pos_while += 2*analyser.cycle
    analyser.cycle = 0
    if(analyser.flag):
        print(f"Operação \"J\" não encontra iterador externo!",analyser.lNumb)
    a[0] = a[1].func + "\n" #Apenas interessa o campo com o vm_code
    return a

def p_operators_rec(a):
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
    a[0] = a[1] + [a[2]]
    return a



def p_operators(a):
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
    a[0] = [a[1]]
    return a



def p_aritmetic(a):
    """
    aritmetic   : OPERATORS
                | MOD
    """
    if   a[1] == '+':
        vm_code = 'add'
    elif a[1] == '-':
        vm_code = 'sub'
    elif a[1] == '*':
        vm_code = 'mul'
    elif a[1] == '/':
        vm_code = 'div'
    elif a[1] == '>':
        vm_code = 'sup'
    elif a[1] == '>=':
        vm_code = 'supeq'
    elif a[1] == '<':
        vm_code = 'inf'
    elif a[1] == '<=':
        vm_code = 'infeq'
    elif a[1] == '=':
        vm_code = 'equal'
    else:
        vm_code = 'mod'
    a[0] = Function(2,1,vm_code)
    return a

def p_single_operations(a):
    """
    oneOne   : ONEONE
    """
    if   a[1] == '1+':
        vm_code = 'pushi 1\nadd'
    elif a[1] == '1-':
        vm_code = 'pushi 1\nsub'
    elif a[1] == '2*':
        vm_code = 'pushi 2\nmul'
    elif a[1] == '2/':
        vm_code = 'pushi 2\ndiv'
    a[0] = Function(1,1,vm_code)
    return a


def p_dup(a):
    'dup    : DUP'
    if a[1].upper() == "DUP":
        vm_code = 'dup 1'
        a[0] = Function(1,2,vm_code)
    else:
        vm_code = 'pushsp\nload-1\npushsp\nload-1'
        a[0] = Function(2,4,vm_code)
    return a

def p_condition(a):
    'condition   : if'
    a[0] = a[1]
    return a


def p_pop(a):
    'drop : DROP'
    if a[1].upper() == "DROP":
        vm_code = 'pop 1'
        a[0] = Function(1,0,vm_code)
    else:
        vm_code = 'pop 2'
        a[0] = Function(2,0,vm_code)
    return a

def p_rot(a):
    'rot : ROT'
    global pos
    global pos_aux
    if a[1].upper() == "ROT":
        if pos_aux < 1:
            pos += 1
            pos_aux = 1
        vm_code = f'storeg 0\nswap\npushg 0\nswap'
        a[0] = Function(3,3,vm_code)
    return a

def p_swap(a):
    'swap : SWAP'
    global pos
    global pos_aux
    if a[1].upper() == "SWAP":
        if pos_aux < 1:
            vm_code = 'swap'
            a[0] = Function(2,2,vm_code)
    else:
        if pos_aux < 2:
            pos += 2-pos_aux
            pos_aux = 2
        vm_code = "storeg 0\nstoreg 1\nswap\npushg 0\npushg 1"
        a[0] = Function(4,4,vm_code)
    return a

def p_over(a):
    'over : OVER'
    if a[1].upper() == "OVER":
        vm_code = 'pushsp\nload-1'
        a[0] = Function(2,3,vm_code)
    else:
        vm_code = 'pushsp\nload-3\npushsp\nload-3'
        a[0] = Function(4,6,vm_code)
    return a

def p_number(a):
    'number   : NUMBER'
    a[0] = Function(1,0,f"pushi {a[1]}")
    return a

def p_if_op_else(a):
    'if     : IF operators else'
    vm_code = f"jz else{analyser.numbIf}\n"
    (in_consume,out_consume,vm_code) = in_out_consume(a[2],vm_code)
    vm_code += f"jump endif{analyser.numbIf}\n" + a[3].func
    if(out_consume-in_consume == a[3].out-a[3].required):
        a[0] = vm_code
    else:
        print("Numero de elementos na stack após Condicional difere nas duas condições!",analyser.lNumb)
        if(out_consume-in_consume < a[3].out-a[3].required):
            a[0] = Function(in_consume,a[3].required,vm_code)
        else:
            a[0] = Function(in_consume,a[3].required,vm_code)
    analyser.numbIf += 1
    return a

def p_if_else(a):
    'if     : IF else'
    if (a[2].out-a[2].required < 0):
        print("Numero de elementos na stack após Condicional difere nas duas condições!",analyser.lNumb)
    vm_code = f"jz else{analyser.numbIf}\n" + f"jump endif{analyser.numbIf}\n" + a[2].func
    a[0] = Function(a[2].required,a[2].out,vm_code)
    analyser.numbIf += 1
    return a

def p_if_op_then(a):
    'if     : IF operators THEN'
    vm_code = f"jz endif{analyser.numbIf}\n"
    (in_consume,out_consume,vm_code) = in_out_consume(a[2],vm_code)
    vm_code += f"endif{analyser.numbIf}:"
    if(out_consume<in_consume):
        print("Numero de elementos na stack após Condicional difere nas duas condições!",analyser.lNumb)
    if(out_consume-in_consume<0):
        a[0] = Function(in_consume+1,out_consume,vm_code)
    else:
        a[0] = Function(in_consume+1,out_consume,vm_code)
    analyser.numbIf += 1
    return a
def p_if_then(a):
    'if     : IF THEN'
    a[0] = Function(0,0,"")
    return a

def p_else_op_then(a):
    'else     : ELSE operators THEN'
    vm_code = f"else{analyser.numbIf}:\n"
    (in_consume,out_consume,vm_code) = in_out_consume(a[2],vm_code)
    vm_code += f"endif{analyser.numbIf}:"
    a[0] = Function(in_consume,out_consume,vm_code)
    return a
def p_else_then(a):
    'else     : ELSE THEN'
    a[0] = Function(0,0,f"else{analyser.numbIf}:\nendif{analyser.numbIf}:")
    return a


def p_it(a):
    """
    Iterator  : ITERATOR
    """
    global pos_while
    if a[1].upper() == 'I':
        a[0] = Function(0,0,f"pushg {pos_while}")
    else:
        a[0] = Function(0,0,None)
    return a

def p_operators_do(a):
    'operators  : do'

    global pos_while
    pos_while += 2*analyser.cycle
    analyser.cycle = 0
    if(analyser.flag):
        print(f"Operação \"J\" não encontra iterador externo!",analyser.lNumb)

    a[0] = [a[1]]
    return a

def p_operators_rec_do(a):
    'operators   : operators do'

    global pos_while
    pos_while += 2*analyser.cycle
    analyser.cycle = 0
    if(analyser.flag):
        print(f"Operação \"J\" não encontra iterador externo!",analyser.lNumb)

    a[0] = a[1] + [a[2]]
    return a

def p_do_operators(a):
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
    global pos_while
    if(a[2].funcName == "DO LOOP"):
        analyser.flag = False
    a[0] = a[1] + [a[2]]
    return a

def p_do_operators_simple(a):
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
    global pos_while
    if(a[1].funcName == "DO LOOP"):
        analyser.flag = False
    a[0] = [a[1]]
    return a

def p_do_while(a):
    'do       : DO do_operators LOOP'
    global pos
    global pos_while
    analyser.numbWhile += 1
    analyser.cycle += 2
    if(pos_while == 0):
        pos += 2
    else:
        pos_while -=2
    vm_code = f"storeg {analyser.cycle-2}\nstoreg {analyser.cycle-1}\nwhile{analyser.numbWhile}:\npushg {analyser.cycle-1}\npushg {analyser.cycle-2}\nsub\njz endwhile{analyser.numbWhile}\n"
    in_consume = a[2][0].required
    aux = in_consume
    out_consume = 0
    for elem in a[2]:
        if elem.required > aux:
            in_consume += elem.required - aux
            aux += elem.required - aux
        out_consume += elem.required - elem.out
        aux += (elem.out - elem.required)
        if(elem.funcName == "Iterador Externo"):
            elem.func = f"pushg {analyser.cycle}"
            analyser.flag = True
        elif(elem.funcName == "Iterador Interno"):
            elem.func = f"pushg {analyser.cycle-2}"
        vm_code += elem.func + "\n"

    out_consume = in_consume - out_consume
    vm_code += f"pushg {analyser.cycle-2}\npushi 1\nadd\nstoreg {analyser.cycle-2}"
    vm_code += f"\njump while{analyser.numbWhile}\nendwhile{analyser.numbWhile}:"
    a[0] = Function(2+in_consume,out_consume,vm_code)
    return a

def p_strg_print(a):
    "print : DOT"
    if a[1][2] != " ":
        print("Missing space after print string opening",analyser.lNumb)

    # [3:-1:] -> contéudo da string
    # [start:stop:]
    vm_code = f'pushs "{a[1][3:-1:]}"\nwrites'
    a[0] = Function(0,0,vm_code)
    return a

def p_emit_print(a):
    "print : EMIT"
    vm_code = "writechr"
    a[0] = Function(0,0,vm_code)
    return a

def p_char_print(a):
    "print : CHAR"
    args = a[1].split()
    if len(args) == 1:
        print("Missing statement after char function call",analyser.lNumb)
    vm_code = f'pushs "{args[1]}"\nchrcode'
    a[0] = Function(0,1,vm_code)
    return a

def p_space_print(a):
    "print : SPACES"
    if a[1][-1].lower() == "s":
        print("Função spaces não implementada",analyser.lNumb)
    vm_code = f'pushs " "\nwrites'
    a[0] = Function(0,0,vm_code)
    return a

def p_cr_print(a):
    "print : CR"
    vm_code = "writeln"
    a[0] = Function(0,0,vm_code)
    return a

def p_print_res(a):
    'dot     : "."'
    a[0] = Function(1,0,"writei")
    return a
def p_error(a):
    print('Erro Sintático!',a)
    analyser.ext = False

analyser = yacc.yacc()
analyser.func_dicionary = {}
analyser.cycle = 0
analyser.numbIf = 0
analyser.numbWhile = 0
analyser.lNumb = 1
analyser.operations = ""
analyser.op = ""
analyser.flag = False
analyser.ext = True