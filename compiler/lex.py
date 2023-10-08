import enum
import sys
import re

class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    INDENT = 2
    STRING = 3

    # Keywords
    OUTPUT = 101
    INPUT = 102
    IF = 103
    THEN = 104
    ELSE = 105
    ENDIF = 106
    REPEAT = 107
    UNTIL = 108
    DECLARE = 109
    CONSTANT = 110
    WHILE = 111
    ENDWHILE = 112
    FOR = 113
    TO = 114
    STEP = 115
    NEXT = 116

    # Operators
    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206  # ==
    NOTEQ = 207  # !=
    LT = 208  # <
    LTEQ = 209  # <=
    GT = 210  # >
    GTEQ = 211  # >=
    IDENT = 212  # Identifiers
    COLON = 213


class Token():
    def __init__(self, tokenText, tokenKind):
        self.text = tokenText
        self.kind = tokenKind


class Lexer():
    def __init__(self, source) -> None:
        self.source = source + "\n"  # Code to be compiled
        self.char = ''
        self.ptr = -1  # Pointer to current char
        self.nextChar()
        pass

    def checkKeyword(self, tokenText):
        for kind in TokenType:
            if kind.name == tokenText and kind.value > 100 and kind.value <= 200:
                return kind

        return None

    def nextChar(self) -> None:
        self.ptr += 1
        if self.ptr >= len(self.source):
            self.char = '\0'
        else:
            self.char = self.source[self.ptr]

    def peek(self):  # Returns the next char without being there
        if (self.ptr + 1) >= len(self.source):
            return '\0'

        return self.source[self.ptr + 1]

    def skipWhitespace(self):
        while self.char == ' ' or self.char == '\t' or self.char == '\r':
            self.nextChar()

    def skipComment(self):
        if self.char == '/':
            if self.peek() == '/':
                self.nextChar()
                while self.char != '\n':
                    self.nextChar()

    def getToken(self):
        self.skipWhitespace()
        self.skipComment()
        token = None

        match(self.char):
            case '+':
                token = Token(self.char, TokenType.PLUS)

            case '-':
                token = Token(self.char, TokenType.MINUS)

            case '*':
                token = Token(self.char, TokenType.ASTERISK)

            case '/':
                token = Token(self.char, TokenType.SLASH)

            case '<':  # Check for >= or >
                if (self.peek == '='):
                    lastChar = self.char
                    self.nextChar()
                    token = Token(lastChar + self.char, TokenType.LTEQ)
                else:
                    token = Token(self.char, TokenType.LT)

            case '>':  # Check for <= or <
                if (self.peek == '='):
                    lastChar = self.char
                    self.nextChar()
                    token = Token(lastChar + self.char, TokenType.GTEQ)
                else:
                    token = Token(self.char, TokenType.GT)

            case '!':
                if (self.peek() == '='):
                    lastChar = self.char
                    self.nextChar()
                    token = Token(lastChar + self.char, TokenType.NOTEQ)
                else:
                    self.abort(f"Expected '!=', got '!{self.peek()}'")

            case '=':
                if (self.peek() == '='):
                    lastChar = self.char
                    self.nextChar()
                    token = Token(lastChar + self.char, TokenType.EQEQ)
                else:
                    token = Token(self.char, TokenType.EQ)

            case '\"':
                self.nextChar()
                startPos = self.ptr

                while self.char != '\"':
                    self.nextChar()

                tokText = self.source[startPos : self.ptr]
                token = Token(tokText, TokenType.STRING)

            case ch if re.match(r"[0-9]", ch): # Digit encountered
                startPos = self.ptr

                while re.match(r"[0-9]", self.peek()):
                    self.nextChar()
                if self.peek() == '.':
                    self.nextChar()

                    if not re.match(r"[0-9]", self.peek()):
                        self.abort("Illegal character in number")

                    while re.match(r"[0-9]", self.peek()):
                        self.nextChar()

                tokText = self.source[startPos : self.ptr + 1]
                token = Token(tokText, TokenType.NUMBER)

            case ':':
                token = Token(self.char, TokenType.COLON)

            case '\n':
                token = Token(self.char, TokenType.NEWLINE)

            case '\0':
                token = Token(self.char, TokenType.EOF)

            case ch if re.match(r"[a-zA-Z0-9_]+$", ch): # Alphanumeric
                startPos = self.ptr

                while re.match(r"[a-zA-Z0-9_]+$", self.peek()):
                    self.nextChar()

                tokText = self.source[startPos : self.ptr + 1]

                keyword = self.checkKeyword(tokText)
                if keyword == None:
                    token = Token(tokText, TokenType.IDENT)
                else:
                    token = Token(tokText, keyword)
                pass

            case _:
                self.abort(f"Unknown token: '{self.char}'")

        self.nextChar()
        return token

    def abort(self, message):
        sys.exit(f"Lexing error. {message}")
