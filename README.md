# compilador

Diagrama Sintático

![alt text](DiagramaSintatico.png)

EBNF

> PROGRAM = '<?php , { COMMAND } , '?>' ;

> BLOCK = '{', { COMMAND }, '}' ;

> COMMAND = ( λ | ASSIGNMENT | PRINT ), ';' | BLOCK | LOOP | CONDITIONAL ;

> ASSIGNMENT = IDENTIFIER, '=', RELEXPR, ';' ;

> PRINT = 'echo', RELEXPR, ';' ;

> LOOP = 'while' , '(' , RELEXPR , ')' , COMMAND ;

> CONDITIONAL = 'if' , '(', RELEXPR , ')' , COMMAND , λ | ('else' , COMMAND )

> RELEXPR = EXPRESSION, { ('==' | '>' | '<' ) , EXPRESSION} ;

> EXPRESSION = TERM, { ('+' | '-' | 'or' | '.'), TERM } ;

> TERM = FACTOR, { ('\*' | '/' | 'and' ), FACTOR } ;

> FACTOR = (('+' | '-' | '!' ), FACTOR) | NUMBER | '(', RELEXPR, ')' | IDENTIFIER | 'readline()' | STRING | BOOL;

> IDENTIFIER = '\$', LETTER, { LETTER | DIGIT | '\_' } ;

> NUMBER = DIGIT, { DIGIT } ;

> STRING = '"', ((' ' | LETTER | DIGIT | '_' ) , { ( ' ' | LETTER | DIGIT | '_') });

> LETTER = ( a | ... | z | A | ... | Z ) ;

> DIGIT = ( 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 0 ) ;

> BOOL = ( True | False) ;
