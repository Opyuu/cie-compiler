class Emitter:
    def __init__(self, file):
        self.filePath = file
        self.header = ""
        self.code = ""
        self.scope = 0

    def emit(self, code, scope=None):
        if scope == None:
            self.code += self.scope * "    " + code

        else:
            self.code += scope * "    " + code

    def emitLine(self, code, scope=None):
        if scope == None:
            self.code += self.scope * "    " + code + "\n"

        else:
            self.code += scope * "    " + code + "\n"

    def writeFile(self):
        with open(self.filePath, 'w') as f:
            f.write(self.header + self.code)

    def headerLine(self, code):
        self.header += self.scope * "    " + code + "\n"