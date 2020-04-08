import sys
import re
from abc import abstractmethod, ABC


list_reserved = ['echo', '$', ';', '=', '+', '-', '/', '*', 'if', 'else', 'while']


class SymbolTable():
    mainDict = {}
    def setter(self, chave, valor):
        self.mainDict[chave] = valor

    def getter(self, chave):
        return self.mainDict[chave]


class Node(ABC):
    value = None
    children = None

    @abstractmethod
    def Evaluate(self):
        pass


class BinOp(Node):
    def __init__(self, value):
        self.children = []
        self.value = value

    def Evaluate(self):
        if(self.value == "+"):
            return self.children[0].Evaluate() + self.children[1].Evaluate()
        elif(self.value == "-"):
            return (self.children[0].Evaluate() - self.children[1].Evaluate())
        elif(self.value == "*"):
            return self.children[0].Evaluate() * self.children[1].Evaluate()
        elif(self.value == "/"):
            return self.children[0].Evaluate() // self.children[1].Evaluate()
        raise Exception("Error in BinOp: Value unexpected")


class UnOp(Node):
    def __init__(self, value):
        self.value = value

    def Evaluate(self):
        if(self.value == "-"):
            return -self.children.Evaluate()
        elif(self.value == "+"):
            return self.children.Evaluate()
        raise Exception("Error in UnOp: Value unexpected")


class IntVal(Node):
    def __init__(self, value):
        self.children = None
        self.value = value

    def Evaluate(self):
        return self.value


class NoOp(Node):
    def __init__(self):
        pass
    def Evaluate(self):
        pass


class Commands(Node):
    def __init__(self):
        self.children = []
        self.value = None

    def Evaluate(self):
        for i in self.children:
            i.Evaluate()

class IdentifierOp(Node):
    def __init__(self,value):
        self.children = None
        self.value = value

    def Evaluate(self):
        return SymbolTable().getter(self.value)

class AssingnmentOp(Node):
    def __init__(self, IDENTIFIER):
        self.children = [IDENTIFIER]
        self.value = None

    def Evaluate(self):
        SymbolTable().setter(self.children[0], self.children[1].Evaluate())

class EchoOp(Node):
    def __init__(self, Expression):
        self.children = Expression
        self.value = None

    def Evaluate(self):
        print(self.children.Evaluate())

class Token:
    Type = None
    value = None


class Tokenizer:

    def __init__(self, origin):
        self.position = 0
        self.origin = origin
        self.actual = Token()

    def selectNext(self):
        goAgain = True
        while goAgain:
            goAgain = False
            self.position += 1
            if(self.position > len(self.origin)):
                self.actual.Type = "EOF"
                self.actual.value = ""
            elif(self.origin[self.position-1].isdigit()):
                init = self.position-1
                while (self.origin[init:self.position+1].isdigit() and (self.position+1 <= len(self.origin))):
                    self.position += 1
                end = self.position
                self.actual.Type = "INT"
                self.actual.value = int(self.origin[init:end])
            elif(self.origin[self.position-1] == "+"):
                self.actual.Type = "PLUS"
                self.actual.value = (self.origin[self.position-1])
            elif(self.origin[self.position-1] == "-"):
                self.actual.Type = "MINUS"
                self.actual.value = (self.origin[self.position-1])
            elif(self.origin[self.position-1] == "*"):
                self.actual.Type = "MULT"
                self.actual.value = (self.origin[self.position-1])
            elif(self.origin[self.position-1] == "/"):
                self.actual.Type = "DIV"
                self.actual.value = (self.origin[self.position-1])
            elif(self.origin[self.position-1] == "("):
                self.actual.Type = "OPENPAR"
                self.actual.value = (self.origin[self.position-1])
            elif(self.origin[self.position-1] == ")"):
                self.actual.Type = "CLOSEPAR"
                self.actual.value = (self.origin[self.position-1])
            elif(self.origin[self.position-1] == "{"):
                self.actual.Type = "OPENBLOCK"
                self.actual.value = (self.origin[self.position-1])
            elif(self.origin[self.position-1] == "}"):
                self.actual.Type = "CLOSEBLOCK"
                self.actual.value = (self.origin[self.position-1])
            elif(self.origin[self.position-1:self.position+3] == "echo"):
                self.actual.Type = "ECHO"
                self.actual.value = (self.origin[self.position-1])
                self.position += 3
            elif(self.origin[self.position-1] == "="):
                self.actual.Type = "EQUAL"
                self.actual.value = (self.origin[self.position-1])
            elif(self.origin[self.position-1] == "$"):
                
                init = self.position-1
                while ((self.origin[self.position] not in list_reserved) and (self.position+1 <= len(self.origin))):
                    self.position += 1
                end = self.position
                if(self.origin[init+1:end] in list_reserved):
                    raise Exception("Error, token reserved: %s" % self.origin[init+1:end])
                elif(not re.match(r'[$]+[A-Za-z]+[A-Za-z0-9_]*$',self.origin[init:end])):
                    raise Exception("Error, token does not follow the rules of var type. (%s) " % (self.origin[init+1:end]))
                self.actual.value = (self.origin[init:end])
                self.actual.Type = "IDENTIFIER"
            elif(self.origin[self.position-1] == ";"):
                self.actual.Type = "ENDLINE"
                self.actual.value = (self.origin[self.position-1])

            else:
                raise Exception(
                    "ERRO", "Operando '%s' não reconhecido na posição %d" % (self.origin[self.position-1], self.position-1))


class Parser:

    tokens = None

    @staticmethod
    def parseFactor(tokens):
        Parser.tokens.selectNext()
        try:
            if(Parser.tokens.actual.Type == "IDENTIFIER"):
                val = IdentifierOp(Parser.tokens.actual.value)
                Parser.tokens.selectNext()
                return val

            elif(Parser.tokens.actual.Type == "INT"):
                val = IntVal(Parser.tokens.actual.value)
                Parser.tokens.selectNext()
                return val
            elif (Parser.tokens.actual.Type in ["MINUS", "PLUS"]):
                if(Parser.tokens.actual.Type == "MINUS"):
                    un = UnOp("-")
                    un.children = Parser.parseFactor(tokens)
                    return un
                else:
                    un = UnOp("+")
                    un.children = Parser.parseFactor(tokens)
                    return un
            
            elif (Parser.tokens.actual.Type == "OPENPAR"):
                temp = Parser.parseExpression(tokens)
                if(Parser.tokens.actual.Type == "CLOSEPAR"):
                    Parser.tokens.selectNext()
                    return temp

            elif (Parser.tokens.actual.Type == "OPENBLOCK"):

                temp = Parser.parseExpression(tokens)
                if(Parser.tokens.actual.Type == "CLOSEBLOCK"):
                    Parser.tokens.selectNext()
                    return temp

            raise Exception("ERROR IN FACTOR")
        except Exception as e:
            print(e)

    @staticmethod
    def parseTerm(tokens):
        temp_value = Parser.parseFactor(tokens)
        if(Parser.tokens.actual.Type == "MULT"):
            term = BinOp("*")
            term.children.append(temp_value)
            term.children.append(Parser.parseTerm(tokens))

        elif(Parser.tokens.actual.Type == "DIV"):
            term = BinOp("/")
            term.children.append(temp_value)
            term.children.append(Parser.parseTerm(tokens))

        else:
            return temp_value
        return term

    @staticmethod
    def parseExpression(tokens):
        temp_value = Parser.parseTerm(tokens)
        if(Parser.tokens.actual.Type not in ["EOF"] and Parser.tokens.actual.Type in ["PLUS", "MINUS"]):
            if(Parser.tokens.actual.Type == "PLUS"):
                main = BinOp("+")
                main.children.append(temp_value)

            elif(Parser.tokens.actual.Type == "MINUS"):
                main = BinOp("-")
                main.children.append(temp_value)
            main.children.append(Parser.parseExpression(tokens))
            return main
        return temp_value

    @staticmethod
    def parseCommand(tokens):
        if(Parser.tokens.actual.Type == "ENDLINE"):
            Parser.tokens.selectNext()
            return NoOp()
        elif(Parser.tokens.actual.Type == "IDENTIFIER"):
            temp = AssingnmentOp(Parser.tokens.actual.value)
            Parser.tokens.selectNext()
            if(Parser.tokens.actual.Type != "EQUAL"):
                raise Exception("Error, equal not found after Assignment")
            temp.children.append(Parser.parseExpression(tokens))            
            if(Parser.tokens.actual.Type == "ENDLINE"):
                Parser.tokens.selectNext()
            else:
                raise Exception("Missing ';' after IDENTIFIER")
            return temp
        elif(Parser.tokens.actual.Type == "ECHO"):
            ecc = EchoOp(Parser.parseExpression(tokens))
            if(Parser.tokens.actual.Type == "ENDLINE"):
                Parser.tokens.selectNext()
            else:
                raise Exception("Missing ';' after IDENTIFIER")
            return ecc
        else:
            #Parser.tokens.selectNext()
            return Parser.parseBlock(tokens)

    @staticmethod
    def parseBlock(tokens):
        commands = Commands()
        if (Parser.tokens.actual.Type == "OPENBLOCK"):
            Parser.tokens.selectNext()
            while(Parser.tokens.actual.Type != "CLOSEBLOCK"):
                temp = Parser.parseCommand(tokens)
                commands.children.append(temp)
            Parser.tokens.selectNext()
            return commands

        raise Exception(
            "Error on ParseBlock, failed to open/close block properly.")

    @staticmethod
    def run(origin):
        Parser.tokens = Tokenizer(PrePro.filter(origin))
        Parser.tokens.selectNext()
        final = Parser.parseBlock(Parser.tokens)
        if(Parser.tokens.actual.Type == "EOF"):
            return final
        else:
            raise Exception("Erro", "Input is wrong at position %d (%s) " % (
                Parser.tokens.position-1, Parser.tokens.origin[Parser.tokens.position-1]))


class PrePro:

    @staticmethod
    def filter(origin):
        pattern = re.compile("/\*.*?\*/", re.DOTALL | re.MULTILINE)
        line = pattern.sub("", origin)
        return line


if __name__ == '__main__':
    file_php = (sys.argv[1])
    if(".php" in file_php):
        with open(file_php) as fp:
            lines = fp.read()
            line = lines.replace('\n', '')
            line = line.replace(' ', '')
            value = Parser.run(line)
            value.Evaluate()

    else:
        raise Exception("Type error: %s is not a '.php' file" % (file_php))
