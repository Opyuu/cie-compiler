import sys
from lex import *
from parser import *
from emit import *
import cpp_parse

def main():
    print("CIE Pseudocode compiler by Opyu")

    if len(sys.argv) < 2:
        sys.exit("Compiler needs a file as input.")

    with open(sys.argv[1], 'r') as i:
        source = i.read()


    lexer = Lexer(source)

    if (len(sys.argv) > 2):
        if sys.argv[2].lower() == "cpp" or sys.argv[2].lower() == "c++":
            emitter = Emitter("out.cpp")
            print("Compiling to C++.")
            parser = cpp_parse.Parser(lexer, emitter)
        else:
            sys.exit("Invalid language specified.")
    else:
        emitter = Emitter("out.py")
        print("Compiling to Python.")
        parser = Parser(lexer, emitter)

    emitter.writeFile()

    parser.program()
    print("Compiling complete")
    # token = lexer.getToken()
    # while token.kind != TokenType.EOF:
    #     print(token.kind, token.text)
    #     token = lexer.getToken()

main()