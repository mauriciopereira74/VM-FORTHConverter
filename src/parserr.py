import ply.yacc as yacc
from lexer import tokens


# EXEMPLO INIFX_STATEMENT (12 * ( 20 - 17 )) fica pushi 20 pushi 17 sub pushi 12 mul

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE'),
    ('nonassoc', 'LPAREN', 'RPAREN')
)

operations = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV'}

def p_expression_statements(p):
    """
    expression : statement
               | expression statement
               | infix_expression
               | statement LPAREN comment RPAREN
               | expression statement LPAREN comment RPAREN
               | statement BACKSLASH comment
               | expression statement BACKSLASH comment
    """
    if len(p) == 2:
        p[0] = p[1]
    elif len(p) == 3:
        p[0] = p[1] + p[2]
    elif len(p) == 5 and p[2] == '(':
        p[0] = p[1] + p[3]
    elif len(p) == 6 and p[3] == '(':
        p[0] = p[1] + p[2] + p[4]
    elif len(p) == 4 and p[2] == '\\':
        p[0] = p[1] + p[3]
    else: # len(p) == 5 and p[3] == '\\':
        p[0] = p[1] + p[2] + p[4]

def p_infix_expression(p):
    """
    infix_expression : LPAREN infix_expression RPAREN
                     | NUMBER
                     | infix_expression PLUS infix_expression
                     | infix_expression MINUS infix_expression
                     | infix_expression TIMES infix_expression
                     | infix_expression DIVIDE infix_expression
    """
    
    if len(p) == 2:
        p[0] = f'PUSHI {p[1]}\n'
    elif len(p) == 4 and p[1] == '(':
        p[0] = p[2]
    else: 
        p[0] = p[1] + p[3] + operations[p[2]] + '\n'
    print("Infix expression: ", p[0])

def p_statement_number(p):
    'statement : NUMBER'
    p[0] = f'PUSHI {p[1]}\n'

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

def p_comment(p):
    """
    comment : NUMBER EQUALS comment
            | infix_expression
    """
    p[0] = ''


def p_error(p):
    print("Syntax error at token", p.type, "with value", p.value)

parser = yacc.yacc()
