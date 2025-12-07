# Minilang Parser — Kullanım

Basit bir "minilang" dilinin lexer ve parser'ını içeren küçük bir Python aracı.

Dosya yapısı
- `main.py` — Lexer ve Parser içeren ana Python dosyası.
- `minilang.txt` — Varsayılan test giriş dosyası (aynı dizinde olmalı).

Çalıştırma (PowerShell)

- Eğer `minilang.txt` dosyası proje dizinindeyse, doğrudan çalıştırın:

```powershell
python "c:\Users\ibrahimoz\Desktop\Derleyici_ Tasarimi_Projesi\main.py"
```

- Farklı bir giriş dosyası kullanmak isterseniz dosya yolunu argüman olarak verin:

```powershell
python "c:\Users\ibrahimoz\Desktop\Derleyici_ Tasarimi_Projesi\main.py" "C:\path\to\your\file.txt"
```

Çıktı
- Program önce token akışını yazdırır, ardından parser'ın çalıştığını ve leftmost türetme adımlarını numaralandırılmış şekilde alt alta gösterir.

Notlar
- `declaration` kuralı sadece `int id;` formunu kabul eder. Yani `int x = 3;` gibi başlangıç atamaları syntax hatası verir.

Sorunlar / Hata ayıklama
- Eğer lexing sırasında beklenmeyen bir karakterle karşılaşılırsa, program satır ve sütun bilgisiyle bir hata mesajı gönderir.
- Parser hatalarında hata mesajı hangi token'ın beklendiğini ve hangi token ile karşılaşıldığını gösterir.