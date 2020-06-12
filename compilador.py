import sys
import re
from abc import abstractmethod, ABC


list_reserved = ['echo', '$', ';', '=', '+', '-', '/', '*', 'if', 'else', ' ',
                 'while', 'readline', 'and', 'or', '<', '>', '==', '!', '(', ')', 'true', 'false', ".", "return", "function", ","]




class SymbolTable():
    
    def __init__(self):
        self.mainDict = {}
        self.value = None    

    def setter(self, chave, valor, tipo):
        self.mainDict[chave] = valor, tipo

    def getter(self, chave):
        return self.mainDict[chave]

    def setall(self, dicionario_novo):
        self.mainDict.clear()
        self.mainDict.update(dicionario_novo)

    def getall(self):
        return self.mainDict.copy()
    
    def getValue(self):
        return self.value

    def setValue(self,_value):
        self.value = _value

class SymbolTableFunc():
    mainDict = {}
    value = None
    def setter(self, chave, valor, tipo):
        if(chave in self.mainDict):
            raise Exception("Can't declare same function twice")
        self.mainDict[chave] = valor, tipo

    def getter(self, chave):
        if(chave not in self.mainDict):
            raise Exception("Function '%s' hasn't been declared" % chave)
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
        child1 = self.children[0].Evaluate()
        child2 = self.children[1].Evaluate()
        if(self.value == "."):
            return str(child1[0])+str(child2[0]), "STR"

        if((child1[1] in ['BOOL', 'INT']) and (child2[1] in ['BOOL', 'INT'])):
            if(self.value in ['+', '-', '/', '*']):
                if(child1[1] == "BOOL"):
                    if(child1[0]):
                        child1 = 1, "INT"
                    else:
                        child1 = 0, "INT"
                if(child2[1] == "BOOL"):
                    if(child2[0]):
                        child2 = 1, "INT"
                    else:
                        child2 = 0, "INT"

                if(self.value == "+"):
                    return child1[0]+child2[0], "INT"
                elif(self.value == "-"):
                    return child1[0]-child2[0], "INT"
                elif(self.value == "*"):
                    return child1[0]*child2[0], "INT"
                elif(self.value == "/"):
                    return child1[0]//child2[0], "INT"
            elif(self.value in ["and", "or"]):
                if(child1[1] == "INT"):
                    child1 = (child1[0] >= 1), "BOOL"
                if(child2[1] == "INT"):
                    child2 = (child2[0] >= 1), "BOOL"

                if(self.value == "and"):
                    return (child1[0] and child2[0]), "BOOL"
                elif(self.value == "or"):
                    return (child1[0] or child2[0]), "BOOL"

        raise Exception("Error in BinOp: Value unexpected")


class UnOp(Node):
    def __init__(self, value):
        self.value = value

    def Evaluate(self):
        eval = self.children.Evaluate()
        if(eval[1] == "INT"):
            if(self.value == "-"):
                return -eval[0], "INT"
            elif(self.value == "+"):
                return eval
            if(self.value == "!"):
                return not eval[0], "BOOL"
        elif(eval[1] == "BOOL"):
            if(self.value == "!"):
                return not eval[0], "BOOL"
        raise Exception("Error in UnOp: Value unexpected")


class IntVal(Node):
    def __init__(self, value):
        self.children = None
        self.value = value

    def Evaluate(self):
        return self.value, "INT"


class BoolVal(Node):
    def __init__(self, value):
        self.children = None
        if(value.lower() == "false" or value == 0):
            self.value = 0
        else:
            self.value = 1

    def Evaluate(self):
        return self.value, "BOOL"


class StringVal(Node):
    def __init__(self, value):
        self.children = None
        self.value = value

    def Evaluate(self):
        return self.value, "STR"


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
            if(SymbolTableUsed.getValue() is None):
                i.Evaluate()
            else:
                break


class IdentifierOp(Node):
    def __init__(self, value):
        self.children = None
        self.value = value

    def Evaluate(self):
        return SymbolTableUsed.getter(self.value)


class ReadlineOp(Node):
    def __init__(self):
        self.children = None

    def Evaluate(self):
        ii = input()
        return int(ii), "INT"


class AssingnmentOp(Node):
    def __init__(self, IDENTIFIER):
        self.children = [IDENTIFIER]
        self.value = None

    def Evaluate(self):
        res = self.children[1].Evaluate()
        SymbolTableUsed.setter(self.children[0], res[0], res[1])


class FuncDec(Node):
    def __init__(self, nome, argumentos):
        self.children = argumentos
        self.value = nome

    def Evaluate(self):
        SymbolTableFunc().setter(self.value, self, "FUNCTION")


class FuncCall(Node):
    def __init__(self, nameFunc):
        self.children = []
        self.value = nameFunc

    def Evaluate(self):
        global SymbolTableUsed
        temp = SymbolTableFunc().getter(self.value)
        dict_temp = SymbolTableUsed
        newSymbol = SymbolTable()
        
        if(len(temp[0].children)-1 != len(self.children)):
            raise Exception("Error on call function. Wrong number of inputs")

        for i in range(len(self.children)):
            tmp_child = self.children[i].Evaluate()
            newSymbol.setter(temp[0].children[i].value,tmp_child[0],tmp_child[1])

        SymbolTableUsed = newSymbol
        temp[0].children[-1].Evaluate()

        if(not (SymbolTableUsed.getValue() is None)):
            temp_ret = SymbolTableUsed.getValue()
            SymbolTableUsed = dict_temp
            return temp_ret
        SymbolTableUsed = dict_temp


class ReturnOp(Node):
    def __init__(self, children):
        self.children = children
        self.value = None

    def Evaluate(self):
        tmp = self.children.Evaluate()
        SymbolTableUsed.setValue(tmp)


class EchoOp(Node):
    def __init__(self, Expression):
        self.children = Expression
        self.value = None

    def Evaluate(self):
        print(self.children.Evaluate()[0])


class WhileOp(Node):
    def __init__(self, expr):
        self.value = None
        self.children = [expr]

    def Evaluate(self):
        while(self.children[0].Evaluate()[0] >= 1):
            self.children[1].Evaluate()


class IfOp(Node):
    def __init__(self, child1):
        self.value = None
        self.children = [child1]

    def Evaluate(self):
        if(self.children[0].Evaluate()[0] >= 1):
            self.children[1].Evaluate()
        elif(len(self.children) == 3):
            self.children[2].Evaluate()


class RelaxOp(Node):
    def __init__(self, value, first):
        self.value = value
        self.children = [first]

    def Evaluate(self):
        child1 = self.children[0].Evaluate()
        child2 = self.children[1].Evaluate()
        if(self.value == "=="):
            return (child1[0] == child2[0]), "BOOL"
        elif(self.value == ">"):
            return (child1[0] > child2[0]), "BOOL"
        elif(self.value == "<"):
            return (child1[0] < child2[0]), "BOOL"


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
            while((self.origin[self.position-1:self.position] == ' ') and (self.position < (len(self.origin)))):
                self.position += 1

            if(self.position > len(self.origin)):
                self.actual.Type = "EOF"
                self.actual.value = ""

            elif(self.origin[self.position-1:self.position+4] == "<?php"):
                self.actual.Type = "PROGOPEN"
                self.actual.value = self.origin[self.position -
                                                1:self.position+4]
                self.position += 4
            elif(self.origin[self.position-1:self.position+1] == "?>"):
                self.actual.Type = "PROGCLOSE"
                self.actual.value = self.origin[self.position -
                                                1:self.position+1]
                self.position += 1

            elif((self.origin[self.position-1:self.position+3]).lower() == "true"):
                self.actual.Type = "BOOL"
                self.actual.value = self.origin[self.position -
                                                1:self.position+3]
                self.position += 3

            elif((self.origin[self.position-1:self.position+4]).lower() == "false"):
                self.actual.Type = "BOOL"
                self.actual.value = self.origin[self.position -
                                                1:self.position+4]
                self.position += 4

            elif(self.origin[self.position-1].isdigit()):
                init = self.position-1
                while (self.origin[init:self.position+1].isdigit() and (self.position+1 <= len(self.origin))):
                    self.position += 1
                end = self.position
                self.actual.Type = "INT"
                self.actual.value = int(self.origin[init:end])
            elif(self.origin[self.position-1] == '"'):
                init = self.position-1
                while (self.origin[self.position+1] != '"'):
                    self.position += 1
                end = self.position + 1
                self.actual.Type = "STR"
                self.actual.value = str(self.origin[init+1:end])
                self.position += 2
            elif(self.origin[self.position-1] == "+"):
                self.actual.Type = "PLUS"
                self.actual.value = (self.origin[self.position-1])
            elif(self.origin[self.position-1] == "."):
                self.actual.Type = "CONCAT"
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
            elif(self.origin[self.position-1] == "!"):
                self.actual.Type = "NOT"
                self.actual.value = (self.origin[self.position-1])
            elif(self.origin[self.position-1] == ">"):
                self.actual.Type = "MORETHAN"
                self.actual.value = (self.origin[self.position-1])
            elif(self.origin[self.position-1] == "<"):
                self.actual.Type = "LESSTHAN"
                self.actual.value = (self.origin[self.position-1])
            elif(re.match(r'[A-Za-z]', self.origin[self.position-1]) and (-1 != self.origin.find('(', self.position) and (self.origin[self.position-1:self.origin.find('(', self.position)] not in list_reserved) and (re.match(r'[A-Za-z]+[A-Za-z0-9_]*$', self.origin[self.position-1:self.origin.find('(', self.position)])))):
                end = self.origin.find('(', self.position)
                if(self.origin[self.position-1:end] in list_reserved):
                    raise Exception("Error, token reserved: %s" %
                                    self.origin[self.position-1:end])
                self.actual.value = self.origin[self.position-1:end]
                self.actual.Type = "FUNCTION_CALL"
                self.position += len(self.actual.value)-1
            elif(str.lower(self.origin[self.position-1:self.position+3]) == "echo"):
                self.actual.Type = "ECHO"
                self.actual.value = ("echo")
                self.position += 3
            elif(str.lower(self.origin[self.position-1:self.position+7]) == "function"):
                self.position += 8
                init = self.position
                while ((self.origin[self.position] not in list_reserved) and (self.position+1 <= len(self.origin))):
                    self.position += 1
                end = self.position

                if(self.origin[init+1:end] in list_reserved):
                    raise Exception("Error, token reserved: %s" %
                                    self.origin[init+1:end])
                elif(not re.match(r'[A-Za-z]+[A-Za-z0-9_]*$', self.origin[init:end])):
                    raise Exception("Error, token does not follow the rules of function type. (%s) " % (
                        self.origin[init:end]))
                self.actual.value = (self.origin[init:end])
                self.actual.Type = "FUNCTION"
                #self.position += len(self.actual.value)-1

            elif(str.lower(self.origin[self.position-1:self.position+5]) == "return"):
                self.actual.Type = "RETURN"
                self.actual.value = ("return")
                self.position += 5
            elif(self.origin[self.position-1] == ","):
                self.actual.Type = "COMMA"
                self.actual.value = (self.origin[self.position-1])
            elif(str.lower(self.origin[self.position-1:self.position+3]) == "else"):
                self.actual.Type = "ELSE"
                self.actual.value = (self.origin[self.position-1])
                self.position += 3
            elif(str.lower(self.origin[self.position-1:self.position+1]) == "if"):
                self.actual.Type = "IF"
                self.actual.value = (self.origin[self.position-1])
                self.position += 1
            elif(str.lower(self.origin[self.position-1:self.position+4]) == "while"):
                self.actual.Type = "WHILE"
                self.actual.value = (self.origin[self.position-1])
                self.position += 4
            elif(str.lower(self.origin[self.position-1:self.position+7]) == "readline"):
                self.actual.Type = "READLINE"
                self.actual.value = (self.origin[self.position-1])
                self.position += 7
            elif(str.lower(self.origin[self.position-1:self.position+1]) == "=="):
                self.actual.Type = "EQUALCMPR"
                self.actual.value = (
                    self.origin[self.position-1:self.position+1])
                self.position += 1
            elif(str.lower(self.origin[self.position-1:self.position+1]) == "or"):
                self.actual.Type = "OR"
                self.actual.value = (self.origin[self.position-1])
                self.position += 1
            elif(str.lower(self.origin[self.position-1:self.position+2]) == "and"):
                self.actual.Type = "AND"
                self.actual.value = (self.origin[self.position-1])
                self.position += 2
            elif(self.origin[self.position-1] == "="):
                self.actual.Type = "EQUAL"
                self.actual.value = (self.origin[self.position-1])
            elif(self.origin[self.position-1] == "$"):
                init = self.position-1
                while ((self.origin[self.position] not in list_reserved) and (self.position+1 <= len(self.origin))):
                    self.position += 1
                end = self.position
                if(self.origin[init+1:end] in list_reserved):
                    raise Exception("Error, token reserved: %s" %
                                    self.origin[init+1:end])
                elif(not re.match(r'[$]+[A-Za-z]+[A-Za-z0-9_]*$', self.origin[init:end])):
                    raise Exception("Error, token does not follow the rules of var type. (%s) " % (
                        self.origin[init+1:end]))
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

            elif(Parser.tokens.actual.Type == "STR"):
                val = StringVal(Parser.tokens.actual.value)
                Parser.tokens.selectNext()
                return val

            elif(Parser.tokens.actual.Type == "BOOL"):
                val = BoolVal(Parser.tokens.actual.value)
                Parser.tokens.selectNext()
                return val

            elif (Parser.tokens.actual.Type in ["MINUS", "PLUS", "NOT"]):
                if(Parser.tokens.actual.Type == "MINUS"):
                    un = UnOp("-")
                    un.children = Parser.parseFactor(tokens)
                elif(Parser.tokens.actual.Type == "PLUS"):
                    un = UnOp("+")
                    un.children = Parser.parseFactor(tokens)
                else:
                    un = UnOp("!")
                    un.children = Parser.parseFactor(tokens)
                return un

            elif(Parser.tokens.actual.Type == "FUNCTION_CALL"):
                callFunc = FuncCall(Parser.tokens.actual.value)
                Parser.tokens.selectNext()
                if(Parser.tokens.actual.Type != "OPENPAR"):
                    raise Exception("Error, OPENPAR not found after FUNCTION_CALL")
                if(len(Parser.tokens.origin[Parser.tokens.position:Parser.tokens.origin.find(")", Parser.tokens.position)].strip()) != 0):
                    while (Parser.tokens.actual.Type != "CLOSEPAR"):
                        callFunc.children.append(Parser.parseRelexpr(tokens))
                else:
                    Parser.tokens.selectNext()
                if(Parser.tokens.actual.Type != "CLOSEPAR"):
                    raise Exception(
                        "Error, CLOSEPAR not found after FUNCTION_CALL")
                Parser.tokens.selectNext()
                return callFunc

            elif (Parser.tokens.actual.Type == "OPENPAR"):
                temp = Parser.parseRelexpr(tokens)
                if(Parser.tokens.actual.Type == "CLOSEPAR"):
                    Parser.tokens.selectNext()
                    return temp

            elif(Parser.tokens.actual.Type == "READLINE"):
                un = ReadlineOp()
                Parser.tokens.selectNext()
                if(Parser.tokens.actual.Type == "OPENPAR"):
                    Parser.tokens.selectNext()
                    if(Parser.tokens.actual.Type == "CLOSEPAR"):
                        Parser.tokens.selectNext()
                        return un
                raise Exception("ERROR IN READLINE")

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

        elif(Parser.tokens.actual.Type == "AND"):
            term = BinOp("and")
            term.children.append(temp_value)
            term.children.append(Parser.parseTerm(tokens))

        else:
            return temp_value
        return term

    @staticmethod
    def parseExpression(tokens):
        temp_value = Parser.parseTerm(tokens)
        if(Parser.tokens.actual.Type not in ["EOF"] and Parser.tokens.actual.Type in ["PLUS", "MINUS", "OR", "CONCAT"]):
            if(Parser.tokens.actual.Type == "PLUS"):
                main = BinOp("+")
                main.children.append(temp_value)

            elif(Parser.tokens.actual.Type == "MINUS"):
                main = BinOp("-")
                main.children.append(temp_value)

            elif(Parser.tokens.actual.Type == "OR"):
                main = BinOp("or")
                main.children.append(temp_value)

            elif(Parser.tokens.actual.Type == "CONCAT"):
                main = BinOp(".")
                main.children.append(temp_value)

            main.children.append(Parser.parseExpression(tokens))
            return main
        return temp_value

    @staticmethod
    def parseRelexpr(tokens):
        temp_value = Parser.parseExpression(tokens)
        if(Parser.tokens.actual.Type not in ["EOF"] and Parser.tokens.actual.Type in ["EQUALCMPR", "MORETHAN", "LESSTHAN"]):
            if(Parser.tokens.actual.Type == "EQUALCMPR"):
                main = RelaxOp("==", temp_value)

            elif(Parser.tokens.actual.Type == "MORETHAN"):
                main = RelaxOp(">", temp_value)

            elif(Parser.tokens.actual.Type == "LESSTHAN"):
                main = RelaxOp("<", temp_value)

            main.children.append(Parser.parseRelexpr(tokens))
            return main
        return temp_value

    @staticmethod
    def parseCommand(tokens):
        if(Parser.tokens.actual.Type == "ENDLINE"):
            Parser.tokens.selectNext()
            return NoOp()

        elif(Parser.tokens.actual.Type == "FUNCTION"):
            name = Parser.tokens.actual.value
            list_data = []
            Parser.tokens.selectNext()
            if(Parser.tokens.actual.Type != "OPENPAR"):
                raise Exception(
                    "Error, OPENPAR not found after FUNCTION assignment")
            Parser.tokens.selectNext()
            if(Parser.tokens.actual.Type != "CLOSEPAR"):
                while(Parser.tokens.actual.Type == "IDENTIFIER"):
                    val = IdentifierOp(Parser.tokens.actual.value)
                    list_data.append(val)
                    Parser.tokens.selectNext()
                    if(Parser.tokens.actual.Type not in ["COMMA", "CLOSEPAR"]):
                        raise Exception("Error while creating function call")
                    if(Parser.tokens.actual.Type in ["COMMA"]):
                        Parser.tokens.selectNext()
            Parser.tokens.selectNext()
            list_data.append(Parser.parseCommand(tokens))
            tt = FuncDec(name, list_data)
            return tt

        elif(Parser.tokens.actual.Type == "FUNCTION_CALL"):
            callFunc = FuncCall(Parser.tokens.actual.value)
            Parser.tokens.selectNext()
            if(Parser.tokens.actual.Type != "OPENPAR"):
                raise Exception("Error, OPENPAR not found after FUNCTION_CALL")
            if(len(Parser.tokens.origin[Parser.tokens.position:Parser.tokens.origin.find(")", Parser.tokens.position)].strip()) != 0):
                while (Parser.tokens.actual.Type != "CLOSEPAR"):
                    callFunc.children.append(Parser.parseRelexpr(tokens))
            else:
                Parser.tokens.selectNext()
            if(Parser.tokens.actual.Type != "CLOSEPAR"):
                raise Exception(
                    "Error, CLOSEPAR not found after FUNCTION_CALL")
            Parser.tokens.selectNext()
            return callFunc

        elif(Parser.tokens.actual.Type == "RETURN"):
            child = Parser.parseRelexpr(tokens)
            ret = ReturnOp(child)
            return ret

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

        elif (Parser.tokens.actual.Type == "OPENBLOCK"):
            return Parser.parseBlock(tokens)

        elif(Parser.tokens.actual.Type == "ECHO"):
            ecc = EchoOp(Parser.parseRelexpr(tokens))
            if(Parser.tokens.actual.Type == "ENDLINE"):
                Parser.tokens.selectNext()
            else:
                raise Exception("Missing ';' after IDENTIFIER")
            return ecc

        elif(Parser.tokens.actual.Type == "WHILE"):
            Parser.tokens.selectNext()
            if(Parser.tokens.actual.Type != "OPENPAR"):
                raise Exception("Error, '(' expected")
            whil = WhileOp(Parser.parseRelexpr(tokens))
            if(Parser.tokens.actual.Type != "CLOSEPAR"):
                raise Exception("Error, ')' expected  (%s)" %
                                (Parser.tokens.actual.value))
            Parser.tokens.selectNext()
            whil.children.append(Parser.parseCommand(tokens))

            return whil

        elif(Parser.tokens.actual.Type == "IF"):
            Parser.tokens.selectNext()
            if(Parser.tokens.actual.Type != "OPENPAR"):
                raise Exception("Error, '(' expected")

            iff = IfOp(Parser.parseRelexpr(tokens))
            if(Parser.tokens.actual.Type != "CLOSEPAR"):
                raise Exception("Error, ')' expected  (%s)" %
                                (Parser.tokens.actual.value))
            Parser.tokens.selectNext()
            iff.children.append(Parser.parseCommand(tokens))
            if(Parser.tokens.actual.Type == "ELSE"):
                Parser.tokens.selectNext()
                iff.children.append(Parser.parseCommand(tokens))
            return iff

        else:
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
    def parseProgram(tokens):
        commands = Commands()
        if (Parser.tokens.actual.Type == "PROGOPEN"):
            Parser.tokens.selectNext()
            temp = Parser.parseCommand(tokens)
            commands.children.append(temp)
            while(Parser.tokens.actual.Type != "PROGCLOSE"):
                temp = Parser.parseCommand(tokens)
                commands.children.append(temp)
            Parser.tokens.selectNext()
            return commands
        raise Exception("Error on program definition.")

    @staticmethod
    def run(origin):
        Parser.tokens = Tokenizer(PrePro.filter(origin))

        Parser.tokens.selectNext()
        final = Parser.parseProgram(Parser.tokens)
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
            value = Parser.run(line) 

            global SymbolTableUsed 
            SymbolTableUsed = SymbolTable()
            value.Evaluate()

    else:
        raise Exception("Type error: %s is not a '.php' file" % (file_php))
