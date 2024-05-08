import ply.yacc as yacc
from lexer import tokens

operations = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}

word_definitions = {}

stack = []


def p_expression(p):
    """
    expression : statement
               | word_def
               | expression statement
               | expression word_def
               | char_expression
               | expression char_expression
    """
    p[0] = ''.join(p[1:])

def p_word_def(p):
    'word_def : COLON WORD expression SEMICOLON'
    word_definitions[p[2]] = p[3]
    p[0] = f'{p[2]} defined.\n'

def p_statement_number(p):
    'statement : NUMBER'
    stack.append(p[1])
    p[0] = f'PUSHI {p[1]}\n'

def p_statement_dup(p):
    'statement : DUP'
    if stack:
        value = stack[-1]
        stack.append(value)
        p[0] = ''
    else:
        print("Error: Cannot DUP, stack is empty")


def p_char_expression(p):
    """
    char_expression : CHAR CHARACTER
    """
    p[0] = f'PUSHI {ord(p[2])}\n'

    
def p_statement_word(p):
    'statement : WORD'
    if p[1] in word_definitions:
        p[0] = word_definitions[p[1]]
    else:
        print(f"Error: Undefined word '{p[1]}'")
        p[0] = ''


def p_statement_operator(p):
    """
    statement : PLUS
              | MINUS
              | TIMES
              | DIVIDE
    """
    if len(stack) < 2:
        print("Error: Insufficient operands for operation")
        p[0] = ''
    else:
        operand2 = stack.pop()
        operand1 = stack.pop()
        if p[1] == 'ADD':
            result = operand1 + operand2
        elif p[1] == 'SUB':
            result = operand1 - operand2
        elif p[1] == 'MUL':
            result = operand1 * operand2
        elif p[1] == 'DIV':
            if operand2 != 0:
                result = operand1 / operand2
            else:
                print("Error: Division by zero")
                p[0] = ''
                return
        stack.append(result)
        p[0] = f'{p[1]}\n'

def p_statement_output(p):
    'statement : DOT'
    p[0] = 'WRITEI\n'


def p_error(p):
    print("Syntax error at token", p.type, "with value", p.value)


parser = yacc.yacc()