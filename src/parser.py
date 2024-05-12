import ply.yacc as yacc
from lexer import tokens

pos = 0
pos_aux = 0
pos_while = 0
operation_types = {}
class Node:
    def __init__(self):
        pass

class Function(Node):
    def __init__(self,required,out,func,pos=None,type=0):
        self.required = required
        self.out = out
        self.func = func
        self.pos = pos
        self.type = type

def usage():
    operation_types[0] = "Unknow Operation"
    operation_types[1] = "+ USAGE:(<number1> <number2> +)"
    operation_types[2] = "- USAGE:(<number1> <number2> -)"
    operation_types[3] = "* USAGE:(<number1> <number2> *)"
    operation_types[4] = "/ USAGE:(<number1> <number2> /)"
    operation_types[5] = "> USAGE:(<number1> <number2> >)"
    operation_types[6] = ">= USAGE:(<number1> <number2> >=)"
    operation_types[7] = "< USAGE:(<number1> <number2> <)"
    operation_types[8] = "<= USAGE:(<number1> <number2> <=)"
    operation_types[9] = "= USAGE:(<number1> <number2> =)"
    operation_types[10] = "SWAP"
    operation_types[11] = "OVER" # duplica o segundo elemento da stack
    operation_types[12] = "ROT"
    operation_types[13] = "DROP"
    operation_types[14] = "1+"
    operation_types[15] = "1-"
    operation_types[16] = "2*"
    operation_types[17] = "2/"
    operation_types[18] = "DO LOOP"
    operation_types[19] = "I" # Iterador Interno
    operation_types[20] = "J"  # Iterador Interno
    operation_types[21] = "IF´S | ELSE´S | THEN´S"
    operation_types[22] = "DUP"
    operation_types[23] = "EMIT"



def in_out_consume(func,format_vm):
    in_consume = func[0].required
    aux = in_consume
    out_consume = 0
    for elem in func:
        if elem.required > aux:
            in_consume += elem.required - aux
            aux += elem.required - aux
        out_consume += elem.required - elem.out
        aux += (elem.out - elem.required)
        format_vm += elem.func + "\n"
    out_consume = in_consume - out_consume
    return(in_consume,out_consume,format_vm)

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
        if (analyser.counter < analyser.func_dicionary[a[1]].required):
            exit("ERROR: \033[91mFunção \"" + a[1] + "\" não tem elementos suficientes para ser realizada\033[0m")
        else:
            analyser.counter += analyser.func_dicionary[a[1]].out
            analyser.counter -= analyser.func_dicionary[a[1]].required
        if analyser.func_dicionary[a[1]].required < 1:
            a[0] = f'pusha {a[1]}\ncall\n'
        else:
            a[0] = f"pusha {a[1]}\ncall\npop {analyser.func_dicionary[a[1]].required}\n"
        for i in range(analyser.func_dicionary[a[1]].pos,analyser.func_dicionary[a[1]].pos+analyser.func_dicionary[a[1]].out):
            a[0] += f'pushg {i}\n'
    else:
        exit(f"ERROR: \033[91m{a[1]} não existe\033[0m")

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
                | basic
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
    if (analyser.counter < a[1].required):
        exit(f"ERROR: \033[91mA Operação {operation_types[a[1].type]} não tem elementos suficientes para ser realizada\033[0m")
        #pass
    else:
        analyser.counter += a[1].out
        analyser.counter -= a[1].required
    a[0] = a[1].func + "\n" #Apenas interessa o campo com o format_vm
    return a

def p_operator_do(a):
    'operator   : do'
    global pos_while
    pos_while += 2*analyser.cycle
    analyser.cycle = 0
    if(analyser.flag):
        exit(f"ERROR: \033[91mA Operação \"J\" não encontra iterador externo\033[0m")
    if(analyser.counter < a[1].required):
        exit(f"ERROR: \033[91mA Operação {operation_types[a[1].type]} não tem elementos suficientes para ser realizada\033[0m")
    else:
        analyser.counter += a[1].out
        analyser.counter -= a[1].required
    a[0] = a[1].func + "\n" #Apenas interessa o campo com o format_vm
    return a

def p_operators_rec(a):
    """
    operators   : operators aritmetic
                | operators dot
                | operators basic
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
                | basic
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
    global  temp
    temp=0
    if   a[1] == '+':
        format_vm = 'add'
        temp=1
    elif a[1] == '-':
        format_vm = 'sub'
        temp = 2
    elif a[1] == '*':
        format_vm = 'mul'
        temp = 3
    elif a[1] == '/':
        format_vm = 'div'
        temp = 4
    elif a[1] == '>':
        format_vm = 'sup'
        temp = 5
    elif a[1] == '>=':
        format_vm = 'supeq'
        temp = 6
    elif a[1] == '<':
        format_vm = 'inf'
        temp = 7
    elif a[1] == '<=':
        format_vm = 'infeq'
        temp = 8
    elif a[1] == '=':
        format_vm = 'equal'
        temp = 9
    else:
        format_vm = 'mod'
        temp = 10
    a[0] = Function(2,1,format_vm,type=temp)
    return a

def p_single_operations(a):
    """
    basic   : BASIC
    """
    global temp
    temp = 0
    if   a[1] == '1+':
        format_vm = 'pushi 1\nadd'
        temp= 14
    elif a[1] == '1-':
        format_vm = 'pushi 1\nsub'
        temp=15
    elif a[1] == '2*':
        format_vm = 'pushi 2\nmul'
        temp=16
    elif a[1] == '2/':
        format_vm = 'pushi 2\ndiv'
        temp=17
    a[0] = Function(1,1,format_vm,temp)
    return a


def p_dup(a):
    'dup    : DUP'
    format_vm = 'dup 1'
    a[0] = Function(1,2,format_vm,type=22)
    return a

def p_condition(a):
    'condition   : if'
    a[0] = a[1]
    return a


def p_pop(a):
    'drop : DROP'
    format_vm = 'pop 1'
    a[0] = Function(1,0,format_vm,type=13)
    return a

def p_rot(a):
    'rot : ROT'
    global pos
    global pos_aux
    if a[1] == "ROT":
        if pos_aux < 1:
            pos += 1
            pos_aux = 1
        format_vm = f'storeg 0\nswap\npushg 0\nswap'
        a[0] = Function(3,3,format_vm,type=12)
    return a

def p_swap(a):
    'swap : SWAP'
    global pos
    global pos_aux

    if pos_aux < 1:
        format_vm = 'swap'
        a[0] = Function(2,2,format_vm,type=10)
    return a

def p_over(a):
    'over : OVER'
    format_vm = 'pushsp\nload-1'
    a[0] = Function(2,3,format_vm,type=11)
    return a

def p_number(a):
    'number   : NUMBER'
    a[0] = Function(0,1,f"pushi {a[1]}")
    return a

def p_if_op_else(a):
    'if     : IF operators else'
    format_vm = f"jz else{analyser.numbIf}\n"
    (in_consume,out_consume,format_vm) = in_out_consume(a[2],format_vm)
    format_vm += f"jump endif{analyser.numbIf}\n" + a[3].func
    if(out_consume-in_consume == a[3].out-a[3].required):
        a[0] = Function(max(in_consume,a[3].required)+1,out_consume,format_vm,type=21)
    else:
        if(out_consume-in_consume < a[3].out-a[3].required):
            a[0] = Function(max(in_consume,a[3].required)+1,out_consume,format_vm,type=21)
        else:
            a[0] = Function(max(in_consume,a[3].required)+1,out_consume,format_vm,type=21)
    analyser.numbIf += 1
    return a

def p_if_else(a):
    'if     : IF else'
    format_vm = f"jz else{analyser.numbIf}\n" + f"jump endif{analyser.numbIf}\n" + a[2].func
    a[0] = Function(a[2].required,a[2].out,format_vm,type=21)
    analyser.numbIf += 1
    return a

def p_if_op_then(a):
    'if     : IF operators THEN'
    format_vm = f"jz endif{analyser.numbIf}\n"
    (in_consume,out_consume,format_vm) = in_out_consume(a[2],format_vm)
    format_vm += f"endif{analyser.numbIf}:"
    if(out_consume-in_consume<0):
        a[0] = Function(in_consume+1,out_consume,format_vm,type=21)
    else:
        a[0] = Function(in_consume+1,0,format_vm,type=21)
    analyser.numbIf += 1
    return a

def p_if_then(a):
    'if     : IF THEN'
    a[0] = Function(0,0,"",type=21)
    return a

def p_else_op_then(a):
    'else     : ELSE operators THEN'
    format_vm = f"else{analyser.numbIf}:\n"
    (in_consume,out_consume,format_vm) = in_out_consume(a[2],format_vm)
    format_vm += f"endif{analyser.numbIf}:"
    a[0] = Function(in_consume,out_consume,format_vm,type=21)
    return a


def p_else_then(a):
    'else     : ELSE THEN'
    a[0] = Function(0,0,f"else{analyser.numbIf}:\nendif{analyser.numbIf}:",type=21)
    return a


def p_it(a):
    """
    Iterator  : ITERATOR
    """
    global pos_while
    if a[1] == 'I':
        a[0] = Function(0,0,f"pushg {pos_while}",type=19)
    elif a[1] == 'J':
        a[0] = Function(0,0,None,type=20)
    else:
        exit(f"ERROR: \033[91mO iterador deve ser I ou J\033[0m")
    return a

def p_operators_do(a):
    'operators  : do'

    global pos_while
    pos_while += 2*analyser.cycle
    analyser.cycle = 0
    if(analyser.flag):
        exit(f"ERROR: \033[91mA Operação \"J\" não encontra iterador externo\033[0m")

    a[0] = [a[1]]
    return a

def p_operators_rec_do(a):
    'operators   : operators do'

    global pos_while
    pos_while += 2*analyser.cycle
    analyser.cycle = 0
    if(analyser.flag):
        exit(f"ERROR: \033[91mA Operação \"J\" não encontra iterador externo\033[0m")

    a[0] = a[1] + [a[2]]
    return a

def p_do_operators(a):
    """
    do_operators    : do_operators aritmetic
                    | do_operators dot
                    | do_operators basic
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
    if(a[2].type == 18):
        analyser.flag = False
    a[0] = a[1] + [a[2]]
    return a

def p_do_operators_simple(a):
    """
    do_operators    : aritmetic
                    | dot
                    | basic
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
    if(a[1].type == 18):
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
    format_vm = f"storeg {analyser.cycle-2}\nstoreg {analyser.cycle-1}\nwhile{analyser.numbWhile}:\npushg {analyser.cycle-1}\npushg {analyser.cycle-2}\nsub\njz endwhile{analyser.numbWhile}\n"
    in_consume = a[2][0].required
    aux = in_consume
    out_consume = 0
    for elem in a[2]:
        if elem.required > aux:
            in_consume += elem.required - aux
            aux += elem.required - aux
        out_consume += elem.required - elem.out
        aux += (elem.out - elem.required)
        if(elem.type == 20):
            elem.func = f"pushg {analyser.cycle}"
            analyser.flag = True
        elif(elem.type == 19):
            elem.func = f"pushg {analyser.cycle-2}"
        format_vm += elem.func + "\n"

    out_consume = in_consume - out_consume
    format_vm += f"pushg {analyser.cycle-2}\npushi 1\nadd\nstoreg {analyser.cycle-2}"
    format_vm += f"\njump while{analyser.numbWhile}\nendwhile{analyser.numbWhile}:"
    a[0] = Function(2+in_consume,out_consume,format_vm, type=18)
    return a

def p_strg_print(a):
    "print : DOT"
    if a[1][2] != " ":
        exit("\033[91mMissing space after print string\033[0m")
    # [3:-1:] -> contéudo da string
    # [start:stop:]
    format_vm = f'pushs "{a[1][3:-1:]}"\nwrites'
    a[0] = Function(0,0,format_vm)
    return a

def p_emit_print(a):
    "print : EMIT"
    format_vm = "writechr"
    a[0] = Function(1,0,format_vm,type=23)
    return a

def p_char_print(a):
    "print : CHAR"
    args = a[1].split()
    if len(args) == 1:
        exit("ERROR: \033[91mWrong Format\033[0m")
    format_vm = f'pushs "{args[1]}"\nchrcode'
    a[0] = Function(0,1,format_vm)
    return a

def p_space_print(a):
    "print : SPACES"
    format_vm = f'pushs " "\nwrites'
    a[0] = Function(0,0,format_vm)
    return a

def p_cr_print(a):
    "print : CR"
    format_vm = "writeln"
    a[0] = Function(0,0,format_vm)
    return a

def p_print_res(a):
    'dot     : "."'
    a[0] = Function(1,0,"writei")
    return a
def p_error(a):
    exit("ERROR: " + f"\033[91mErro Sintático {a}\033[0m")
    analyser.ext = False

analyser = yacc.yacc()
analyser.func_dicionary = {}
analyser.cycle = 0
analyser.numbIf = 0
analyser.numbWhile = 0
analyser.counter = 0
analyser.operations = ""
analyser.op = ""
analyser.flag = False
analyser.ext = True