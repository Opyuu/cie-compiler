import sys
from lex import *
from parser import *
from emit import *


def main():
    print("CIE Pseudocode compiler by Opyu")

    if len(sys.argv) != 2:
        sys.exit("Compiler needs a file as input.")

    with open(sys.argv[1], 'r') as i:
        source = i.read()


    lexer = Lexer(source)
    emitter = Emitter("../out.py")
    parser = Parser(lexer, emitter)

    emitter.writeFile()

    parser.program()
    print("Compiling complete")
    # token = lexer.getToken()
    # while token.kind != TokenType.EOF:
    #     print(token.kind, token.text)
    #     token = lexer.getToken()

main()