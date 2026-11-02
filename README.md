# Öneri Sistemleri Algoritmaları — yazı dizisi

[Kariyer.net Tech](https://medium.com/kariyertech) altında yayımladığım öneri sistemleri
yazı dizisinin betikleri, ham çıktıları ve yazı metinleri.

Dizinin çıkış noktası, bu dönem İstanbul Ticaret Üniversitesi ve Nevşehir Hacı Bektaş Veli
Üniversitesi'nde verdiğim **Öneri Sistemleri Algoritmaları** dersi. Burada duran her şey
indirilip çalıştırılabilir; veri kümeleri kamuya açık ve sürümleri sabitlenmiş.

## Yazılar

| # | Yazı | Klasör |
|---|---|---|
| 01 | Offline kazandım, online kaybettim | [`01-offline-online/`](01-offline-online/) |
| 02 | [Filmin "hayır" deme hakkı yok, işverenin var](https://medium.com/kariyertech/filmin-hayır-deme-hakkı-yok-işverenin-var-49d70a364c11) | [`02-karsilikli-oneri/`](02-karsilikli-oneri/) |
| 03 | Hiçbir şey öğrenmeyen model neden herkesi yendi? | [`03-populerlik-temel-modeli/`](03-populerlik-temel-modeli/) |
| 04 | Bir bölme işareti yüzünden kırk kat | *hazırlanıyor* |
| 05 | Varsayılan ayarlarla çalıştırdım, model kaybetti | *hazırlanıyor* |

## İki tür klasör var

Aynı görünüyorlar ama aynı şey değiller, karıştırmamak önemli:

**Deney klasörü.** Yazıdaki sayılar birebir o klasördeki betiklerden çıkıyor.
`03-populerlik-temel-modeli/` böyle.

**Gösterim klasörü.** Yazı literatüre dayanıyor, kendi ölçümüm yok; klasördeki betikler
yazının *anlattığı mekanizmayı* kamuya açık veriyle ya da açıkça kurgulanmış bir dünyada
çalıştırıyor. `01-offline-online/` ve `02-karsilikli-oneri/` böyle. Bu klasörlerin
README'si en başta bunu yazıyor; oradaki bir sayıyı yazıdaki bir iddianın kanıtı gibi
okumayın.

Ayrımı neden bu kadar vurguluyorum: dizinin bütün derdi, bir sayının neyi ölçtüğünü
bilmek. Kendi deponda bunu karıştırırsan geri kalanı konuşmaya değmez.

## Nasıl kurulu

Her yazının kendi klasörü var: betikler, ham sonuç dosyaları, yazının markdown hâli
(`yazi.md`) ve kurulumu anlatan bir `README.md`. Veri dosyaları depoya konmadı — her
klasörün README'si veriyi nereden ve hangi sürümüyle indireceğinizi yazıyor.

```
01-offline-online/
├── README.md               kurulum, sonuç tabloları, uyarılar
├── yazi.md                 yazının metni
├── deney1_bolme.py         rastgele bölme vs zaman bölmesi   -> sonuclar_bolme.csv
├── deney2_konum.py         konum yanlılığı simülasyonu       -> sonuclar_konum.csv
└── tavan_notu.txt          ulaşılamaz isabetlerin payı

02-karsilikli-oneri/
├── README.md
├── yazi.md
├── deney1_tikanma.py       kapasite kotası, isabet-tıkanma   -> sonuclar_tikanma.csv
└── deney2_cift_sayim.py    tek taraflı ölçütün kör noktası   -> sonuclar_cift_sayim.csv

03-populerlik-temel-modeli/
├── README.md
├── yazi.md
├── deney.py                temel karşılaştırma               -> sonuclar.csv
└── deney2.py               pencere + kNN taraması            -> sonuclar2.csv
```

Hepsi için `pip install numpy scipy pandas` yeter; en uzunu yarım dakika sürüyor.

## Bu betikler ne değil

Bunlar makale değil, ders örneği. Kurulumlar kasten sade: tek bir zaman bölmesi, sınırlı
bir ayar taraması, güven aralığı yok. Amaç bir yöntemin en iyi halini göstermek değil, bir
fikrin neden işe yaradığını ya da yaramadığını en az kodla görünür kılmak.

Simülasyon içeren betiklerde bütün varsayımlar docstring'in başında, tek tek yazılı.
Ölçülmüş olanla varsayılan olan ayrı ayrı işaretlendi. Bir simülasyon "gerçek hayatta da
böyle" demez; "bu varsayımlar doğruysa şu olur" der.

## İletişim

Dr. Kübra Karacan Uyar · [LinkedIn](https://linkedin.com/in/kkaracan) ·
[Google Scholar](https://scholar.google.com/citations?user=XLDSx7QAAAAJ)
