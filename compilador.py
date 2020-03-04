import sys


class Token:
    Type = None
    value = None


class Tokenizer:
    # 4 Tipos de Tokens:
    # INT
    # PLUS
    # MINUS
    # EOF

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
            elif(self.origin[self.position-1] == " "):
                goAgain = True
            else:
                raise Exception(
                    "ERRO", "Operando '%s' não reconhecido na posição %d" % (self.origin[self.position-1], self.position-1))


class Parser:

    tokens = None

    @staticmethod
    def parseExpression(tokens):
        # Consome tokens do Tokenizer e analisa se a sintaxe esta aderente à gramatica proposta
        Parser.tokens.selectNext()
        try:
            if(Parser.tokens.actual.Type == "INT"):
                endValue = Parser.tokens.actual.value
                Parser.tokens.selectNext()

                while (Parser.tokens.actual.Type == "PLUS" or Parser.tokens.actual.Type == "MINUS"):
                    if(Parser.tokens.actual.Type == "PLUS"):
                        Parser.tokens.selectNext()
                        if(Parser.tokens.actual.Type == "INT"):
                            endValue += Parser.tokens.actual.value
                        else:
                            raise Exception("ERRO", "Sintaxe incorreta")
                    elif(Parser.tokens.actual.Type == "MINUS"):
                        Parser.tokens.selectNext()
                        if(Parser.tokens.actual.Type == "INT"):
                            endValue -= Parser.tokens.actual.value
                        else:
                            raise Exception("Erro", "Sintaxe incorreta")

                    Parser.tokens.selectNext()

                return endValue

        except Exception as e:
            print(e)

    @staticmethod
    def run(origin):
        Parser.tokens = Tokenizer(origin)
        return Parser.parseExpression(Parser.tokens)
        # recebe origin e inicializa um objeto tokenizer e retorna o resultado de parseExpression
        # Sera chamado pelo main()


if __name__ == '__main__':
    value = Parser.run(sys.argv[1])
    print(value)
