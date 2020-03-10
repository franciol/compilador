import sys
import re


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
            elif(self.origin[self.position-1] == " "):
                goAgain = True
            else:
                raise Exception(
                    "ERRO", "Operando '%s' não reconhecido na posição %d" % (self.origin[self.position-1], self.position-1))


class Parser:

    tokens = None

    @staticmethod
    def parseTerm(tokens):
        Parser.tokens.selectNext()
        try:
            if(Parser.tokens.actual.Type == "INT"):
                endValue = Parser.tokens.actual.value
                Parser.tokens.selectNext()
                while (Parser.tokens.actual.Type == "DIV" or Parser.tokens.actual.Type == "MULT"):
                    if(Parser.tokens.actual.Type == "MULT"):
                        Parser.tokens.selectNext()
                        if(Parser.tokens.actual.Type == "INT"):
                            endValue *= Parser.tokens.actual.value
                        else:
                            raise Exception("ERRO", "Sintaxe incorreta")
                    elif(Parser.tokens.actual.Type == "DIV"):
                        Parser.tokens.selectNext()
                        if(Parser.tokens.actual.Type == "INT"):
                            endValue //= Parser.tokens.actual.value
                        else:
                            raise Exception("Erro", "Sintaxe incorreta")

                    Parser.tokens.selectNext()

                return endValue

            else:
                raise Exception("Error", "")
                exit(0)
        except Exception as e:
            print(e)

    @staticmethod
    def parseExpression(tokens):
        temp_value = Parser.parseTerm(tokens)
        while(Parser.tokens.actual.Type == "PLUS" or Parser.tokens.actual.Type == "MINUS"):
            if(Parser.tokens.actual.Type == "PLUS"):
                temp_value += Parser.parseTerm(tokens)
            elif(Parser.tokens.actual.Type == "MINUS"):
                temp_value -= Parser.parseTerm(tokens)
        return temp_value

    @staticmethod
    def run(origin):
        Parser.tokens = Tokenizer(PrePro.filter(origin))
        final = Parser.parseExpression(Parser.tokens)
        if(Parser.tokens.actual.Type == "EOF"):
            return final
        else:
            raise Exception("Erro", "Input is wrong at position %d (%s) " % (Parser.tokens.position-1,Parser.tokens.origin[Parser.tokens.position-1]))


class PrePro:

    @staticmethod
    def filter(origin):
        pattern = re.compile("/\*.*?\*/", re.DOTALL | re.MULTILINE)
        line = pattern.sub("", origin)
        return line


if __name__ == '__main__':
    value = Parser.run(sys.argv[1])
    print(value)
