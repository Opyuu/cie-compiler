import sys
from lex import *


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

        self.types = ["INTEGER", "BOOLEAN", "FLOAT", "STRING", "CHAR"]

        self.nextToken()
        self.nextToken()

    def checkToken(self, kind):
        return kind == self.curToken.kind

    def checkPeek(self, kind):
        return kind == self.peekToken.kind

    def match(self, kind):
        if not self.checkToken(kind):
            self.abort(f"Expected token {kind}, got {self.curToken.kind.name}.")

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
                    self.emitter.emitLine(f'print("{self.curToken.text}")')
                    self.nextToken()
                else:
                    self.emitter.emit(f'print(')
                    self.expression()
                    self.emitter.emitLine(')', 0)

            case TokenType.INPUT:
                self.nextToken()

                if (self.curToken.text, "INTEGER") in self.symbols:
                    self.emitter.emitLine(f"{self.curToken.text} = int(input(''))")
                elif (self.curToken.text, "FLOAT") in self.symbols:
                    self.emitter.emitLine(f"{self.curToken.text} = float(input(''))")

                elif (checkItem(self.symbols, self.curToken.text)):
                    self.abort(f"Undefined type conversion from STRING to {findItem(self.symbols, self.curToken.text)[1]}.")

                else:
                    self.symbols.add((self.curToken.text, "STRING"))
                    self.emitter.emitLine(f"{self.curToken.text} = input('')")  # Assume float.

                self.match(TokenType.IDENT)

            case TokenType.IF:  # IF <comparison> THEN ... ENDIF
                prevSymbols = set(self.symbols)
                self.emitter.emit("if (")
                self.nextToken()
                self.comparison()

                self.match(TokenType.THEN)
                self.nl()
                self.emitter.emitLine("):", 0)
                self.emitter.scope += 1

                while not self.checkToken(TokenType.ENDIF) and not self.checkToken(TokenType.ELSE):  # Check for ... statements inside IF block
                    self.statement()

                def check_else():
                    if self.checkToken(TokenType.ELSE):  # ELSE ...
                        # ELIFS are actually not defined by CIE Pseudocode
                        self.emitter.scope -= 1

                        self.nextToken()

                        if self.checkToken(TokenType.IF):  # ELSE IF <condition> THEN
                            self.nextToken()
                            self.emitter.emit("elif (")
                            self.comparison()
                            self.emitter.emitLine("):", 0)
                            self.match(TokenType.THEN)
                            self.nl()

                            self.emitter.scope += 1
                            while not self.checkToken(TokenType.ENDIF) and not self.checkToken(TokenType.ELSE):
                                self.statement()

                            check_else()

                        else:
                            self.match(TokenType.NEWLINE)
                            self.emitter.emitLine("else:")

                            self.emitter.scope += 1
                            while not self.checkToken(TokenType.ENDIF):
                                self.statement()

                check_else()
                self.match(TokenType.ENDIF) # Emit error for missing ENDIF
                self.emitter.scope -= 1
                self.emitter.emit("\n")
                self.symbols = set(prevSymbols)

            case TokenType.WHILE:
                prevSymbols = set(self.symbols)
                self.emitter.emit("while (")
                self.nextToken()
                self.comparison()

                self.match(TokenType.NEWLINE)
                self.emitter.emitLine("):", 0)
                self.emitter.scope += 1

                while not self.checkToken(TokenType.ENDWHILE):
                    self.statement()

                self.match(TokenType.ENDWHILE)
                self.emitter.scope -= 1
                self.emitter.emit("\n")
                self.symbols = set(prevSymbols)

            case TokenType.FOR:  # FOR <ident> = <expr> TO <expr> {STEP <expr>}
                prevSymbols = set(self.symbols)
                self.emitter.emit("for")
                self.nextToken()

                if not checkItem(self.symbols, self.curToken.text):  # <ident>
                    self.symbols.add((self.curToken.text, "INTEGER"))

                elif (self.curToken.text, "INTEGER") not in self.symbols:
                    self.abort(f"Unable to iterate using type {findItem(self.symbols, self.curToken.text)[1]}.")

                self.emitter.emit(f" {self.curToken.text} in range(", 0)

                self.nextToken()
                self.match(TokenType.EQ)  # =

                self.expression()  # <expr>

                self.match(TokenType.TO)  # TO
                self.emitter.emit(", ", 0)

                self.expression()  # <expr>

                if self.checkToken(TokenType.STEP):  # STEP <expr>
                    self.nextToken()
                    self.emitter.emit(", ", 0)
                    self.expression()

                self.nl()
                self.emitter.emitLine("):", 0)
                self.emitter.scope += 1

                while not self.checkToken(TokenType.NEXT):
                    self.statement()

                self.match(TokenType.NEXT)
                self.nextToken()

                self.emitter.emitLine("")
                self.emitter.scope -= 1

                self.symbols = set(prevSymbols)


            case TokenType.DECLARE:
                self.nextToken()

                identName = self.curToken.text
                self.emitter.emit(f"{self.curToken.text} = None")
                self.match(TokenType.IDENT)
                self.match(TokenType.COLON)

                if not self.curToken.text in self.types:
                    self.abort(f"Unknown type: {self.curToken.text}.")


                self.emitter.emit(f"  # Type {self.curToken.text}", 0)

                if not checkItem(self.symbols, identName):
                    self.symbols.add((identName, self.curToken.text))
                else:
                    self.abort(f"Re-declaration of identifier {identName}.")

                self.nextToken()
                # self.expression()
                self.emitter.emitLine("")

            case TokenType.IDENT:
                if not findItem(self.symbols, self.curToken.text):
                    self.abort(f"Unknown identifier: {self.curToken.text}.")

                self.emitter.emit(f"{self.curToken.text}")
                self.nextToken()
                self.match(TokenType.EQ)
                self.emitter.emit(" = ", 0)
                self.expression()
                self.emitter.emitLine("")

            case TokenType.REPEAT:
                prevSymbols = set(self.symbols)
                self.emitter.emitLine("while True:")
                self.nextToken()
                self.match(TokenType.NEWLINE)
                self.emitter.scope += 1

                while not self.checkToken(TokenType.UNTIL):
                    self.statement()

                self.match(TokenType.UNTIL)
                self.emitter.emit("if (")
                self.comparison()
                self.emitter.emitLine("):", 0)
                self.emitter.scope += 1
                self.emitter.emitLine("break")
                self.emitter.scope -= 1
                self.emitter.emitLine("")
                self.emitter.scope -= 1

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
                self.emitter.emit("True", 0)
            elif self.curToken.text == "FALSE":
                self.emitter.emit("False", 0)

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
        self.emitter.headerLine("def main():")
        self.emitter.scope += 1
        while self.checkToken(TokenType.NEWLINE):
            self.nextToken()

        while not self.checkToken(TokenType.EOF):
            self.statement()

        self.emitter.emitLine('return')

        self.emitter.scope -= 1

        self.emitter.emitLine('\nmain()')
        self.emitter.writeFile()
