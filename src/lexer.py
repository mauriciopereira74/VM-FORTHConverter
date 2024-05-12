# pylint: disable=invalid-name
import ply.lex as lex

literals = ('.',':',';')

tokens = (
    "NUMBER",
    "OPERATORS",
    "MOD",
    "DUP",
    "BASIC",
    "SWAP",
    "DROP",
    "OVER",
    "ROT",
    "DOT",
    "EMIT",
    "CHAR",
    "SPACES",
    "CR",
    "IF",
    "THEN",
    "ELSE",
    "DO",
    "LOOP",
    "ITERATOR",
    "STRING"
)

def t_MOD(t):
    r'\bMOD\b'
    return t

def t_ITERATOR(t):
    r'\bI\b|J\b'
    return t

def t_DO(t):
    r'\bDO\b'
    return t

def t_LOOP(t):
    r'\bLOOP\b'
    return t

def t_IF(t):
    r'\bIF\b'
    return t

def t_THEN(t):
    r'\bTHEN\b'
    return t

def t_ELSE(t):
    r'\bELSE\b'
    return t

def t_ROT(t):
    r'\bROT\b'
    return t

def t_OVER(t):
    r'\bOVER\b'
    return t

def t_OPERATORS(t):
    r"\+|\-|\*|\/|<=?|>=?|="
    return t

def t_DROP(t):
    r'\bDROP\b'
    return t

def t_DUP(t):
    r'\bDUP\b'
    return t

def t_BASIC(t):
    r"\b1\+|1\-|2\*|2\/\b"
    return t

def t_SWAP(t):
    r'\bSWAP\b'
    return t

def t_NUMBER(t):
    r'\b\d+\b'
    return t

def t_DOT(t):
    r'\." .*?"'
    return t

def t_EMIT(t):
    r'\bEMIT\b'
    return t

def t_CHAR(t):
    r"\bCHAR(\s[^\s]*)?"
    return t

def t_SPACES(t):
    r"\bSPACES\b"
    return t

def t_CR(t):
    r'\bCR\b'
    return t

def t_STRING(t):
    r'\b[A-Za-z\d]+\b'
    return t
def t_ignore_COMMENT(t):
    r'\(.*?\)|\\[^\n]*'
    t.lexer.lineno += t.value.count('\n')

def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

t_ignore = " \t\n"

lexer = lex.lex()
