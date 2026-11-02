# Öneri Sistemleri Algoritmaları — yazı dizisi

[Kariyer.net Tech](https://medium.com/kariyertech) altında yayımladığım öneri sistemleri
yazı dizisinin deney betikleri ve ham çıktıları.

Dizinin çıkış noktası, bu dönem İstanbul Ticaret Üniversitesi ve Nevşehir Hacı Bektaş Veli
Üniversitesi'nde verdiğim **Öneri Sistemleri Algoritmaları** dersi. Yazılarda geçen her sayı
burada duran betiklerden çıkıyor; isteyen indirip kendi makinesinde çalıştırabilir.

## Yazılar

| # | Yazı | Klasör |
|---|---|---|
| 01 | Offline kazandım, online kaybettim | — |
| 02 | [Filmin "hayır" deme hakkı yok, işverenin var](https://medium.com/kariyertech/filmin-hayır-deme-hakkı-yok-işverenin-var-49d70a364c11) | — |
| 03 | Hiçbir şey öğrenmeyen model neden herkesi yendi? | [`03-populerlik-temel-modeli/`](03-populerlik-temel-modeli/) |
| 04 | Bir bölme işareti yüzünden kırk kat | *hazırlanıyor* |
| 05 | Varsayılan ayarlarla çalıştırdım, model kaybetti | *hazırlanıyor* |

## Nasıl kurulu

Her yazının kendi klasörü var. Klasörün içinde o deneyin betikleri, ham sonuç dosyaları ve
kurulumu anlatan bir `README.md` duruyor. Veri dosyaları depoya konmadı — her klasörün
README'si veriyi nereden ve hangi sürümüyle indireceğinizi yazıyor.

```
03-populerlik-temel-modeli/
├── README.md       kurulum, veri kaynağı, çalıştırma adımları
├── deney.py        temel karşılaştırma      -> sonuclar.csv
├── deney2.py       pencere + kNN taraması   -> sonuclar2.csv
├── sonuclar.csv    ham çıktı
└── sonuclar2.csv   ham çıktı
```

## Bu betikler ne değil

Bunlar makale değil, ders örneği. Kurulumlar kasten sade: tek bir zaman bölmesi, sınırlı bir
ayar taraması, güven aralığı yok. Amaç bir yöntemin en iyi halini göstermek değil, bir fikrin
neden işe yaradığını ya da yaramadığını en az kodla görünür kılmak.

## İletişim

Dr. Kübra Karacan Uyar · [LinkedIn](https://linkedin.com/in/kkaracan) ·
[Google Scholar](https://scholar.google.com/citations?user=XLDSx7QAAAAJ)
