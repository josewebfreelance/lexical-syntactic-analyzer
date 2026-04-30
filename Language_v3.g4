grammar Language_v3;

// --- REGLAS SINTÁCTICA ---
program: (importStmt)* PROGRAM_R ID BRACES (declaration | statement)* BRACEE;

importStmt: IMPORT_R ID LINEE;
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
	| breakStmt LINEE
	| continueStmt LINEE
	| assignment LINEE;

varType: (INT_R | FLOAT_R | STRING_R | BOOL_R | VOID_R) (BRACKETS)?;

variable: varType ID (ASSIGN expr)? LINEE;

// Permite múltiples argumentos separados por comas
argsFunction: varType ID (COMMA varType ID)*;
function: varType ID (PARS argsFunction PARE) block;

conditional: IF_R PARS condition PARE block (ELSE_R block)?;
whileStmt: WHILE_R PARS condition PARE block;
forStmt:
	FOR_R PARS (variable | assignment)? LINEE (condition | expr)? LINEE assignment? PARE statement;
printStmt: PRINT_R PARS expr PARE;
returnStmt: RETURN_R expr?;

breakStmt: BREAK_R;
continueStmt: CONTINUE_R;

assignment: 
	ID ASSIGN expr
	| ID BRACKS expr BRACKE ASSIGN expr; // Asignación a índice de arreglo

// Un bloque permite agrupar múltiples instrucciones entre llaves
block: BRACES (declaration | statement)* BRACEE;

condition:
	condition op = (AND | OR) condition					# AndOr
	| expr op = (GT | LT | EQ | NE | GTE | LTE) expr	# Comparison
	| PARS condition PARE								# ParensCond;

// Expresiones con precedencia automática por orden de aparición
expr:
	left = expr op = (MUL | DIV | MOD) right = expr	# MulDivMod
	| left = expr op = (ADD | SUB) right = expr	# AddSub
	| PARS expr PARE							# Parens
	| ID PARS (args?) PARE						# FunctionCall
	| ID BRACKS expr BRACKE						# ArrayAccess
	| BRACKS (expr (COMMA expr)*)? BRACKE		# ArrayLit
	| (INT_R | FLOAT_R | STRING_R | BOOL_R) BRACKS expr BRACKE # ArrayNew
	| ID										# Id
	| NUMBER									# Int
	| FLOAT										# FloatExpr
	| STRING									# StringExpr
	| BOOL										# BoolExpr;

args: expr (COMMA expr)*;

// --- REGLAS LÉXICAS ---
PROGRAM_R: 'program';
IMPORT_R: 'import';
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
BREAK_R: 'break';
CONTINUE_R: 'continue';
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
MOD: '%';
ADD: '+';
SUB: '-';
BRACES: '{';
BRACEE: '}';
PARS: '(';
PARE: ')';
BRACKETS: '[]';
BRACKS: '[';
BRACKE: ']';
NUMBER: [0-9]+;
FLOAT: [0-9]+ '.' [0-9]+;
STRING: '"' (~["\r\n])* '"';
BOOL: 'true' | 'false';
ID: [a-zA-Z][a-zA-Z0-9]*;
WS: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;