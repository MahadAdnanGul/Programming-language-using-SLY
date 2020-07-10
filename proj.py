from sly import Lexer
from sly import Parser

class BasicLexer(Lexer):
    tokens = {NAME, DOUBLE,LIST,INT, STRING, IF, THEN, ELSE, ELSEIF , PRINT, EQEQ , LESSEQ, GREATEQ ,NOTEQ, NOT, AND, OR,DOUBLEPLUS,DOUBLEMINUS, BOOL}
    ignore = '\t '

    literals = { '=', '+', '-', '/', '*', '(', ')', ',', ';','<','>' ,'%' ,'^','.','[',']'}

    # Define tokens
    IF = r'IF'
    THEN = r'THEN'
    ELSEIF=r'ELSEIF'
    ELSE = r'ELSE'
    PRINT = r'print'
    NOT=r'NOT'
    AND=r'AND'
    OR=r'OR'
    BOOL=r'False|True'
   # LIST=r'\[((\d+,)*\d+)\]|\[\]'
    NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
    @_(r'\".*?\"')
    def STRING(self, t):
        t.value=str(t.value)
        return t
    EQEQ = r'=='
    LESSEQ=r'<='
    GREATEQ=r'>='
    NOTEQ=r'!='
    DOUBLEPLUS=r'\+\+'
    DOUBLEMINUS=r'\-\-'


    @_(r'\[((\d+,)*\d+)\]|\[\]',
        r'\[((\".*?\",)*\".*?\")\]|\[\]')
    def LIST(self, t):
        return t

    @_(r'\d+\.\d+')
    def DOUBLE(self, t):
        t.value=float(t.value)
        return t

    @_(r'\d+')
    def INT(self, t):
        t.value = int(t.value)
        return t

    @_(r'#.*')
    def COMMENT(self, t):
        pass

    @_(r'\n+')
    def newline(self,t ):
        self.lineno = t.value.count('\n')

    

class BasicParser(Parser):
    tokens = BasicLexer.tokens

    precedence = (
        ('left', '+', '-'),
        ('left', '*', '/'),
        ('left','^'),
        ('right', 'UMINUS'),
        )

    def __init__(self):
        self.env = { }

    @_('')
    def statement(self, p):
        pass

    @_(r'IF condition THEN statement ELSEIF condition THEN statement ELSE statement')
    def statement(self, p):
        return ('if_elif_stmt', p.condition0,p.condition1,  ('branch', p.statement0, p.statement1,p.statement2))

    @_(r'IF condition THEN statement ELSEIF condition THEN statement')
    def statement(self, p):
        return ('if_elif_stmt_no_else', p.condition0,p.condition1,  ('branch', p.statement0, p.statement1))

    @_(r'IF condition THEN statement ELSE statement')
    def statement(self, p):
        return ('if_stmt', p.condition,  ('branch', p.statement0, p.statement1))

    @_(r'IF condition THEN statement')
    def statement(self, p):
        return ('if_only', p.condition,  ('branch', p.statement))

    @_('PRINT "(" expr ")"')
    def statement(self, p):
        return ('printf', p.expr)

    @_('PRINT "(" expr "," expr ")"')
    def statement(self, p):
        return ('printff', p.expr0,p.expr1)

    @_('PRINT "(" expr "," expr "," expr ")"')
    def statement(self, p):
        return ('printfff', p.expr0,p.expr1,p.expr2)

    @_('NAME "(" ")"')
    def statement(self, p):
        return ('fun_call', p.NAME)

    #LOGICAL OPS

    @_('expr EQEQ expr')
    def condition(self, p):
        return ('condition_eqeq', p.expr0, p.expr1)

    @_('expr LESSEQ expr')
    def condition(self, p):
        return ('condition_lesseq', p.expr0, p.expr1)

    @_('expr GREATEQ expr')
    def condition(self, p):
        return ('condition_greateq', p.expr0, p.expr1)

    @_('expr NOTEQ expr')
    def condition(self, p):
        return ('condition_noteq', p.expr0, p.expr1)

    @_('expr NOT expr')
    def condition(self, p):
        return ('condition_not', p.expr0, p.expr1)

    @_('expr AND expr')
    def condition(self, p):
        return ('condition_and', p.expr0, p.expr1)

    @_('expr OR expr')
    def condition(self, p):
        return ('condition_or', p.expr0, p.expr1)

    @_('expr "<" expr')
    def condition(self, p):
        return ('condition_less', p.expr0, p.expr1)

    @_('expr ">" expr')
    def condition(self, p):
        return ('condition_great', p.expr0, p.expr1)

    @_('"(" expr ")"')
    def expr(self, p):
        return p.expr

    #END LOGICAL OPS


    @_('var_assign')
    def statement(self, p):
        return p.var_assign

    @_('NAME "=" expr')
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.expr)

    @_('NAME DOUBLEPLUS')
    def var_assign(self, p):
        return ('ADD1', p.NAME, 1)

    @_('NAME "=" STRING')
    def var_assign(self, p):
        return ('var_assign', p.NAME, p.STRING[1:-1])


    @_('expr')
    def statement(self, p):
        return (p.expr)

    @_('expr "+" expr')
    def expr(self, p):
        return ('add', p.expr0, p.expr1)

    @_('expr "^" INT')
    def expr(self, p):
        return ('pow', p.expr, p.INT)

    @_('expr "^" DOUBLE')
    def expr(self, p):
        return ('pow', p.expr, p.DOUBLE)
    
    @_('expr "^" expr')
    def expr(self, p):
        return ('pow', p.expr0, p.expr1)

    @_('expr "-" expr')
    def expr(self, p):
        return ('sub', p.expr0, p.expr1)

    @_('expr "*" expr')
    def expr(self, p):
        return ('mul', p.expr0, p.expr1)

    @_('expr "/" expr')
    def expr(self, p):
        return ('div', p.expr0, p.expr1)

    @_('expr "%" expr')
    def expr(self, p):
        return ('rem', p.expr0, p.expr1)

    @_('expr DOUBLEMINUS')
    def expr(self, p):
        return ('SUB1', p.expr)



    @_('"-" expr %prec UMINUS')
    def expr(self, p):
        return ('neg',p.expr)

    @_('NAME')
    def expr(self, p):
        return ('var', p.NAME)

    @_('INT')
    def expr(self, p):
        return ('num', p.INT)

    @_('DOUBLE')
    def expr(self, p):
        return ('float', p.DOUBLE)

    @_('STRING')
    def expr(self, p):
        return ('str', p.STRING[1:-1])

    @_('BOOL')
    def expr(self, p):
        return ('bool', p.BOOL)

    @_('LIST')
    def expr(self, p):
        return ('list', p.LIST)



class BasicExecute:

    def __init__(self, tree, env):
        self.env = env
        result = self.walkTree(tree)
        #if result is not None and isinstance(result, int):
       #     print(result)
        #if result is not None and isinstance(result, float):
       #     print(result)
        #if isinstance(result, str) and result[0] == '"':
         #   print(result)   

    def walkTree(self, node):

        if isinstance(node, int):
            return node
        if isinstance(node, str):
            return node

        if node is None:
            return None

        if node[0] == 'program':
            if node[1] == None:
                self.walkTree(node[2])
            else:
                self.walkTree(node[1])
                self.walkTree(node[2])

        if node[0] == 'num':
            return node[1]

        if node[0] == 'float':
            return node[1]

        if node[0] == 'str':
            return node[1]

        if node[0] == 'bool':
            return node[1]

        if node[0] == 'list':
            return node[1]

        if node[0] == 'if_stmt':
            result = self.walkTree(node[1])
            if result:
                return self.walkTree(node[2][1])
            return self.walkTree(node[2][2])

        if node[0] == 'slice':
            result = self.walkTree(node[1])
            print(type(result))
            x= self.walkTree(node[2])
            y= self.walkTree(node[3])
            print(result)

        if node[0] == 'if_only':
            result = self.walkTree(node[1])
            if result:
                return self.walkTree(node[2][1])

        if node[0] == 'if_elif_stmt':
            result = self.walkTree(node[1])
            if result:
                return self.walkTree(node[3][1])
            result= self.walkTree(node[2])
            if result:
                return self.walkTree(node[3][2])
            return self.walkTree(node[3][3])


        if node[0] == 'if_elif_stmt_no_else':
            result = self.walkTree(node[1])
            if result:
                return self.walkTree(node[3][1])
            result= self.walkTree(node[2])
            if result:
                return self.walkTree(node[3][2])


        if node[0] == 'condition_eqeq':
            return self.walkTree(node[1]) == self.walkTree(node[2])

        if node[0] == 'condition_less':
            return self.walkTree(node[1]) < self.walkTree(node[2])

        if node[0] == 'condition_lesseq':
            return self.walkTree(node[1]) <= self.walkTree(node[2])

        if node[0] == 'condition_great':
            return self.walkTree(node[1]) > self.walkTree(node[2])

        if node[0] == 'condition_greateq':
            return self.walkTree(node[1]) >= self.walkTree(node[2])

        if node[0] == 'condition_noteq':
            return self.walkTree(node[1]) != self.walkTree(node[2])

        if node[0] == 'fun_def':
            self.env[node[1]] = node[2]

        if node[0] == 'printf':
                printer= self.walkTree(node[1])
                print(printer)

        if node[0] == 'printff':
                printer1= self.walkTree(node[1])
                printer2= self.walkTree(node[2])
                print(printer1,printer2)

        if node[0] == 'printfff':
                printer1= self.walkTree(node[1])
                printer2= self.walkTree(node[2])
                printer3= self.walkTree(node[3])
                print(printer1,printer2,printer3)

        if node[0] == 'add':
            return self.walkTree(node[1]) + self.walkTree(node[2])
        elif node[0] == 'sub':
            return self.walkTree(node[1]) - self.walkTree(node[2])
        elif node[0] == 'mul':
            return self.walkTree(node[1]) * self.walkTree(node[2])
        elif node[0] == 'div':
            return self.walkTree(node[1]) / self.walkTree(node[2])
        elif node[0] == 'neg':
            return -self.walkTree(node[1]) 
        elif node[0] == 'rem':
            return self.walkTree(node[1]) % self.walkTree(node[2])
        elif node[0] == 'pow':
            base=self.walkTree(node[1])
            exp=self.walkTree(node[2])
            power=pow(base,exp)
            return  power 


        if node[0] == 'var_assign':
            self.env[node[1]] = self.walkTree(node[2])
            return node[1]

        if node[0] == 'ADD1':
            x=self.walkTree(node[1])
            tree=parser.parse(lexer.tokenize(str(x)+"="+str(x)+"+1"))
            self.walkTree(tree)
        if node[0] == 'var':
            try:
                return self.env[node[1]]
            except LookupError:
                print("Undefined variable '"+node[1]+"' found!")
                return 0


if __name__ == '__main__':
    lexer = BasicLexer()
    parser = BasicParser()
    env = {}
    my_input=open("standard.txt",'r')
    lines=my_input.readlines()
    count=0
    while True:
        try:
            tree=parser.parse(lexer.tokenize(lines[count]))
            BasicExecute(tree,env)
            count=count+1
        except EOFError:
            break
