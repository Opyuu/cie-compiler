import sys
from lex import *

class Parser():
    def __init__(self, lexer, emitter) -> None:
        self.lexer = lexer
        self.emitter = emitter

        self.curToken = None
        self.peekToken = None
        self.symbols = set()

        self.nextToken()
        self.nextToken()

    def checkToken(self, kind):
        return kind == self.curToken.kind

    def checkPeek(self, kind):
        return kind == self.peekToken.kind

    def match(self, kind):
        if not self.checkToken(kind):
            self.abort(f"Expected token {kind}, got {self.curToken.kind.name}")

        self.nextToken()

    def nextToken(self):
        self.curToken = self.peekToken
        self.peekToken = self.lexer.getToken()

    def abort(self, message):
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

                if self.curToken.text not in self.symbols:
                    self.symbols.add(self.curToken.text)
                    self.emitter.emitLine(f"{self.curToken.text} = float(input(''))")  # Assume float. Will change when add typing

                self.match(TokenType.IDENT)

            case TokenType.IF:  # IF <comparison> THEN ... ENDIF
                self.emitter.emit("if (")
                self.nextToken()
                self.comparison()

                self.match(TokenType.THEN)
                self.nl()
                self.emitter.emitLine("):", 0)
                self.emitter.scope += 1

                while not self.checkToken(TokenType.ENDIF):  # Check for ... statements inside IF block
                    self.statement()

                self.match(TokenType.ENDIF) # Emit error for missing ENDIF
                self.emitter.scope -= 1
                self.emitter.emit("\n")


            case TokenType.WHILE:
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

            case TokenType.DECLARE:
                self.nextToken()

                if self.curToken.text not in self.symbols:
                    self.symbols.add(self.curToken.text)

                self.emitter.emit(f"{self.curToken.text} = ")
                self.match(TokenType.IDENT)
                self.match(TokenType.EQ)
                self.expression()
                self.emitter.emitLine("")

            case TokenType.IDENT:
                if self.curToken.text not in self.symbols:
                    self.abort(f"Unknown identifier: {self.curToken.text}")

                self.emitter.emit(f"{self.curToken.text}")
                self.nextToken()
                self.match(TokenType.EQ)
                self.emitter.emit(" = ", 0)
                self.expression()
                self.emitter.emitLine("")

            case TokenType.REPEAT:
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


            case _:
                self.abort(f"Invalid statement at {self.curToken.text} ({self.curToken.kind.name})")

        self.nl()

    def comparison(self):
        self.expression()

        if self.isComparisonOperator():
            self.emitter.emit(f" {self.curToken.text} ", 0)
            self.nextToken()
            self.expression()
        else:
            self.abort(f"Expected comparison operator at: {self.curToken.text}")

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
            if self.curToken.text not in self.symbols:
                self.abort(f"Referencing variable before assignment: {self.curToken.text}")

            self.emitter.emit(f"{self.curToken.text}", 0)
            self.nextToken()
        else:
            # Error!
            self.abort("Unexpected token at " + self.curToken.text)

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
