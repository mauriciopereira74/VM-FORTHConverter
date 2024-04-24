import json
from lexer import lexer
from parserr import parser

inp = """
7 2* 1+ . ( 15=7*2+1 )
(12 * ( 20 - 17 ))
"""

def main():
    lexer.input(inp)
    parsed_dict = parser.parse(inp)
    #print(json.dumps(parsed_dict, indent=2))
    print(parsed_dict)

if __name__ == '__main__':
    main()
