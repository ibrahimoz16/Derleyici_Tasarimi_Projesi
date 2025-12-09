# Minilang Parser — Kullanım

Basit bir "minilang" dilinin lexer ve parser'ını içeren küçük bir Python aracı.

Dosya yapısı
- `main.py` — Lexer ve Parser içeren ana Python dosyası.
- `minilang.txt` — Varsayılan test giriş dosyası (aynı dizinde olmalı).

Çalıştırma (PowerShell)

- Eğer proje dizinindeyseniz doğrudan çalıştırın:

```powershell
python "main.py"
```

- Farklı bir giriş dosyası kullanmak isterseniz dosya yolunu argüman olarak verin:

```powershell
python "main.py" "C:\path\to\your\file.txt"
```

Çıktı
- Program önce token akışını yazdırır, ardından parser'ın çalıştığını ve leftmost türetme adımlarını numaralandırılmış şekilde alt alta gösterir.

Önemli değişiklikler
- **Token biçimi:** Token'lar artık konsola `(TYPE , value)` formatında yazdırılır. Örnek: `(INT , int) (ID , x) (SEMICOLON , ;) (EOF , )`.
- **Hata mesajı düzeltilmesi:** Parser içindeki `error` fonksiyonundaki tekrar eden "Expected ..." ifadesi giderildi; artık hata mesajları daha okunaklıdır (ör. `Syntax error: Expected SEMICOLON. Got token ')'`).

Örnek çıktı

- Token akışı (örnek):

```
(INT , int) (ID , x) (SEMICOLON , ;) (INT , int) (ID , y) (SEMICOLON , ;) (ID , x) (ASSIGN , =) (NUMBER , 3) (PLUS , +) (NUMBER , 6) (SEMICOLON , ;) (ID , y) (ASSIGN , =) (LPAREN , () (ID , x) (MINUS , -) (NUMBER , 5) (RPAREN , )) (DIV , /) (NUMBER , 2) (SEMICOLON , ;) (PRINT , print) (LPAREN , () (ID , x) (PLUS , +) (ID , y) (RPAREN , )) (SEMICOLON , ;) (EOF , )
```