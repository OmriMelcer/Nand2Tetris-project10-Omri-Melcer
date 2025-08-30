"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of  tokens. The
    tokens may be separated by an arbitrary number of whitesvalidpace characters, 
    and comments, which are ignored. There are three possible comment formats: 
    /* comment until closing */ , /** API comment until closing */ , and 
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs 
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' | 
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' | 
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate 
    file. A compilation unit is a single class. A class is a sequence of tokens 
    structured according to the following context free syntax:
    
    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) 
    - subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement | 
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{' 
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions
    
    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName | 
            varName '['expression']' | subroutineCall | '(' expression ')' | 
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className | 
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'
    
    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_stream.read().splitlines()
        self.input_lines = input_stream.read().splitlines()
        self.current_row_index = -1
        self.current_token = ""
        self.tokens = []
        self.keywords = ['class', 'constructor', 'function', 'method', 'field',
                         'static', 'var', 'int', 'char', 'boolean', 'void', 'true',
                         'false', 'null', 'this', 'let', 'do', 'if', 'else',
                         'while', 'return']
        self.symbols = ['{', '}', '(', ')', '[', ']', '.', ',', ';', '+',
                        '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#']
        self.keywordConstants = ['true', 'false', 'null', 'this']
        self.unaryOps = ['-', '~', '^', '#']
        self.ops = ['+', '-', '*', '/', '&', '|', '<', '>', '=']
        self.lines_length = len(self.input_lines)
        self.current_line_tokens = []

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self.current_row_index < self.lines_length

    def delete_current_command(self) -> None:
        """Deletes the current command."""
        self.input_lines.pop(self.current_row_index)
        self.current_row_index = self.current_row_index - 1
        self.commands_length = self.commands_length - 1

    def advance(self) -> bool:
        """Gets the next token from the input and makes it the current token. 
        This method should be called if has_more_tokens() is true. 
        Initially there is no current token.
        """
        if self.current_line_tokens != []:
            self.current_token = self.current_line_tokens.pop(0)
            return True
        self.current_row_index += 1
        if not self.has_more_tokens():
            return False
        self.current_token = self.input_lines[self.current_row_index]
        if not self.handle_comments_and_blanks():
            return False
        if not self.handle_comment_block():
            return False
        self.current_token = self._remove_comments_and_blanks(self.current_token)
        self.split_line_to_tokens()
        self.current_token = self.current_line_tokens.pop(0)
        return True

    def split_line_to_tokens(self) -> None:
        lst = []
        lst = self.current_token.split()
        word_until_symbol = ""
        for word in lst:
            index = 0
            word_until_symbol = ""
            while (index < len(word)):
                char = word[index]
                if char not in self.symbols:
                    word_until_symbol += char
                else:
                    if word_until_symbol != "":
                        self.current_line_tokens.append(word_until_symbol)
                    word_until_symbol = ""
                    self.current_line_tokens.append(char)
                index += 1
        if word_until_symbol != "":
            self.current_line_tokens.append(word_until_symbol)

    def handle_comment_block(self) -> bool:
        """Handles multi-line comments in the input."""
        if not self.current_token.startswith("/**"):
            return False
        while not self.current_token.endswith("*/"):
            self.delete_current_command()
            self.current_row_index += 1
            if not self.has_more_tokens():
                return False
            self.current_token = self.input_lines[self.current_row_index]
        return True

    def handle_comments_and_blanks(self) -> bool:
        """Handles comments and blank lines in the input."""
        while self.current_token.strip() == "" or self.current_token.startswith("//") or self.current_token.startswith("/*"):
            self.delete_current_command()
            self.current_row_index += 1
            if not self.has_more_tokens():
                return False
            self.current_token = self.input_lines[self.current_row_index]
        return True

    def _remove_comments_and_blanks(self, command: str) -> str:
        """Removes comments and blank lines from the command.

        Args:
            command (str): the command to remove comments and blanks from.

        Returns:
            str: the command without comments.
        """
        if "//" in command:
            return "".join(command.split("//")[0].strip())
        return command
    
    def token_type(self) -> str:
        
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        # Your code goes here!
        if self.current_token in self.keywords:
            return "KEYWORD"
        if self.current_token in self.symbols:
            return "SYMBOL"
        if self.current_token.isdigit():
            return "INT_CONST"
        if self.current_token.startswith('"') and self.current_token.endswith('"'):
            return "STRING_CONST"
        if self.isidentifier():
            return "IDENTIFIER"
        return "UNKNOWN"

    def isidentifier(self) -> bool:
        """
        Checks if the current token is a valid identifier.
        """
        return (not self.current_token[0].isdigit())

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT", 
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", 
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        return self.current_token.upper()

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' | 
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        return self.current_token[0]

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not 
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        return self.current_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        return int(self.current_token)

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double 
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including 
                      double quote or newline '"'
        """
        return self.current_token[1:-1]
