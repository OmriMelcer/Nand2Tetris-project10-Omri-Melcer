"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from JackTokenizer import JackTokenizer

class CompilationEngine:
    """
    Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: JackTokenizer, output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        self.input_stream = input_stream
        self.output_stream = output_stream
        self.current_type_processed = ""
        self.compile_class()

    def compile_class(self) -> None:
        """Compiles a complete class."""
        # Your code goes here!
        self.input_stream.advance()
        self.output_stream.write("<class>\n")
        self.output_stream.write(f"<keyword> {self.input_stream.keyword()} </keyword>\n")
        self.input_stream.advance()
        self.output_stream.write(f"<identifier> {self.input_stream.identifier()} </identifier>\n")
        self.input_stream.advance()
        self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n")
        self.compile_class_var_dec()
        self.compile_subroutine()
        self.input_stream.advance() #TODO check if needed
        self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n")
        self.output_stream.write("</class>\n")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.compile_a_single_variable_line(True)

    def compile_a_single_variable_line(self, is_class_var_dec: bool) -> None:
        self.input_stream.advance()
        type_of_var = "classVarDec" if is_class_var_dec else "varDec"
        while self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword() in ["static", "field"]:
            self.output_stream.write(f"<{type_of_var}>\n")
            self.output_stream.write(f"<keyword> {self.input_stream.keyword()} </keyword>\n")
            self.input_stream.advance()
            self.output_stream.write(f"<{self.input_stream.type().lower()}>{self.input_stream.identifier()}</{self.input_stream.type().lower()}>\n")
            self.input_stream.advance()
            self.output_stream.write(f"<identifier> {self.input_stream.identifier()} </identifier>\n")
            self.input_stream.advance()
            while self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ",":
                self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n")
                self.input_stream.advance()
                self.output_stream.write(f"<identifier> {self.input_stream.identifier()} </identifier>\n")
                self.input_stream.advance()
            self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n")
            self.output_stream.write(f"</{type_of_var}>\n")
            self.input_stream.advance()

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        while self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword() in ["constructor", "function", "method"]:
            self.output_stream.write("<subroutineDec>\n") # Start of subroutine declaration
            self.output_stream.write(f"<keyword> {self.input_stream.keyword()} </keyword>\n") #type: method, constructor, function
            self.input_stream.advance()
            self.output_stream.write(f"<{self.input_stream.type().lower()}>{self.input_stream.identifier()}</{self.input_stream.type().lower()}>\n") # type: void | type
            self.input_stream.advance()
            self.output_stream.write(f"<identifier> {self.input_stream.identifier()} </identifier>\n") #subroutineName
            self.input_stream.advance()
            self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n") # (
            self.compile_parameter_list()
            self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n") # )
            self.input_stream.advance()
            self.output_stream.write("<subroutineBody>\n")
            self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n") # {
            self.compile_var_dec()
            # self.output_stream.advance()
            self.compile_statements()
            self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n") # }
            self.output_stream.write("</subroutineBody>\n")
            self.output_stream.write("</subroutineDec>\n")
            self.input_stream.advance()

    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.output_stream.write("<parameterList>\n")
        self.input_stream.advance()
        while True:
            self.output_stream.write(f"<{self.input_stream.type().lower()}>{self.input_stream.identifier()}</{self.input_stream.type().lower()}>\n")
            self.input_stream.advance()
            self.output_stream.write(f"<identifier> {self.input_stream.identifier()} </identifier>\n")
            self.input_stream.advance()
            if not (self.input_stream.token_type() == "SYMBOL" and self.input_stream.symbol() == ","):
                break
            self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n")
        self.output_stream.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.compile_a_single_variable_line(False)

    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.output_stream.write("<statements>\n")
        while self.input_stream.token_type() == "KEYWORD" and self.input_stream.keyword() in ["let", "if", "while", "do", "return"]:
            if self.input_stream.keyword() == "let":
                self.compile_let()
            elif self.input_stream.keyword() == "if":
                self.compile_if()
            elif self.input_stream.keyword() == "while":
                self.compile_while()
            elif self.input_stream.keyword() == "do":
                self.compile_do()
            elif self.input_stream.keyword() == "return":
                self.compile_return()
            # TODO: check if advanced is need here.
            self.input_stream.advance()
        self.output_stream.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # Your code goes here!
        self.output_stream.write("<doStatement>\n")
        self.output_stream.write(f"<keyword> {self.input_stream.keyword()} </keyword>\n") #do
        self.compile_subroutine_call()
        self.input_stream.advance()
        self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n") #;
        self.output_stream.write("</doStatement>\n")

    def compile_subroutine_call(self) -> None:
        """
        starts by using advanced i.e in the token before the subroutine call.
        returns at the ) token as current
        """
        self.input_stream.advance()
        self.output_stream.write(f"<identifier> {self.input_stream.identifier()} </identifier>\n")
        class_or_subroutine = self.input_stream.identifier() #className | subroutineName
        self.input_stream.advance()
        self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n")
        while self.input_stream.symbol() == ".":
            self.input_stream.advance()
            self.output_stream.write(f"<identifier> {self.input_stream.identifier()} </identifier>\n")
            self.input_stream.advance()
            self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n") # . or ) in the last iteration
        self.input_stream.advance()
        self.compile_expression_list()
        self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n") # )


    def compile_let(self) -> None:
        """Compiles a let statement."""
        # Your code goes here!
        self.output_stream.write("<letStatement>\n")
        self.output_stream.write(f"<keyword> {self.input_stream.keyword()} </keyword>\n") #let
        self.input_stream.advance()
        self.output_stream.write(f"<identifier> {self.input_stream.identifier()} </identifier>\n") # varName
        self.input_stream.advance()
        self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n") # = or [
        if self.input_stream.symbol() == "[":
            self.input_stream.advance()
            self.compile_expression() #TODO: should finish after the advancing to the ] token
            self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n") # ]
            self.input_stream.advance()
            self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n") # =
        self.input_stream.advance()
        self.compile_expression()
        
        self.output_stream.write(f"<symbol> {self.input_stream.symbol()} </symbol>\n") # ;
        self.output_stream.write("</letStatement>\n")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        # Your code goes here!
        pass

    def compile_return(self) -> None:
        """Compiles a return statement."""
        # Your code goes here!
        pass

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""
        # Your code goes here!
        pass

    def compile_expression(self) -> None:
        """Compiles an expression.
        Should finish at the ) or ] token as current
        starts after advancing to the first token
        """
        # Your code goes here!
        pass

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        # Your code goes here!
        pass

    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # Your code goes here!
        pass
