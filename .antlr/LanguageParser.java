// Generated from \\wsl.localhost\Ubuntu\home\jomi1\UNIVERSIDAD\compiladores\lexical-syntactic-analyzer\Language.g4 by ANTLR 4.9.2
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.*;
import org.antlr.v4.runtime.tree.*;
import java.util.List;
import java.util.Iterator;
import java.util.ArrayList;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast"})
public class LanguageParser extends Parser {
	static { RuntimeMetaData.checkVersion("4.9.2", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		PROGRAM_R=1, INT_R=2, FLOAT_R=3, STRING_R=4, BOOL_R=5, VOID_R=6, IF_R=7, 
		ELSE_R=8, WHILE_R=9, FOR_R=10, PRINT_R=11, RETURN_R=12, ASSIGN=13, LINEE=14, 
		COMMA=15, GT=16, LT=17, EQ=18, NE=19, GTE=20, LTE=21, AND=22, OR=23, MUL=24, 
		DIV=25, ADD=26, SUB=27, BRACES=28, BRACEE=29, PARS=30, PARE=31, NUMBER=32, 
		FLOAT=33, STRING=34, BOOL=35, ID=36, WS=37, COMMENT=38;
	public static final int
		RULE_program = 0, RULE_declaration = 1, RULE_statement = 2, RULE_type = 3, 
		RULE_variable = 4, RULE_argsFunction = 5, RULE_function = 6, RULE_conditional = 7, 
		RULE_whileStmt = 8, RULE_forStmt = 9, RULE_printStmt = 10, RULE_returnStmt = 11, 
		RULE_assignment = 12, RULE_block = 13, RULE_condition = 14, RULE_expr = 15, 
		RULE_args = 16;
	private static String[] makeRuleNames() {
		return new String[] {
			"program", "declaration", "statement", "type", "variable", "argsFunction", 
			"function", "conditional", "whileStmt", "forStmt", "printStmt", "returnStmt", 
			"assignment", "block", "condition", "expr", "args"
		};
	}
	public static final String[] ruleNames = makeRuleNames();

	private static String[] makeLiteralNames() {
		return new String[] {
			null, "'program'", "'int'", "'float'", "'string'", "'bool'", "'void'", 
			"'if'", "'else'", "'while'", "'for'", "'print'", "'return'", "'='", "';'", 
			"','", "'>'", "'<'", "'=='", "'!='", "'>='", "'<='", "'&&'", "'||'", 
			"'*'", "'/'", "'+'", "'-'", "'{'", "'}'", "'('", "')'"
		};
	}
	private static final String[] _LITERAL_NAMES = makeLiteralNames();
	private static String[] makeSymbolicNames() {
		return new String[] {
			null, "PROGRAM_R", "INT_R", "FLOAT_R", "STRING_R", "BOOL_R", "VOID_R", 
			"IF_R", "ELSE_R", "WHILE_R", "FOR_R", "PRINT_R", "RETURN_R", "ASSIGN", 
			"LINEE", "COMMA", "GT", "LT", "EQ", "NE", "GTE", "LTE", "AND", "OR", 
			"MUL", "DIV", "ADD", "SUB", "BRACES", "BRACEE", "PARS", "PARE", "NUMBER", 
			"FLOAT", "STRING", "BOOL", "ID", "WS", "COMMENT"
		};
	}
	private static final String[] _SYMBOLIC_NAMES = makeSymbolicNames();
	public static final Vocabulary VOCABULARY = new VocabularyImpl(_LITERAL_NAMES, _SYMBOLIC_NAMES);

	/**
	 * @deprecated Use {@link #VOCABULARY} instead.
	 */
	@Deprecated
	public static final String[] tokenNames;
	static {
		tokenNames = new String[_SYMBOLIC_NAMES.length];
		for (int i = 0; i < tokenNames.length; i++) {
			tokenNames[i] = VOCABULARY.getLiteralName(i);
			if (tokenNames[i] == null) {
				tokenNames[i] = VOCABULARY.getSymbolicName(i);
			}

			if (tokenNames[i] == null) {
				tokenNames[i] = "<INVALID>";
			}
		}
	}

	@Override
	@Deprecated
	public String[] getTokenNames() {
		return tokenNames;
	}

	@Override

	public Vocabulary getVocabulary() {
		return VOCABULARY;
	}

	@Override
	public String getGrammarFileName() { return "Language.g4"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public ATN getATN() { return _ATN; }

	public LanguageParser(TokenStream input) {
		super(input);
		_interp = new ParserATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}

	public static class ProgramContext extends ParserRuleContext {
		public TerminalNode PROGRAM_R() { return getToken(LanguageParser.PROGRAM_R, 0); }
		public TerminalNode ID() { return getToken(LanguageParser.ID, 0); }
		public TerminalNode BRACES() { return getToken(LanguageParser.BRACES, 0); }
		public TerminalNode BRACEE() { return getToken(LanguageParser.BRACEE, 0); }
		public List<DeclarationContext> declaration() {
			return getRuleContexts(DeclarationContext.class);
		}
		public DeclarationContext declaration(int i) {
			return getRuleContext(DeclarationContext.class,i);
		}
		public List<StatementContext> statement() {
			return getRuleContexts(StatementContext.class);
		}
		public StatementContext statement(int i) {
			return getRuleContext(StatementContext.class,i);
		}
		public ProgramContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_program; }
	}

	public final ProgramContext program() throws RecognitionException {
		ProgramContext _localctx = new ProgramContext(_ctx, getState());
		enterRule(_localctx, 0, RULE_program);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(34);
			match(PROGRAM_R);
			setState(35);
			match(ID);
			setState(36);
			match(BRACES);
			setState(41);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << INT_R) | (1L << FLOAT_R) | (1L << STRING_R) | (1L << BOOL_R) | (1L << VOID_R) | (1L << IF_R) | (1L << WHILE_R) | (1L << FOR_R) | (1L << PRINT_R) | (1L << RETURN_R) | (1L << BRACES) | (1L << ID))) != 0)) {
				{
				setState(39);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,0,_ctx) ) {
				case 1:
					{
					setState(37);
					declaration();
					}
					break;
				case 2:
					{
					setState(38);
					statement();
					}
					break;
				}
				}
				setState(43);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(44);
			match(BRACEE);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class DeclarationContext extends ParserRuleContext {
		public VariableContext variable() {
			return getRuleContext(VariableContext.class,0);
		}
		public FunctionContext function() {
			return getRuleContext(FunctionContext.class,0);
		}
		public StatementContext statement() {
			return getRuleContext(StatementContext.class,0);
		}
		public DeclarationContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_declaration; }
	}

	public final DeclarationContext declaration() throws RecognitionException {
		DeclarationContext _localctx = new DeclarationContext(_ctx, getState());
		enterRule(_localctx, 2, RULE_declaration);
		try {
			setState(49);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,2,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(46);
				variable();
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(47);
				function();
				}
				break;
			case 3:
				enterOuterAlt(_localctx, 3);
				{
				setState(48);
				statement();
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class StatementContext extends ParserRuleContext {
		public VariableContext variable() {
			return getRuleContext(VariableContext.class,0);
		}
		public FunctionContext function() {
			return getRuleContext(FunctionContext.class,0);
		}
		public ConditionalContext conditional() {
			return getRuleContext(ConditionalContext.class,0);
		}
		public BlockContext block() {
			return getRuleContext(BlockContext.class,0);
		}
		public WhileStmtContext whileStmt() {
			return getRuleContext(WhileStmtContext.class,0);
		}
		public ForStmtContext forStmt() {
			return getRuleContext(ForStmtContext.class,0);
		}
		public PrintStmtContext printStmt() {
			return getRuleContext(PrintStmtContext.class,0);
		}
		public TerminalNode LINEE() { return getToken(LanguageParser.LINEE, 0); }
		public ReturnStmtContext returnStmt() {
			return getRuleContext(ReturnStmtContext.class,0);
		}
		public AssignmentContext assignment() {
			return getRuleContext(AssignmentContext.class,0);
		}
		public StatementContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_statement; }
	}

	public final StatementContext statement() throws RecognitionException {
		StatementContext _localctx = new StatementContext(_ctx, getState());
		enterRule(_localctx, 4, RULE_statement);
		try {
			setState(66);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,3,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(51);
				variable();
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(52);
				function();
				}
				break;
			case 3:
				enterOuterAlt(_localctx, 3);
				{
				setState(53);
				conditional();
				}
				break;
			case 4:
				enterOuterAlt(_localctx, 4);
				{
				setState(54);
				block();
				}
				break;
			case 5:
				enterOuterAlt(_localctx, 5);
				{
				setState(55);
				whileStmt();
				}
				break;
			case 6:
				enterOuterAlt(_localctx, 6);
				{
				setState(56);
				forStmt();
				}
				break;
			case 7:
				enterOuterAlt(_localctx, 7);
				{
				setState(57);
				printStmt();
				setState(58);
				match(LINEE);
				}
				break;
			case 8:
				enterOuterAlt(_localctx, 8);
				{
				setState(60);
				returnStmt();
				setState(61);
				match(LINEE);
				}
				break;
			case 9:
				enterOuterAlt(_localctx, 9);
				{
				setState(63);
				assignment();
				setState(64);
				match(LINEE);
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class TypeContext extends ParserRuleContext {
		public TerminalNode INT_R() { return getToken(LanguageParser.INT_R, 0); }
		public TerminalNode FLOAT_R() { return getToken(LanguageParser.FLOAT_R, 0); }
		public TerminalNode STRING_R() { return getToken(LanguageParser.STRING_R, 0); }
		public TerminalNode BOOL_R() { return getToken(LanguageParser.BOOL_R, 0); }
		public TerminalNode VOID_R() { return getToken(LanguageParser.VOID_R, 0); }
		public TypeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_type; }
	}

	public final TypeContext type() throws RecognitionException {
		TypeContext _localctx = new TypeContext(_ctx, getState());
		enterRule(_localctx, 6, RULE_type);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(68);
			_la = _input.LA(1);
			if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << INT_R) | (1L << FLOAT_R) | (1L << STRING_R) | (1L << BOOL_R) | (1L << VOID_R))) != 0)) ) {
			_errHandler.recoverInline(this);
			}
			else {
				if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
				_errHandler.reportMatch(this);
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class VariableContext extends ParserRuleContext {
		public TypeContext type() {
			return getRuleContext(TypeContext.class,0);
		}
		public TerminalNode ID() { return getToken(LanguageParser.ID, 0); }
		public TerminalNode LINEE() { return getToken(LanguageParser.LINEE, 0); }
		public TerminalNode ASSIGN() { return getToken(LanguageParser.ASSIGN, 0); }
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public VariableContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_variable; }
	}

	public final VariableContext variable() throws RecognitionException {
		VariableContext _localctx = new VariableContext(_ctx, getState());
		enterRule(_localctx, 8, RULE_variable);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(70);
			type();
			setState(71);
			match(ID);
			setState(74);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==ASSIGN) {
				{
				setState(72);
				match(ASSIGN);
				setState(73);
				expr(0);
				}
			}

			setState(76);
			match(LINEE);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ArgsFunctionContext extends ParserRuleContext {
		public List<TypeContext> type() {
			return getRuleContexts(TypeContext.class);
		}
		public TypeContext type(int i) {
			return getRuleContext(TypeContext.class,i);
		}
		public List<TerminalNode> ID() { return getTokens(LanguageParser.ID); }
		public TerminalNode ID(int i) {
			return getToken(LanguageParser.ID, i);
		}
		public List<TerminalNode> COMMA() { return getTokens(LanguageParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(LanguageParser.COMMA, i);
		}
		public ArgsFunctionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_argsFunction; }
	}

	public final ArgsFunctionContext argsFunction() throws RecognitionException {
		ArgsFunctionContext _localctx = new ArgsFunctionContext(_ctx, getState());
		enterRule(_localctx, 10, RULE_argsFunction);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(78);
			type();
			setState(79);
			match(ID);
			setState(86);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==COMMA) {
				{
				{
				setState(80);
				match(COMMA);
				setState(81);
				type();
				setState(82);
				match(ID);
				}
				}
				setState(88);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class FunctionContext extends ParserRuleContext {
		public TypeContext type() {
			return getRuleContext(TypeContext.class,0);
		}
		public TerminalNode ID() { return getToken(LanguageParser.ID, 0); }
		public BlockContext block() {
			return getRuleContext(BlockContext.class,0);
		}
		public TerminalNode PARS() { return getToken(LanguageParser.PARS, 0); }
		public ArgsFunctionContext argsFunction() {
			return getRuleContext(ArgsFunctionContext.class,0);
		}
		public TerminalNode PARE() { return getToken(LanguageParser.PARE, 0); }
		public FunctionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_function; }
	}

	public final FunctionContext function() throws RecognitionException {
		FunctionContext _localctx = new FunctionContext(_ctx, getState());
		enterRule(_localctx, 12, RULE_function);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(89);
			type();
			setState(90);
			match(ID);
			{
			setState(91);
			match(PARS);
			setState(92);
			argsFunction();
			setState(93);
			match(PARE);
			}
			setState(95);
			block();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ConditionalContext extends ParserRuleContext {
		public TerminalNode IF_R() { return getToken(LanguageParser.IF_R, 0); }
		public TerminalNode PARS() { return getToken(LanguageParser.PARS, 0); }
		public ConditionContext condition() {
			return getRuleContext(ConditionContext.class,0);
		}
		public TerminalNode PARE() { return getToken(LanguageParser.PARE, 0); }
		public List<BlockContext> block() {
			return getRuleContexts(BlockContext.class);
		}
		public BlockContext block(int i) {
			return getRuleContext(BlockContext.class,i);
		}
		public TerminalNode ELSE_R() { return getToken(LanguageParser.ELSE_R, 0); }
		public ConditionalContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_conditional; }
	}

	public final ConditionalContext conditional() throws RecognitionException {
		ConditionalContext _localctx = new ConditionalContext(_ctx, getState());
		enterRule(_localctx, 14, RULE_conditional);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(97);
			match(IF_R);
			setState(98);
			match(PARS);
			setState(99);
			condition(0);
			setState(100);
			match(PARE);
			setState(101);
			block();
			setState(104);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==ELSE_R) {
				{
				setState(102);
				match(ELSE_R);
				setState(103);
				block();
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class WhileStmtContext extends ParserRuleContext {
		public TerminalNode WHILE_R() { return getToken(LanguageParser.WHILE_R, 0); }
		public TerminalNode PARS() { return getToken(LanguageParser.PARS, 0); }
		public ConditionContext condition() {
			return getRuleContext(ConditionContext.class,0);
		}
		public TerminalNode PARE() { return getToken(LanguageParser.PARE, 0); }
		public BlockContext block() {
			return getRuleContext(BlockContext.class,0);
		}
		public WhileStmtContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_whileStmt; }
	}

	public final WhileStmtContext whileStmt() throws RecognitionException {
		WhileStmtContext _localctx = new WhileStmtContext(_ctx, getState());
		enterRule(_localctx, 16, RULE_whileStmt);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(106);
			match(WHILE_R);
			setState(107);
			match(PARS);
			setState(108);
			condition(0);
			setState(109);
			match(PARE);
			setState(110);
			block();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ForStmtContext extends ParserRuleContext {
		public TerminalNode FOR_R() { return getToken(LanguageParser.FOR_R, 0); }
		public TerminalNode PARS() { return getToken(LanguageParser.PARS, 0); }
		public List<TerminalNode> LINEE() { return getTokens(LanguageParser.LINEE); }
		public TerminalNode LINEE(int i) {
			return getToken(LanguageParser.LINEE, i);
		}
		public TerminalNode PARE() { return getToken(LanguageParser.PARE, 0); }
		public StatementContext statement() {
			return getRuleContext(StatementContext.class,0);
		}
		public VariableContext variable() {
			return getRuleContext(VariableContext.class,0);
		}
		public List<AssignmentContext> assignment() {
			return getRuleContexts(AssignmentContext.class);
		}
		public AssignmentContext assignment(int i) {
			return getRuleContext(AssignmentContext.class,i);
		}
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public ForStmtContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_forStmt; }
	}

	public final ForStmtContext forStmt() throws RecognitionException {
		ForStmtContext _localctx = new ForStmtContext(_ctx, getState());
		enterRule(_localctx, 18, RULE_forStmt);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(112);
			match(FOR_R);
			setState(113);
			match(PARS);
			setState(116);
			_errHandler.sync(this);
			switch (_input.LA(1)) {
			case INT_R:
			case FLOAT_R:
			case STRING_R:
			case BOOL_R:
			case VOID_R:
				{
				setState(114);
				variable();
				}
				break;
			case ID:
				{
				setState(115);
				assignment();
				}
				break;
			case LINEE:
				break;
			default:
				break;
			}
			setState(118);
			match(LINEE);
			setState(120);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << PARS) | (1L << NUMBER) | (1L << FLOAT) | (1L << STRING) | (1L << BOOL) | (1L << ID))) != 0)) {
				{
				setState(119);
				expr(0);
				}
			}

			setState(122);
			match(LINEE);
			setState(124);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if (_la==ID) {
				{
				setState(123);
				assignment();
				}
			}

			setState(126);
			match(PARE);
			setState(127);
			statement();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class PrintStmtContext extends ParserRuleContext {
		public TerminalNode PRINT_R() { return getToken(LanguageParser.PRINT_R, 0); }
		public TerminalNode PARS() { return getToken(LanguageParser.PARS, 0); }
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public TerminalNode PARE() { return getToken(LanguageParser.PARE, 0); }
		public PrintStmtContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_printStmt; }
	}

	public final PrintStmtContext printStmt() throws RecognitionException {
		PrintStmtContext _localctx = new PrintStmtContext(_ctx, getState());
		enterRule(_localctx, 20, RULE_printStmt);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(129);
			match(PRINT_R);
			setState(130);
			match(PARS);
			setState(131);
			expr(0);
			setState(132);
			match(PARE);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ReturnStmtContext extends ParserRuleContext {
		public TerminalNode RETURN_R() { return getToken(LanguageParser.RETURN_R, 0); }
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public ReturnStmtContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_returnStmt; }
	}

	public final ReturnStmtContext returnStmt() throws RecognitionException {
		ReturnStmtContext _localctx = new ReturnStmtContext(_ctx, getState());
		enterRule(_localctx, 22, RULE_returnStmt);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(134);
			match(RETURN_R);
			setState(136);
			_errHandler.sync(this);
			_la = _input.LA(1);
			if ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << PARS) | (1L << NUMBER) | (1L << FLOAT) | (1L << STRING) | (1L << BOOL) | (1L << ID))) != 0)) {
				{
				setState(135);
				expr(0);
				}
			}

			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class AssignmentContext extends ParserRuleContext {
		public TerminalNode ID() { return getToken(LanguageParser.ID, 0); }
		public TerminalNode ASSIGN() { return getToken(LanguageParser.ASSIGN, 0); }
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public AssignmentContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_assignment; }
	}

	public final AssignmentContext assignment() throws RecognitionException {
		AssignmentContext _localctx = new AssignmentContext(_ctx, getState());
		enterRule(_localctx, 24, RULE_assignment);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(138);
			match(ID);
			setState(139);
			match(ASSIGN);
			setState(140);
			expr(0);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class BlockContext extends ParserRuleContext {
		public TerminalNode BRACES() { return getToken(LanguageParser.BRACES, 0); }
		public TerminalNode BRACEE() { return getToken(LanguageParser.BRACEE, 0); }
		public List<DeclarationContext> declaration() {
			return getRuleContexts(DeclarationContext.class);
		}
		public DeclarationContext declaration(int i) {
			return getRuleContext(DeclarationContext.class,i);
		}
		public List<StatementContext> statement() {
			return getRuleContexts(StatementContext.class);
		}
		public StatementContext statement(int i) {
			return getRuleContext(StatementContext.class,i);
		}
		public BlockContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_block; }
	}

	public final BlockContext block() throws RecognitionException {
		BlockContext _localctx = new BlockContext(_ctx, getState());
		enterRule(_localctx, 26, RULE_block);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(142);
			match(BRACES);
			setState(147);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << INT_R) | (1L << FLOAT_R) | (1L << STRING_R) | (1L << BOOL_R) | (1L << VOID_R) | (1L << IF_R) | (1L << WHILE_R) | (1L << FOR_R) | (1L << PRINT_R) | (1L << RETURN_R) | (1L << BRACES) | (1L << ID))) != 0)) {
				{
				setState(145);
				_errHandler.sync(this);
				switch ( getInterpreter().adaptivePredict(_input,11,_ctx) ) {
				case 1:
					{
					setState(143);
					declaration();
					}
					break;
				case 2:
					{
					setState(144);
					statement();
					}
					break;
				}
				}
				setState(149);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			setState(150);
			match(BRACEE);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ConditionContext extends ParserRuleContext {
		public ConditionContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_condition; }
	 
		public ConditionContext() { }
		public void copyFrom(ConditionContext ctx) {
			super.copyFrom(ctx);
		}
	}
	public static class ComparisonContext extends ConditionContext {
		public Token op;
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
		public TerminalNode GT() { return getToken(LanguageParser.GT, 0); }
		public TerminalNode LT() { return getToken(LanguageParser.LT, 0); }
		public TerminalNode EQ() { return getToken(LanguageParser.EQ, 0); }
		public TerminalNode NE() { return getToken(LanguageParser.NE, 0); }
		public TerminalNode GTE() { return getToken(LanguageParser.GTE, 0); }
		public TerminalNode LTE() { return getToken(LanguageParser.LTE, 0); }
		public ComparisonContext(ConditionContext ctx) { copyFrom(ctx); }
	}
	public static class ParensCondContext extends ConditionContext {
		public TerminalNode PARS() { return getToken(LanguageParser.PARS, 0); }
		public ConditionContext condition() {
			return getRuleContext(ConditionContext.class,0);
		}
		public TerminalNode PARE() { return getToken(LanguageParser.PARE, 0); }
		public ParensCondContext(ConditionContext ctx) { copyFrom(ctx); }
	}
	public static class AndOrContext extends ConditionContext {
		public Token op;
		public List<ConditionContext> condition() {
			return getRuleContexts(ConditionContext.class);
		}
		public ConditionContext condition(int i) {
			return getRuleContext(ConditionContext.class,i);
		}
		public TerminalNode AND() { return getToken(LanguageParser.AND, 0); }
		public TerminalNode OR() { return getToken(LanguageParser.OR, 0); }
		public AndOrContext(ConditionContext ctx) { copyFrom(ctx); }
	}

	public final ConditionContext condition() throws RecognitionException {
		return condition(0);
	}

	private ConditionContext condition(int _p) throws RecognitionException {
		ParserRuleContext _parentctx = _ctx;
		int _parentState = getState();
		ConditionContext _localctx = new ConditionContext(_ctx, _parentState);
		ConditionContext _prevctx = _localctx;
		int _startState = 28;
		enterRecursionRule(_localctx, 28, RULE_condition, _p);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(161);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,13,_ctx) ) {
			case 1:
				{
				_localctx = new ComparisonContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;

				setState(153);
				expr(0);
				setState(154);
				((ComparisonContext)_localctx).op = _input.LT(1);
				_la = _input.LA(1);
				if ( !((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << GT) | (1L << LT) | (1L << EQ) | (1L << NE) | (1L << GTE) | (1L << LTE))) != 0)) ) {
					((ComparisonContext)_localctx).op = (Token)_errHandler.recoverInline(this);
				}
				else {
					if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
					_errHandler.reportMatch(this);
					consume();
				}
				setState(155);
				expr(0);
				}
				break;
			case 2:
				{
				_localctx = new ParensCondContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(157);
				match(PARS);
				setState(158);
				condition(0);
				setState(159);
				match(PARE);
				}
				break;
			}
			_ctx.stop = _input.LT(-1);
			setState(168);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,14,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					if ( _parseListeners!=null ) triggerExitRuleEvent();
					_prevctx = _localctx;
					{
					{
					_localctx = new AndOrContext(new ConditionContext(_parentctx, _parentState));
					pushNewRecursionContext(_localctx, _startState, RULE_condition);
					setState(163);
					if (!(precpred(_ctx, 3))) throw new FailedPredicateException(this, "precpred(_ctx, 3)");
					setState(164);
					((AndOrContext)_localctx).op = _input.LT(1);
					_la = _input.LA(1);
					if ( !(_la==AND || _la==OR) ) {
						((AndOrContext)_localctx).op = (Token)_errHandler.recoverInline(this);
					}
					else {
						if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
						_errHandler.reportMatch(this);
						consume();
					}
					setState(165);
					condition(4);
					}
					} 
				}
				setState(170);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,14,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			unrollRecursionContexts(_parentctx);
		}
		return _localctx;
	}

	public static class ExprContext extends ParserRuleContext {
		public ExprContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_expr; }
	 
		public ExprContext() { }
		public void copyFrom(ExprContext ctx) {
			super.copyFrom(ctx);
		}
	}
	public static class StringExprContext extends ExprContext {
		public TerminalNode STRING() { return getToken(LanguageParser.STRING, 0); }
		public StringExprContext(ExprContext ctx) { copyFrom(ctx); }
	}
	public static class BoolExprContext extends ExprContext {
		public TerminalNode BOOL() { return getToken(LanguageParser.BOOL, 0); }
		public BoolExprContext(ExprContext ctx) { copyFrom(ctx); }
	}
	public static class FloatExprContext extends ExprContext {
		public TerminalNode FLOAT() { return getToken(LanguageParser.FLOAT, 0); }
		public FloatExprContext(ExprContext ctx) { copyFrom(ctx); }
	}
	public static class MulDivContext extends ExprContext {
		public ExprContext left;
		public Token op;
		public ExprContext right;
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
		public TerminalNode MUL() { return getToken(LanguageParser.MUL, 0); }
		public TerminalNode DIV() { return getToken(LanguageParser.DIV, 0); }
		public MulDivContext(ExprContext ctx) { copyFrom(ctx); }
	}
	public static class AddSubContext extends ExprContext {
		public ExprContext left;
		public Token op;
		public ExprContext right;
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
		public TerminalNode ADD() { return getToken(LanguageParser.ADD, 0); }
		public TerminalNode SUB() { return getToken(LanguageParser.SUB, 0); }
		public AddSubContext(ExprContext ctx) { copyFrom(ctx); }
	}
	public static class ParensContext extends ExprContext {
		public TerminalNode PARS() { return getToken(LanguageParser.PARS, 0); }
		public ExprContext expr() {
			return getRuleContext(ExprContext.class,0);
		}
		public TerminalNode PARE() { return getToken(LanguageParser.PARE, 0); }
		public ParensContext(ExprContext ctx) { copyFrom(ctx); }
	}
	public static class FunctionCallContext extends ExprContext {
		public TerminalNode ID() { return getToken(LanguageParser.ID, 0); }
		public TerminalNode PARS() { return getToken(LanguageParser.PARS, 0); }
		public TerminalNode PARE() { return getToken(LanguageParser.PARE, 0); }
		public ArgsContext args() {
			return getRuleContext(ArgsContext.class,0);
		}
		public FunctionCallContext(ExprContext ctx) { copyFrom(ctx); }
	}
	public static class IdContext extends ExprContext {
		public TerminalNode ID() { return getToken(LanguageParser.ID, 0); }
		public IdContext(ExprContext ctx) { copyFrom(ctx); }
	}
	public static class IntContext extends ExprContext {
		public TerminalNode NUMBER() { return getToken(LanguageParser.NUMBER, 0); }
		public IntContext(ExprContext ctx) { copyFrom(ctx); }
	}

	public final ExprContext expr() throws RecognitionException {
		return expr(0);
	}

	private ExprContext expr(int _p) throws RecognitionException {
		ParserRuleContext _parentctx = _ctx;
		int _parentState = getState();
		ExprContext _localctx = new ExprContext(_ctx, _parentState);
		ExprContext _prevctx = _localctx;
		int _startState = 30;
		enterRecursionRule(_localctx, 30, RULE_expr, _p);
		int _la;
		try {
			int _alt;
			enterOuterAlt(_localctx, 1);
			{
			setState(187);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,16,_ctx) ) {
			case 1:
				{
				_localctx = new ParensContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;

				setState(172);
				match(PARS);
				setState(173);
				expr(0);
				setState(174);
				match(PARE);
				}
				break;
			case 2:
				{
				_localctx = new FunctionCallContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(176);
				match(ID);
				setState(177);
				match(PARS);
				{
				setState(179);
				_errHandler.sync(this);
				_la = _input.LA(1);
				if ((((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << PARS) | (1L << NUMBER) | (1L << FLOAT) | (1L << STRING) | (1L << BOOL) | (1L << ID))) != 0)) {
					{
					setState(178);
					args();
					}
				}

				}
				setState(181);
				match(PARE);
				}
				break;
			case 3:
				{
				_localctx = new IdContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(182);
				match(ID);
				}
				break;
			case 4:
				{
				_localctx = new IntContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(183);
				match(NUMBER);
				}
				break;
			case 5:
				{
				_localctx = new FloatExprContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(184);
				match(FLOAT);
				}
				break;
			case 6:
				{
				_localctx = new StringExprContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(185);
				match(STRING);
				}
				break;
			case 7:
				{
				_localctx = new BoolExprContext(_localctx);
				_ctx = _localctx;
				_prevctx = _localctx;
				setState(186);
				match(BOOL);
				}
				break;
			}
			_ctx.stop = _input.LT(-1);
			setState(197);
			_errHandler.sync(this);
			_alt = getInterpreter().adaptivePredict(_input,18,_ctx);
			while ( _alt!=2 && _alt!=org.antlr.v4.runtime.atn.ATN.INVALID_ALT_NUMBER ) {
				if ( _alt==1 ) {
					if ( _parseListeners!=null ) triggerExitRuleEvent();
					_prevctx = _localctx;
					{
					setState(195);
					_errHandler.sync(this);
					switch ( getInterpreter().adaptivePredict(_input,17,_ctx) ) {
					case 1:
						{
						_localctx = new MulDivContext(new ExprContext(_parentctx, _parentState));
						((MulDivContext)_localctx).left = _prevctx;
						pushNewRecursionContext(_localctx, _startState, RULE_expr);
						setState(189);
						if (!(precpred(_ctx, 9))) throw new FailedPredicateException(this, "precpred(_ctx, 9)");
						setState(190);
						((MulDivContext)_localctx).op = _input.LT(1);
						_la = _input.LA(1);
						if ( !(_la==MUL || _la==DIV) ) {
							((MulDivContext)_localctx).op = (Token)_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						setState(191);
						((MulDivContext)_localctx).right = expr(10);
						}
						break;
					case 2:
						{
						_localctx = new AddSubContext(new ExprContext(_parentctx, _parentState));
						((AddSubContext)_localctx).left = _prevctx;
						pushNewRecursionContext(_localctx, _startState, RULE_expr);
						setState(192);
						if (!(precpred(_ctx, 8))) throw new FailedPredicateException(this, "precpred(_ctx, 8)");
						setState(193);
						((AddSubContext)_localctx).op = _input.LT(1);
						_la = _input.LA(1);
						if ( !(_la==ADD || _la==SUB) ) {
							((AddSubContext)_localctx).op = (Token)_errHandler.recoverInline(this);
						}
						else {
							if ( _input.LA(1)==Token.EOF ) matchedEOF = true;
							_errHandler.reportMatch(this);
							consume();
						}
						setState(194);
						((AddSubContext)_localctx).right = expr(9);
						}
						break;
					}
					} 
				}
				setState(199);
				_errHandler.sync(this);
				_alt = getInterpreter().adaptivePredict(_input,18,_ctx);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			unrollRecursionContexts(_parentctx);
		}
		return _localctx;
	}

	public static class ArgsContext extends ParserRuleContext {
		public List<ExprContext> expr() {
			return getRuleContexts(ExprContext.class);
		}
		public ExprContext expr(int i) {
			return getRuleContext(ExprContext.class,i);
		}
		public List<TerminalNode> COMMA() { return getTokens(LanguageParser.COMMA); }
		public TerminalNode COMMA(int i) {
			return getToken(LanguageParser.COMMA, i);
		}
		public ArgsContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_args; }
	}

	public final ArgsContext args() throws RecognitionException {
		ArgsContext _localctx = new ArgsContext(_ctx, getState());
		enterRule(_localctx, 32, RULE_args);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(200);
			expr(0);
			setState(205);
			_errHandler.sync(this);
			_la = _input.LA(1);
			while (_la==COMMA) {
				{
				{
				setState(201);
				match(COMMA);
				setState(202);
				expr(0);
				}
				}
				setState(207);
				_errHandler.sync(this);
				_la = _input.LA(1);
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public boolean sempred(RuleContext _localctx, int ruleIndex, int predIndex) {
		switch (ruleIndex) {
		case 14:
			return condition_sempred((ConditionContext)_localctx, predIndex);
		case 15:
			return expr_sempred((ExprContext)_localctx, predIndex);
		}
		return true;
	}
	private boolean condition_sempred(ConditionContext _localctx, int predIndex) {
		switch (predIndex) {
		case 0:
			return precpred(_ctx, 3);
		}
		return true;
	}
	private boolean expr_sempred(ExprContext _localctx, int predIndex) {
		switch (predIndex) {
		case 1:
			return precpred(_ctx, 9);
		case 2:
			return precpred(_ctx, 8);
		}
		return true;
	}

	public static final String _serializedATN =
		"\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3(\u00d3\4\2\t\2\4"+
		"\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t"+
		"\13\4\f\t\f\4\r\t\r\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22"+
		"\3\2\3\2\3\2\3\2\3\2\7\2*\n\2\f\2\16\2-\13\2\3\2\3\2\3\3\3\3\3\3\5\3\64"+
		"\n\3\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\3\4\5\4E"+
		"\n\4\3\5\3\5\3\6\3\6\3\6\3\6\5\6M\n\6\3\6\3\6\3\7\3\7\3\7\3\7\3\7\3\7"+
		"\7\7W\n\7\f\7\16\7Z\13\7\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\b\3\t\3\t\3\t\3"+
		"\t\3\t\3\t\3\t\5\tk\n\t\3\n\3\n\3\n\3\n\3\n\3\n\3\13\3\13\3\13\3\13\5"+
		"\13w\n\13\3\13\3\13\5\13{\n\13\3\13\3\13\5\13\177\n\13\3\13\3\13\3\13"+
		"\3\f\3\f\3\f\3\f\3\f\3\r\3\r\5\r\u008b\n\r\3\16\3\16\3\16\3\16\3\17\3"+
		"\17\3\17\7\17\u0094\n\17\f\17\16\17\u0097\13\17\3\17\3\17\3\20\3\20\3"+
		"\20\3\20\3\20\3\20\3\20\3\20\3\20\5\20\u00a4\n\20\3\20\3\20\3\20\7\20"+
		"\u00a9\n\20\f\20\16\20\u00ac\13\20\3\21\3\21\3\21\3\21\3\21\3\21\3\21"+
		"\3\21\5\21\u00b6\n\21\3\21\3\21\3\21\3\21\3\21\3\21\5\21\u00be\n\21\3"+
		"\21\3\21\3\21\3\21\3\21\3\21\7\21\u00c6\n\21\f\21\16\21\u00c9\13\21\3"+
		"\22\3\22\3\22\7\22\u00ce\n\22\f\22\16\22\u00d1\13\22\3\22\2\4\36 \23\2"+
		"\4\6\b\n\f\16\20\22\24\26\30\32\34\36 \"\2\7\3\2\4\b\3\2\22\27\3\2\30"+
		"\31\3\2\32\33\3\2\34\35\2\u00e3\2$\3\2\2\2\4\63\3\2\2\2\6D\3\2\2\2\bF"+
		"\3\2\2\2\nH\3\2\2\2\fP\3\2\2\2\16[\3\2\2\2\20c\3\2\2\2\22l\3\2\2\2\24"+
		"r\3\2\2\2\26\u0083\3\2\2\2\30\u0088\3\2\2\2\32\u008c\3\2\2\2\34\u0090"+
		"\3\2\2\2\36\u00a3\3\2\2\2 \u00bd\3\2\2\2\"\u00ca\3\2\2\2$%\7\3\2\2%&\7"+
		"&\2\2&+\7\36\2\2\'*\5\4\3\2(*\5\6\4\2)\'\3\2\2\2)(\3\2\2\2*-\3\2\2\2+"+
		")\3\2\2\2+,\3\2\2\2,.\3\2\2\2-+\3\2\2\2./\7\37\2\2/\3\3\2\2\2\60\64\5"+
		"\n\6\2\61\64\5\16\b\2\62\64\5\6\4\2\63\60\3\2\2\2\63\61\3\2\2\2\63\62"+
		"\3\2\2\2\64\5\3\2\2\2\65E\5\n\6\2\66E\5\16\b\2\67E\5\20\t\28E\5\34\17"+
		"\29E\5\22\n\2:E\5\24\13\2;<\5\26\f\2<=\7\20\2\2=E\3\2\2\2>?\5\30\r\2?"+
		"@\7\20\2\2@E\3\2\2\2AB\5\32\16\2BC\7\20\2\2CE\3\2\2\2D\65\3\2\2\2D\66"+
		"\3\2\2\2D\67\3\2\2\2D8\3\2\2\2D9\3\2\2\2D:\3\2\2\2D;\3\2\2\2D>\3\2\2\2"+
		"DA\3\2\2\2E\7\3\2\2\2FG\t\2\2\2G\t\3\2\2\2HI\5\b\5\2IL\7&\2\2JK\7\17\2"+
		"\2KM\5 \21\2LJ\3\2\2\2LM\3\2\2\2MN\3\2\2\2NO\7\20\2\2O\13\3\2\2\2PQ\5"+
		"\b\5\2QX\7&\2\2RS\7\21\2\2ST\5\b\5\2TU\7&\2\2UW\3\2\2\2VR\3\2\2\2WZ\3"+
		"\2\2\2XV\3\2\2\2XY\3\2\2\2Y\r\3\2\2\2ZX\3\2\2\2[\\\5\b\5\2\\]\7&\2\2]"+
		"^\7 \2\2^_\5\f\7\2_`\7!\2\2`a\3\2\2\2ab\5\34\17\2b\17\3\2\2\2cd\7\t\2"+
		"\2de\7 \2\2ef\5\36\20\2fg\7!\2\2gj\5\34\17\2hi\7\n\2\2ik\5\34\17\2jh\3"+
		"\2\2\2jk\3\2\2\2k\21\3\2\2\2lm\7\13\2\2mn\7 \2\2no\5\36\20\2op\7!\2\2"+
		"pq\5\34\17\2q\23\3\2\2\2rs\7\f\2\2sv\7 \2\2tw\5\n\6\2uw\5\32\16\2vt\3"+
		"\2\2\2vu\3\2\2\2vw\3\2\2\2wx\3\2\2\2xz\7\20\2\2y{\5 \21\2zy\3\2\2\2z{"+
		"\3\2\2\2{|\3\2\2\2|~\7\20\2\2}\177\5\32\16\2~}\3\2\2\2~\177\3\2\2\2\177"+
		"\u0080\3\2\2\2\u0080\u0081\7!\2\2\u0081\u0082\5\6\4\2\u0082\25\3\2\2\2"+
		"\u0083\u0084\7\r\2\2\u0084\u0085\7 \2\2\u0085\u0086\5 \21\2\u0086\u0087"+
		"\7!\2\2\u0087\27\3\2\2\2\u0088\u008a\7\16\2\2\u0089\u008b\5 \21\2\u008a"+
		"\u0089\3\2\2\2\u008a\u008b\3\2\2\2\u008b\31\3\2\2\2\u008c\u008d\7&\2\2"+
		"\u008d\u008e\7\17\2\2\u008e\u008f\5 \21\2\u008f\33\3\2\2\2\u0090\u0095"+
		"\7\36\2\2\u0091\u0094\5\4\3\2\u0092\u0094\5\6\4\2\u0093\u0091\3\2\2\2"+
		"\u0093\u0092\3\2\2\2\u0094\u0097\3\2\2\2\u0095\u0093\3\2\2\2\u0095\u0096"+
		"\3\2\2\2\u0096\u0098\3\2\2\2\u0097\u0095\3\2\2\2\u0098\u0099\7\37\2\2"+
		"\u0099\35\3\2\2\2\u009a\u009b\b\20\1\2\u009b\u009c\5 \21\2\u009c\u009d"+
		"\t\3\2\2\u009d\u009e\5 \21\2\u009e\u00a4\3\2\2\2\u009f\u00a0\7 \2\2\u00a0"+
		"\u00a1\5\36\20\2\u00a1\u00a2\7!\2\2\u00a2\u00a4\3\2\2\2\u00a3\u009a\3"+
		"\2\2\2\u00a3\u009f\3\2\2\2\u00a4\u00aa\3\2\2\2\u00a5\u00a6\f\5\2\2\u00a6"+
		"\u00a7\t\4\2\2\u00a7\u00a9\5\36\20\6\u00a8\u00a5\3\2\2\2\u00a9\u00ac\3"+
		"\2\2\2\u00aa\u00a8\3\2\2\2\u00aa\u00ab\3\2\2\2\u00ab\37\3\2\2\2\u00ac"+
		"\u00aa\3\2\2\2\u00ad\u00ae\b\21\1\2\u00ae\u00af\7 \2\2\u00af\u00b0\5 "+
		"\21\2\u00b0\u00b1\7!\2\2\u00b1\u00be\3\2\2\2\u00b2\u00b3\7&\2\2\u00b3"+
		"\u00b5\7 \2\2\u00b4\u00b6\5\"\22\2\u00b5\u00b4\3\2\2\2\u00b5\u00b6\3\2"+
		"\2\2\u00b6\u00b7\3\2\2\2\u00b7\u00be\7!\2\2\u00b8\u00be\7&\2\2\u00b9\u00be"+
		"\7\"\2\2\u00ba\u00be\7#\2\2\u00bb\u00be\7$\2\2\u00bc\u00be\7%\2\2\u00bd"+
		"\u00ad\3\2\2\2\u00bd\u00b2\3\2\2\2\u00bd\u00b8\3\2\2\2\u00bd\u00b9\3\2"+
		"\2\2\u00bd\u00ba\3\2\2\2\u00bd\u00bb\3\2\2\2\u00bd\u00bc\3\2\2\2\u00be"+
		"\u00c7\3\2\2\2\u00bf\u00c0\f\13\2\2\u00c0\u00c1\t\5\2\2\u00c1\u00c6\5"+
		" \21\f\u00c2\u00c3\f\n\2\2\u00c3\u00c4\t\6\2\2\u00c4\u00c6\5 \21\13\u00c5"+
		"\u00bf\3\2\2\2\u00c5\u00c2\3\2\2\2\u00c6\u00c9\3\2\2\2\u00c7\u00c5\3\2"+
		"\2\2\u00c7\u00c8\3\2\2\2\u00c8!\3\2\2\2\u00c9\u00c7\3\2\2\2\u00ca\u00cf"+
		"\5 \21\2\u00cb\u00cc\7\21\2\2\u00cc\u00ce\5 \21\2\u00cd\u00cb\3\2\2\2"+
		"\u00ce\u00d1\3\2\2\2\u00cf\u00cd\3\2\2\2\u00cf\u00d0\3\2\2\2\u00d0#\3"+
		"\2\2\2\u00d1\u00cf\3\2\2\2\26)+\63DLXjvz~\u008a\u0093\u0095\u00a3\u00aa"+
		"\u00b5\u00bd\u00c5\u00c7\u00cf";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}