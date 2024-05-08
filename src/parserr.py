import ply.yacc as yacc
from lexer import tokens

operations = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}

word_definitions = {}


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
    p[0] = f'PUSHI {p[1]}\n'

def p_statement_dup(p):
    'statement : DUP'

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
    p[0] = operations[p[1]] + '\n'


def p_statement_output(p):
    'statement : DOT'
    p[0] = 'WRITEI\n'


def p_error(p):
    print("Syntax error at token", p.type, "with value", p.value)


parser = yacc.yacc()