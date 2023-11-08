import sys
from lex import *

varMap = {
    "INTEGER": "int",
    "BOOLEAN": "bool",
    "REAL": "float",
    "STRING": "std::string"
}

def checkItem(set, item) -> bool:
    for i in set:
        if item == i[0]:
            return True

    return False


def findItem(set, item) -> tuple:
    for i in set:
        if item == i[0]:
            return i

    return None


class Parser():
    def __init__(self, lexer, emitter) -> None:
        self.lexer = lexer
        self.emitter = emitter

        self.curToken = None
        self.peekToken = None
        self.symbols = set()
        self.constants = set()

        self.types = ["INTEGER", "BOOLEAN", "REAL", "STRING", "CHAR"]

        self.nextToken()
        self.nextToken()

    def checkToken(self, kind):
        return kind == self.curToken.kind

    def checkPeek(self, kind):
        return kind == self.peekToken.kind

    def match(self, kind):
        if not self.checkToken(kind):
            self.abort(f"Expected token '{kind}', got '{self.curToken.kind.name}.'")

        self.nextToken()

    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()

    @staticmethod
    def abort(message):
        sys.exit(f"Error: {message}")

    def nl(self):
        self.match(TokenType.NEWLINE)

        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

    def statement(self):
        match(self.curToken.kind):
            case TokenType.OUTPUT:  # Check for OUTPUT statements
                self.nextToken()

                if self.checkToken(TokenType.STRING):
                    self.emitter.emitLine(f'std::cout << "{self.curToken.text}" << std::endl;')
                    self.nextToken()
                else:
                    self.emitter.emit(f'std::cout << ')
                    self.expression()
                    self.emitter.emitLine(' << std::endl;', 0)

            case TokenType.INPUT:
                self.nextToken()



                if (self.curToken.text, "INTEGER") in self.symbols:
                    self.emitter.emitLine(f"std::cin >> {self.curToken.text};")
                elif (self.curToken.text, "REAL") in self.symbols:
                    self.emitter.emitLine(f"std::cin >> {self.curToken.text};")

                elif (checkItem(self.symbols, self.curToken.text)):
                    self.abort(f"Undefined type conversion from 'STRING' to '{findItem(self.symbols, self.curToken.text)[1]}'.")

                else:
                    self.symbols.add((self.curToken.text, "STRING"))
                    self.emitter.emitLine(f"std::string {self.curToken.text};")
                    self.emitter.emitLine(f"std::cin << {self.curToken.text};")  # Assume float.

                self.match(TokenType.IDENT)

            case TokenType.IF:  # IF <comparison> THEN ... ENDIF
                prevSymbols = set(self.symbols)
                self.emitter.emit("if (")
                self.nextToken()
                self.comparison()

                self.match(TokenType.THEN)
                self.nl()
                self.emitter.emitLine("){", 0)
                self.emitter.scope += 1

                while not self.checkToken(TokenType.ENDIF) and not self.checkToken(TokenType.ELSE):  # Check for ... statements inside IF block
                    self.statement()

                def check_else():
                    if self.checkToken(TokenType.ELSE):  # ELSE ...
                        # ELIFS are actually not defined by CIE Pseudocode
                        self.emitter.scope -= 1
                        self.emitter.emit("} ")

                        self.nextToken()

                        if self.checkToken(TokenType.IF):  # ELSE IF <condition> THEN
                            self.nextToken()
                            self.emitter.emit("else if (", 0)
                            self.comparison()
                            self.emitter.emitLine("){", 0)
                            self.match(TokenType.THEN)
                            self.nl()

                            self.emitter.scope += 1
                            while not self.checkToken(TokenType.ENDIF) and not self.checkToken(TokenType.ELSE):
                                self.statement()

                            check_else()

                        else:
                            self.match(TokenType.NEWLINE)
                            self.emitter.emitLine("else{", 0)

                            self.emitter.scope += 1
                            while not self.checkToken(TokenType.ENDIF):
                                self.statement()

                check_else()
                self.match(TokenType.ENDIF) # Emit error for missing ENDIF
                self.emitter.scope -= 1
                self.emitter.emitLine("}\n")
                self.symbols = set(prevSymbols)

            case TokenType.WHILE:
                prevSymbols = set(self.symbols)
                self.emitter.emit("while (")
                self.nextToken()
                self.comparison()

                self.match(TokenType.NEWLINE)
                self.emitter.emitLine("){", 0)
                self.emitter.scope += 1

                while not self.checkToken(TokenType.ENDWHILE):
                    self.statement()

                self.match(TokenType.ENDWHILE)
                self.emitter.scope -= 1
                self.emitter.emitLine("}\n")
                self.symbols = set(prevSymbols)

            case TokenType.FOR:  # FOR <ident> = <expr> TO <expr> {STEP <expr>}
                prevSymbols = set(self.symbols)
                self.emitter.emit("for (")
                self.nextToken()

                iterator = self.curToken.text

                if not checkItem(self.symbols, self.curToken.text):  # <ident>
                    self.symbols.add((self.curToken.text, "INTEGER"))
                    self.emitter.emit("int ", 0)

                elif (self.curToken.text, "INTEGER") not in self.symbols:
                    self.abort(f"Unable to iterate using type '{findItem(self.symbols, self.curToken.text)[1]}'.")

                self.emitter.emit(f"{self.curToken.text} = ", 0)

                self.nextToken()
                self.match(TokenType.EQ)  # =

                self.expression()  # <expr>

                self.match(TokenType.TO)  # TO
                self.emitter.emit(f"; {iterator} < ", 0)

                self.expression()  # <expr>

                if self.checkToken(TokenType.STEP):  # STEP <expr>
                    self.nextToken()
                    self.emitter.emit(f"; {iterator} += ", 0)
                    self.expression()
                else:
                    self.emitter.emit(f"; {iterator}++", 0)

                self.nl()
                self.emitter.emitLine("){", 0)
                self.emitter.scope += 1

                while not self.checkToken(TokenType.NEXT):
                    self.statement()

                self.match(TokenType.NEXT)
                self.nextToken()

                self.emitter.scope -= 1
                self.emitter.emitLine("}\n")


                self.symbols = set(prevSymbols)

            case TokenType.DECLARE:
                self.nextToken()

                identName = self.curToken.text
                # self.emitter.emit(f"{self.curToken.text} = None")
                self.match(TokenType.IDENT)
                self.match(TokenType.COLON)

                if not self.curToken.text in self.types:
                    self.abort(f"Unknown type: '{self.curToken.text}'.")

                self.emitter.emit(f"{varMap[self.curToken.text]} {identName}")

                if (self.curToken.text == "INTEGER"):
                    self.emitter.emit(" = 0", 0)

                self.emitter.emitLine(";", 0)

                if not checkItem(self.symbols, identName):
                    self.symbols.add((identName, self.curToken.text))
                else:
                    self.abort(f"Re-declaration of identifier '{identName}'.")

                self.nextToken()

            case TokenType.CONSTANT:
                self.nextToken()

                if not checkItem(self.symbols, self.curToken.text):
                    self.symbols.add((self.curToken.text, "CONSTANT"))
                    self.emitter.emit(f"const auto {self.curToken.text} = ")
                else:
                    self.abort(f"Re-declaration of CONSTANT '{self.curToken.text}'.")


                self.match(TokenType.IDENT)

                self.match(TokenType.EQ)

                self.expression()
                self.emitter.emitLine(";", 0)



            case TokenType.IDENT:
                if not findItem(self.symbols, self.curToken.text):
                    self.abort(f"Unknown identifier: {self.curToken.text}.")

                if (self.curToken.text, "CONSTANT") in self.symbols:
                    self.abort(f"Re-assignment of CONSTANT '{self.curToken.text}'.")

                self.emitter.emit(f"{self.curToken.text}")
                self.nextToken()
                self.match(TokenType.EQ)
                self.emitter.emit(" = ", 0)
                self.expression()
                self.emitter.emitLine(";", 0)

            case TokenType.REPEAT:
                prevSymbols = set(self.symbols)
                self.emitter.emitLine("do {")
                self.nextToken()
                self.match(TokenType.NEWLINE)
                self.emitter.scope += 1

                while not self.checkToken(TokenType.UNTIL):
                    self.statement()

                self.match(TokenType.UNTIL)
                self.emitter.scope -= 1
                self.emitter.emit("} while (!(")
                self.comparison()
                self.emitter.emitLine("));", 0)


                self.symbols = set(prevSymbols)

            case _:
                self.abort(f"Invalid statement at {self.curToken.text} ({self.curToken.kind.name}).")

        self.nl()

    def comparison(self):
        self.expression()

        if self.isComparisonOperator():
            self.emitter.emit(f" {self.curToken.text} ", 0)
            self.nextToken()
            self.expression()
        else:
            self.abort(f"Expected comparison operator at: {self.curToken.text}.")

    def expression(self):
        self.term()

        while self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(f" {self.curToken.text} ", 0)
            self.nextToken()
            self.term()

    def term(self):
        self.unary()

        while self.checkToken(TokenType.ASTERISK) or self.checkToken(TokenType.SLASH):
            self.emitter.emit(f" {self.curToken.text} ", 0)
            self.nextToken()
            self.unary()

    def unary(self):
        if self.checkToken(TokenType.PLUS) or self.checkToken(TokenType.MINUS):
            self.emitter.emit(f"{self.curToken.text}", 0)
            self.nextToken()
        self.primary()

    def primary(self):
        if self.checkToken(TokenType.NUMBER):
            self.emitter.emit(f"{self.curToken.text}", 0)

            self.nextToken()
        elif self.checkToken(TokenType.IDENT):
            if self.curToken.text == "TRUE":
                self.emitter.emit("true", 0)
            elif self.curToken.text == "FALSE":
                self.emitter.emit("false", 0)

            elif not checkItem(self.symbols, self.curToken.text):
                self.abort(f"Referencing variable before assignment: {self.curToken.text}.")

            else:
                self.emitter.emit(f"{self.curToken.text}", 0)
            self.nextToken()
        else:
            # Error!
            self.abort(f"Unexpected token at {self.curToken.text}.")

    def isComparisonOperator(self) -> bool:
        return self.checkToken(TokenType.GT) or self.checkToken(TokenType.GTEQ) or self.checkToken(TokenType.LT) or self.checkToken(TokenType.LTEQ) or self.checkToken(TokenType.EQEQ) or self.checkToken(TokenType.NOTEQ)

    def program(self):
        self.emitter.headerLine("#include <iostream>\n")
        self.emitter.headerLine("int main(){")
        self.emitter.scope += 1
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        while not self.checkToken(TokenType.EOF):
            self.statement()

        self.emitter.emitLine('return 0;')

        self.emitter.scope -= 1

        self.emitter.emitLine('}')
        self.emitter.writeFile()
