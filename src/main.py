import json
from lexer import lexer
from parserr import parser


inp = r"""

: DOBRO 2 * ;
2 DOBRO .
: AVERAGE ( a b -- avg ) + 2/ ;
10 20 AVERAGE .

"""

def main():
    lexer.input(inp)
    parsed_dict = parser.parse(inp)
    #print(json.dumps(parsed_dict, indent=2))
    print(parsed_dict)

if __name__ == '__main__':
    main()
