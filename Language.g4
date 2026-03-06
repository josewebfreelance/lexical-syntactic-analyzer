grammar Language;

// --- REGLAS SINTÁCTICAS ---
program : 'program' '{' (declaration | statement)* '}' ;

// Permite 'int x;'
declaration : 'int' ID ';' ;

// Un statement puede ser una asignación, un if, o un bloque de código
statement 
    : assignment 
    | conditional 
    | block
    ;

assignment : ID '=' expr ';' ;

// Corregido: Ahora el IF acepta cualquier statement (incluyendo bloques con {})
conditional 
    : 'if' '(' condition ')' block ('else' block)? 
    ;

// Un bloque permite agrupar múltiples instrucciones entre llaves
block : '{' (declaration | statement)* '}' ;

condition : left=expr op=('>' | '<' | '==' | '!=' | '>=' | '<=') right=expr ;

// Expresiones con precedencia automática por orden de aparición
expr : left=expr op=('*'|'/') right=expr   # MulDiv
     | left=expr op=('+'|'-') right=expr   # AddSub
     | '(' expr ')'                        # Parens
     | ID                                  # Id
     | NUMBER                              # Int
     ;

// --- REGLAS LÉXICAS ---
ID     : [a-zA-Z_][a-zA-Z0-9_]* ;
NUMBER : [0-9]+ ;
WS     : [ \t\r\n]+ -> skip ;
COMMENT: '//' ~[\r\n]* -> skip ;
