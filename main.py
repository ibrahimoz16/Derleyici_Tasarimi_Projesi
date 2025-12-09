import re
import sys
import os

# Token sınıfı
class Token:
    def __init__(self, type_, value):
        self.type = type_
        self.value = value
    
    def __str__(self):
        return f"{self.type}('{self.value}')" if self.value != '' else f"{self.type}"

# Lexer sınıfı
class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.text else None
        self.tokens = []
        
        # Token tanımlamaları
        self.token_patterns = [
            ('INT', r'int'),
            ('PRINT', r'print'),
            ('ID', r'[a-zA-Z][a-zA-Z0-9]*'),
            ('NUMBER', r'[0-9]+'),
            ('ASSIGN', r'='),
            ('PLUS', r'\+'),
            ('MINUS', r'-'),
            ('MULT', r'\*'),
            ('DIV', r'/'),
            ('LPAREN', r'\('),
            ('RPAREN', r'\)'),
            ('SEMICOLON', r';'),
            ('SKIP', r'[ \t\r\n]+'),
            ('MISMATCH', r'.')
        ]
        
        # Regex patternini derle
        self.token_regex = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in self.token_patterns)
        self.pattern = re.compile(self.token_regex)
    
    def tokenize(self):
        for match in self.pattern.finditer(self.text):
            kind = match.lastgroup
            value = match.group()

            if kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                # Daha iyi hata raporu için satır ve sütun hesapla
                pos = match.start()
                # satır numarası: pos öncesindeki '\n' sayısı + 1
                line_num = self.text.count('\n', 0, pos) + 1
                # o satırın başlangıç/bitiş konumunu bul
                prev_nl = self.text.rfind('\n', 0, pos)
                line_start = 0 if prev_nl == -1 else prev_nl + 1
                next_nl = self.text.find('\n', pos)
                line_end = len(self.text) if next_nl == -1 else next_nl
                line_text = self.text[line_start:line_end]
                col = pos - line_start + 1

                pointer = (' ' * (col - 1)) + '^'
                raise RuntimeError(f"Unexpected character '{value}' at line {line_num}, column {col}\n{line_text}\n{pointer}")
            else:
                self.tokens.append(Token(kind, value))

        self.tokens.append(Token('EOF', ''))
        return self.tokens

# Parser sınıfı
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]
        # derivation_steps, sentansiyel formların sırasını saklayacak
        self.derivation_steps = []
        # current_form, mevcut sentansiyel formu temsil eden sembollerin
        # (nonterminal/terminal) listesidir; başlangıç sembolü 'Program'
        self.current_form = ['Program']
        self.error_occurred = False

    def record(self, nonterminal, rhs):
        """
        Soldan ilk görülen `nonterminal` öğesini `self.current_form` içinde
        `rhs` ile değiştirir (rhs boş liste ise epsilon olarak kabul edilir)
        ve ortaya çıkan sentansiyel formu (string olarak) `derivation_steps`
        listesine ekler.
        """
        # soldan ilk oluşumu bul
        idx = None
        for i, sym in enumerate(self.current_form):
            if sym == nonterminal:
                idx = i
                break
        if idx is None:
            return

        if rhs == []:
            # epsilon -> o nonterminal'i kaldır
            self.current_form.pop(idx)
        else:
            # rhs ile değiştir
            self.current_form = self.current_form[:idx] + rhs + self.current_form[idx+1:]

        # yeni sentansiyel formu string olarak ekle
        self.derivation_steps.append(' '.join(self.current_form))
    
    def error(self, msg):
        self.error_occurred = True
        # Eğer gelen mesaj zaten "Expected ..." ile başlıyorsa tekrar ekleme; sadece mevcut token bilgisini ekle
        if isinstance(msg, str) and msg.strip().startswith("Expected"):
            raise SyntaxError(f"Syntax error: {msg}. Got token '{self.current_token.value}'")
        else:
            raise SyntaxError(f"Syntax error: {msg}. Expected {self.current_token.type}, got token '{self.current_token.value}'")
    
    def eat(self, token_type):
        if self.current_token.type == token_type:
            self.pos += 1
            if self.pos < len(self.tokens):
                self.current_token = self.tokens[self.pos]
        else:
            self.error(f"Expected {token_type}")
    
    def parse(self):
        try:
            # türetmeyi başlangıç sembolü ile başlat
            self.derivation_steps = [' '.join(self.current_form)]
            self.program()

            if not self.error_occurred and self.current_token.type == 'EOF':
                print("\nProgram başarıyla parse edildi.")
                print("\nLeftmost derivation:")
                # Soldan türetmeyi adım adım alt alta yazdır
                for i, step in enumerate(self.derivation_steps, 1):
                    print(f"{i}. {step}")
            else:
                if not self.error_occurred:
                    print(f"Syntax error: Unexpected token '{self.current_token.value}'")
        except SyntaxError as e:
            print(e)
    
    def program(self):
        # Program -> StatementList kuralı
        self.record('Program', ['StatementList'])
        self.statement_list()
    
    def statement_list(self):
        # StatementList -> Statement StatementList | ε kuralı
        if self.current_token.type in ['INT', 'ID', 'PRINT']:
            # StatementList -> Statement StatementList kuralı
            self.record('StatementList', ['Statement', 'StatementList'])
            self.statement()
            self.statement_list()
        else:
            # epsilon (boş türetim)
            self.record('StatementList', [])
    
    def statement(self):
        # Statement -> Declaration | Assignment | PrintStmt kuralı
        if self.current_token.type == 'INT':
            self.record('Statement', ['Declaration'])
            self.declaration()
        elif self.current_token.type == 'ID':
            self.record('Statement', ['Assignment'])
            self.assignment()
        elif self.current_token.type == 'PRINT':
            self.record('Statement', ['PrintStmt'])
            self.print_stmt()
        else:
            self.error("Expected 'int', ID, or 'print'")
    
    def declaration(self):
        # Declaration -> int id ; kuralı
        self.record('Declaration', ['int', 'id', ';'])

        self.eat('INT')
        self.eat('ID')
        self.eat('SEMICOLON')
    
    def assignment(self):
        # Assignment -> id = Expr ; kuralı
        self.record('Assignment', ['id', '=', 'Expr', ';'])

        self.eat('ID')
        self.eat('ASSIGN')
        self.expr()
        self.eat('SEMICOLON')
    
    def print_stmt(self):
        # PrintStmt -> print ( Expr ) ; kuralı
        self.record('PrintStmt', ['print', '(', 'Expr', ')', ';'])

        self.eat('PRINT')
        self.eat('LPAREN')
        self.expr()
        self.eat('RPAREN')
        self.eat('SEMICOLON')
    
    def expr(self):
        # Expr -> Term ExprPrime kuralı
        self.record('Expr', ['Term', 'ExprPrime'])

        self.term()
        self.expr_prime()
    
    def expr_prime(self):
        # ExprPrime -> + Term ExprPrime | - Term ExprPrime | ε kuralı
        if self.current_token.type == 'PLUS':
            self.record('ExprPrime', ['+', 'Term', 'ExprPrime'])

            self.eat('PLUS')
            self.term()
            self.expr_prime()
        elif self.current_token.type == 'MINUS':
            self.record('ExprPrime', ['-', 'Term', 'ExprPrime'])

            self.eat('MINUS')
            self.term()
            self.expr_prime()
        else:
            # ε (epsilon) kuralı
            self.record('ExprPrime', [])
    
    def term(self):
        # Term -> Factor TermPrime kuralı
        self.record('Term', ['Factor', 'TermPrime'])

        self.factor()
        self.term_prime()
    
    def term_prime(self):
        # TermPrime -> * Factor TermPrime | / Factor TermPrime | ε kuralı
        if self.current_token.type == 'MULT':
            self.record('TermPrime', ['*', 'Factor', 'TermPrime'])

            self.eat('MULT')
            self.factor()
            self.term_prime()
        elif self.current_token.type == 'DIV':
            self.record('TermPrime', ['/', 'Factor', 'TermPrime'])

            self.eat('DIV')
            self.factor()
            self.term_prime()
        else:
            # ε (epsilon) kuralı
            self.record('TermPrime', [])
    
    def factor(self):
        # Factor -> id | num | ( Expr ) kuralı
        if self.current_token.type == 'ID':
            self.record('Factor', ['id'])
            self.eat('ID')
        elif self.current_token.type == 'NUMBER':
            self.record('Factor', ['num'])
            self.eat('NUMBER')
        elif self.current_token.type == 'LPAREN':
            self.record('Factor', ['(', 'Expr', ')'])
            self.eat('LPAREN')
            self.expr()
            self.eat('RPAREN')
        else:
            self.error("Expected ID, NUMBER, or '('")

# Ana program
def main():
    # İlk tercih olarak komut satırı argümanı
    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    else:
        # Dosya belirtilmediğinde varsayılan 'minilang.txt' dosyasını okumayı dene
        default_path = os.path.join(os.path.dirname(__file__), 'minilang.txt')
        if os.path.exists(default_path):
            input_path = default_path
        else:
            print(f"No input file specified and default '{default_path}' not found.")
            print("Please create 'minilang.txt' next to main.py with your minilang program")
            print("or run: python main.py <path_to_minilang_file>")
            return

    # Minilang programını seçilen giriş yolundan oku
    with open(input_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    print("Token akışı:")
    print("=" * 50)
    
    try:
        # Lexer'ı çalıştır
        lexer = Lexer(text)
        tokens = lexer.tokenize()
        
        # Token'ları yazdır: (TYPE , value) formatında
        token_output = []
        for token in tokens:
            # token.value boş ise boş bırakılacak, örn. EOF için
            token_output.append(f"({token.type} , {token.value})")
        print(' '.join(token_output))
        
        print("\n" + "=" * 50)
        
        # Parser'ı çalıştır
        parser = Parser(tokens)
        parser.parse()
        
    except RuntimeError as e:
        print(f"Lexical error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()