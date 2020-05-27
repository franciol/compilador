import sys
import re
from abc import abstractmethod, ABC


list_reserved = ['echo', '$', ';', '=', '+', '-', '/', '*', 'if', 'else', ' ',
                 'while', 'readline', 'and', 'or', '<', '>', '==', '!', '(', ')', 'true', 'false', "."]

id_base = 0
class ASM_JUNCT():
    lista = ['; constantes',
             'SYS_EXIT equ 1',
             'SYS_READ equ 3',
             'SYS_WRITE equ 4',
             'STDIN equ 0',
             'STDOUT equ 1',
             'True equ 1',
             'False equ 0',
             'segment .data',
             'segment .bss  ; variaveis',
             'res RESB 1',

             'section .text',
             'global _start',

             'print:  ; subrotina print',

             'PUSH EBP ; guarda o base pointer',
             'MOV EBP, ESP ; estabelece um novo base pointer',

             'MOV EAX, [EBP+8] ; 1 argumento antes do RET e EBP',
             'XOR ESI, ESI',

             'print_dec: ; empilha todos os digitos',
             'MOV EDX, 0',
             'MOV EBX, 0x000A',
             'DIV EBX',
             "ADD EDX, '0'",
             'PUSH EDX',
             'INC ESI ; contador de digitos',
             'CMP EAX, 0',
             'JZ print_next ; quando acabar pula',
             'JMP print_dec',


             'print_next:',
             'CMP ESI, 0',
             'JZ print_exit; quando acabar de imprimir',
             'DEC ESI',

             'MOV EAX, SYS_WRITE',
             'MOV EBX, STDOUT',

             'POP ECX',
             'MOV[res], ECX',
             'MOV ECX, res',

             'MOV EDX, 1',
             'INT 0x80',
             'JMP print_next',

             'print_exit:',
             'POP EBP',
             'RET',

             '; subrotinas if/while',
             'binop_je:',
             'JE binop_true',
             'JMP binop_false',

             'binop_jg:',
             'JG binop_true',
             'JMP binop_false',

             'binop_jl:',
             'JL binop_true',
             'JMP binop_false',

             'binop_false:',
             'MOV EBX, False',
             'JMP binop_exit',
             'binop_true:',
             'MOV EBX, True',
             'binop_exit:',
             'RET',

             '_start:',

             'PUSH EBP; guarda o base pointer',
             'MOV EBP, ESP; estabelece um novo base pointer']

    def add_lista(self, str):
        self.lista.append(str)

    def flush(self):
        self.add_lista("POP EBP")
        self.add_lista("MOV EAX, 1")
        self.add_lista("INT 0x80")
        return '\n'.join(self.lista)


class SymbolTable():
    mainDict = {}
    displacement = [4]

    def setter(self, chave, valor, tipo):
        self.mainDict[chave] = valor, tipo

    def getter(self, chave):
        return self.mainDict[chave]
    
    def exist(self,chave):
        return (chave in self.mainDict)

    def getDisplacement(self):
        temp = self.displacement[0]
        self.displacement[0] += 4
        return temp


class Node(ABC):
    value = None
    children = None
    
    def newId(self):
        global id_base
        id_base += 1
        return id_base

    @abstractmethod
    def Evaluate(self):
        pass


class BinOp(Node):
    def __init__(self, value):
        self.children = []
        self.value = value

    def Evaluate(self):
        # BIN OP
        '''
        EVALUATE child1

        PUSH EBX ; guarda na Pilha  o valor de child1

        Evaluate child2

        POP EAX;
        ADD EAX, EBX;
        MOV EBX, EAX;

        '''

        self.children[0].Evaluate()
        ASM_JUNCT().add_lista("PUSH EBX ;")
        self.children[1].Evaluate()
        ASM_JUNCT().add_lista("POP EAX ;")
        if(self.value in ['+','-','/','*','and','or']):
            if(self.value == '+'):
                ASM_JUNCT().add_lista("ADD EAX, EBX ;")
            elif(self.value == '-'):
                ASM_JUNCT().add_lista("SUB EAX, EBX ;")
            elif(self.value == '*'):
                ASM_JUNCT().add_lista("IMUL EBX ;")
            elif(self.value == '/'):
                ASM_JUNCT().add_lista("IDIV EBX ;")
            elif(self.value == 'and'):
                ASM_JUNCT().add_lista("AND EAX, EBX ;")
            elif(self.value == 'or'):
                ASM_JUNCT().add_lista("OR EAX, EBX ;")
            ASM_JUNCT().add_lista("MOV EBX, EAX ;")
        else:
            raise Exception("Error in BinOp: Value unexpected")


class UnOp(Node):
    def __init__(self, value):
        self.value = value
        self.ID = super().newId()

    def Evaluate(self):
        if(self.value in ['-','+','!']):
            self.children.Evaluate()
            if(self.value == '-'):
                ASM_JUNCT().add_lista("XOR EBX, 0xFFFFFFFF ; ")
                ASM_JUNCT().add_lista("ADD EBX, 1 ; ")
            elif(self.value == '!'):
                jmp_point = 'UNOP_%d' % (self.ID)
                ASM_JUNCT().add_lista("CMP EBX, 0 ;")
                ASM_JUNCT().add_lista("JE %s ;" % jmp_point)
                ASM_JUNCT().add_lista("MOV EBX, 1 ;")
                ASM_JUNCT().add_lista("%s:" % jmp_point)
                
                

        else:
            raise Exception("Error in UnOp: Value unexpected")


class IntVal(Node):
    def __init__(self, value):
        self.children = None
        self.value = value

    def Evaluate(self):
        # MOV EBX, self.value\n;
        ASM_JUNCT().add_lista("MOV EBX, %d ;"%(self.value))
        # return self.value, "INT"


class BoolVal(Node):
    def __init__(self, value):
        self.children = None
        self.value = value

    def Evaluate(self):
        ASM_JUNCT().add_lista("MOV EBX, %s ;"%(self.value))
        #return self.value, "BOOL"




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
    def __init__(self, value):
        self.children = None
        self.value = value

    def Evaluate(self):
        '''

        '''
        ASM_JUNCT().add_lista("MOV EBX, [EBP-%d] ; " % SymbolTable().getter(self.value)[0])
                



class AssingnmentOp(Node):
    def __init__(self, IDENTIFIER):
        self.children = [IDENTIFIER]
        self.value = None

    def Evaluate(self):
        temp_val = 0
        if( SymbolTable().exist(self.children[0])):
            temp_val = SymbolTable().getter(self.children[0])[0]
        else:
            ASM_JUNCT().add_lista("PUSH DWORD 0 ;")
            temp_val = SymbolTable().getDisplacement()
            SymbolTable().setter(self.children[0], temp_val, "INT")

        self.children[1].Evaluate()
        ASM_JUNCT().add_lista("MOV [EBP-%d], EBX ;" % temp_val)
        


class EchoOp(Node):
    def __init__(self, Expression):
        self.children = Expression
        self.value = None

    def Evaluate(self):
        self.children.Evaluate()
        ASM_JUNCT().add_lista("PUSH EBX ;")
        ASM_JUNCT().add_lista("CALL print ;")
        ASM_JUNCT().add_lista("POP EBX ;")


class WhileOp(Node):
    def __init__(self, expr):
        self.value = None
        self.children = [expr]
        self.ID = super().newId()

    def Evaluate(self):
        ASM_JUNCT().add_lista("LOOP_%d:" % self.ID)
        self.children[0].Evaluate()
        ASM_JUNCT().add_lista("CMP EBX, False ;")
        ASM_JUNCT().add_lista("JE EXIT_%d ;" % (self.ID))
        self.children[1].Evaluate()
        ASM_JUNCT().add_lista("JMP LOOP_%d" % (self.ID))
        ASM_JUNCT().add_lista("EXIT_%d:" % self.ID)


class IfOp(Node):
    def __init__(self, child1):
        self.value = None
        self.children = [child1]
        self.ID = super().newId()

    def Evaluate(self):
        if(len(self.children) == 3):
            self.children[0].Evaluate()
            ASM_JUNCT().add_lista("CMP EBX, False ;")
            ASM_JUNCT().add_lista("JE ELSE_%d ;" % (self.ID))
            self.children[1].Evaluate()
            ASM_JUNCT().add_lista("JMP EXIT_%d ;" % (self.ID))
            ASM_JUNCT().add_lista("ELSE_%d:" % (self.ID))
            self.children[2].Evaluate()
            ASM_JUNCT().add_lista("EXIT_%d:" % (self.ID))
        else:
            self.children[0].Evaluate()
            ASM_JUNCT().add_lista("CMP EBX, False ;")
            ASM_JUNCT().add_lista("JE EXIT_%d ;" % (self.ID))
            self.children[1].Evaluate()
            ASM_JUNCT().add_lista("EXIT_%d:" % (self.ID))


class RelaxOp(Node):
    def __init__(self, value, first):
        self.value = value
        self.children = [first]
        self.ID = super().newId()

    def Evaluate(self):
        self.children[0].Evaluate()
        ASM_JUNCT().add_lista("PUSH EBX ;")
        self.children[1].Evaluate()
        ASM_JUNCT().add_lista("POP EAX ;")
        ASM_JUNCT().add_lista("CMP EBX, EAX ;")
        
        if(self.value == "=="):
            ASM_JUNCT().add_lista("jne FALSE_%d" % self.ID)
        elif(self.value == ">"):
            ASM_JUNCT().add_lista("jge FALSE_%d" % self.ID)
        elif(self.value == "<"):
            ASM_JUNCT().add_lista("jle FALSE_%d" % self.ID)
        ASM_JUNCT().add_lista("MOV EBX, True ; ")
        ASM_JUNCT().add_lista("JMP END_%d " % self.ID)
        ASM_JUNCT().add_lista("FALSE_%d:" % self.ID)
        ASM_JUNCT().add_lista("MOV EBX, False ; ")
        ASM_JUNCT().add_lista("END_%d:" % self.ID)
        

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
            while((self.origin[self.position-1: self.position] == ' ') and (self.position < (len(self.origin)))):
                self.position += 1

            if(self.position > len(self.origin)):
                self.actual.Type = "EOF"
                self.actual.value = ""

            elif(self.origin[self.position-1: self.position+4] == "<?php"):
                self.actual.Type = "PROGOPEN"
                self.actual.value = self.origin[self.position -
                                                1: self.position+4]
                self.position += 4
            elif(self.origin[self.position-1: self.position+1] == "?>"):
                self.actual.Type = "PROGCLOSE"
                self.actual.value = self.origin[self.position -
                                                1: self.position+1]
                self.position += 1

            elif((self.origin[self.position-1: self.position+3]).lower() == "true"):
                self.actual.Type = "BOOL"
                self.actual.value = self.origin[self.position -
                                                1: self.position+3]
                self.position += 3

            elif((self.origin[self.position-1: self.position+4]).lower() == "false"):
                self.actual.Type = "BOOL"
                self.actual.value = self.origin[self.position -
                                                1: self.position+4]
                self.position += 4

            elif(self.origin[self.position-1].isdigit()):
                init = self.position-1
                while (self.origin[init: self.position+1].isdigit() and (self.position+1 <= len(self.origin))):
                    self.position += 1
                end = self.position
                self.actual.Type = "INT"
                self.actual.value = int(self.origin[init: end])
            elif(self.origin[self.position-1] == '"'):
                init = self.position-1
                while (self.origin[self.position+1] != '"'):
                    self.position += 1
                end = self.position + 1
                self.actual.Type = "STR"
                self.actual.value = str(self.origin[init+1: end])
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
            elif(str.lower(self.origin[self.position-1: self.position+3]) == "echo"):
                self.actual.Type = "ECHO"
                self.actual.value = ("echo")
                self.position += 3
            elif(str.lower(self.origin[self.position-1: self.position+3]) == "else"):
                self.actual.Type = "ELSE"
                self.actual.value = (self.origin[self.position-1])
                self.position += 3
            elif(str.lower(self.origin[self.position-1: self.position+1]) == "if"):
                self.actual.Type = "IF"
                self.actual.value = (self.origin[self.position-1])
                self.position += 1
            elif(str.lower(self.origin[self.position-1: self.position+4]) == "while"):
                self.actual.Type = "WHILE"
                self.actual.value = (self.origin[self.position-1])
                self.position += 4
            elif(str.lower(self.origin[self.position-1: self.position+7]) == "readline"):
                self.actual.Type = "READLINE"
                self.actual.value = (self.origin[self.position-1])
                self.position += 7
            elif(str.lower(self.origin[self.position-1: self.position+1]) == "=="):
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

            elif (Parser.tokens.actual.Type == "OPENPAR"):
                temp = Parser.parseRelexpr(tokens)
                if(Parser.tokens.actual.Type == "CLOSEPAR"):
                    Parser.tokens.selectNext()
                    return temp

          
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
            term.children.append(Parser.parseFactor(tokens))

        elif(Parser.tokens.actual.Type == "DIV"):
            term = BinOp("/")
            term.children.append(temp_value)
            term.children.append(Parser.parseFactor(tokens))

        elif(Parser.tokens.actual.Type == "AND"):
            term = BinOp("and")
            term.children.append(temp_value)
            term.children.append(Parser.parseFactor(tokens))

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

            main.children.append(Parser.parseTerm(tokens))
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
            # line = line.replace(' ', '')
            value = Parser.run(line)
            value.Evaluate()
        print(ASM_JUNCT().flush())
    else:
        raise Exception("Type error: %s is not a '.php' file" % (file_php))
