grammar Language;

// --- REGLAS SINTÁCTICAS ---
program: PROGRAM_R ID BRACES (declaration | statement)* BRACEE;

// Permite 'int x;'
declaration: variable | function | statement;

// Un statement puede ser una asignación, un if, o un bloque de código
statement:
	variable
	| function
	| conditional
	| block
	| whileStmt
	| forStmt
	| printStmt LINEE
	| returnStmt LINEE
	| assignment LINEE;

type: INT_R | FLOAT_R | STRING_R | BOOL_R | VOID_R;

variable: type ID (ASSIGN expr)? LINEE;

// Permite múltiples argumentos separados por comas
argsFunction: type ID (COMMA type ID)*;
function: type ID (PARS argsFunction PARE) block;

conditional: IF_R PARS condition PARE block (ELSE_R block)?;
whileStmt: WHILE_R PARS condition PARE block;
forStmt:
	FOR_R PARS (variable | assignment)? LINEE expr? LINEE assignment? PARE statement;
printStmt: PRINT_R PARS expr PARE;
returnStmt: RETURN_R expr?;

assignment: ID ASSIGN expr;

// Un bloque permite agrupar múltiples instrucciones entre llaves
block: BRACES (declaration | statement)* BRACEE;

condition:
	condition op = (AND | OR) condition					# AndOr
	| expr op = (GT | LT | EQ | NE | GTE | LTE) expr	# Comparison
	| PARS condition PARE								# ParensCond;

// Expresiones con precedencia automática por orden de aparición
expr:
	left = expr op = (MUL | DIV) right = expr	# MulDiv
	| left = expr op = (ADD | SUB) right = expr	# AddSub
	| PARS expr PARE							# Parens
	| ID PARS (args?) PARE						# FunctionCall
	| ID										# Id
	| NUMBER									# Int
	| FLOAT										# FloatExpr
	| STRING									# StringExpr
	| BOOL										# BoolExpr;

args: expr (COMMA expr)*;

// --- REGLAS LÉXICAS ---
PROGRAM_R: 'program';
INT_R: 'int';
FLOAT_R: 'float';
STRING_R: 'string';
BOOL_R: 'bool';
VOID_R: 'void';
IF_R: 'if';
ELSE_R: 'else';
WHILE_R: 'while';
FOR_R: 'for';
PRINT_R: 'print';
RETURN_R: 'return';
ASSIGN: '=';
LINEE: ';';
COMMA: ',';
GT: '>';
LT: '<';
EQ: '==';
NE: '!=';
GTE: '>=';
LTE: '<=';
AND: '&&';
OR: '||';
MUL: '*';
DIV: '/';
ADD: '+';
SUB: '-';
BRACES: '{';
BRACEE: '}';
PARS: '(';
PARE: ')';
NUMBER: [0-9]+;
FLOAT: [0-9]+ '.' [0-9]+;
STRING: '"' (~["\r\n])* '"';
BOOL: 'true' | 'false';
ID: [a-zA-Z][a-zA-Z0-9]*;
WS: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;