import ply.lex as lex

tokens = (
    'NUMBER',
    'DOT',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'COLON',
    'SEMICOLON',
    'CHARACTER',
    'CHAR',
    'WORD',
    'DUP'
)

t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_DOT = r'\.'
t_COLON = r':'
t_SEMICOLON = r';'

def t_CHAR(t):
    r'CHAR'
    return t

def t_DUP(t):
    r'DUP'
    return t

def t_CHARACTER(t):
    r'\b[a-zA-Z]\b'
    return t

def t_WORD(t):
    r'[a-zA-Z_]{2,}'
    return t

def t_NUMBER(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_ignore_COMMENT(t):
    r'\(.*\)|\\.*\n'
    t.lexer.lineno += t.value.count('\n')
    
t_ignore = ' \t'

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
        
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

lexer = lex.lex()