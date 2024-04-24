import ply.lex as lex

"""
17 34 23
.
2 3 + .
2 3 + 10 + .
30 5 - . ( 25=30-5 )
30 5 / . ( 6=30/5 )
30 5 * . ( 150=30*5 )
30 5 + 7 / . \ 5=(30+5)/7
"""

tokens = (
    'NUMBER',
    'DOT',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'LPAREN',
    'RPAREN',
    'BACKSLASH',
    'EQUALS',
)

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_BACKSLASH = r'\\'
t_EQUALS = r'='
t_DOT = r'\.'


def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()