# 01 — Çevrimdışı test neyi ödüllendiriyor?

Yazı: **Offline kazandım, online kaybettim**

## Bu klasör ne değil

Yazıdaki hiçbir sayı buradan çıkmıyor. Yazı, kendi deneyimimi anlatıp üç nedeni
literatürden gösteriyor; içindeki bütün sayılar başka makalelerden (Joachims ve ark.
2005, Joachims–Swaminathan–Schnabel 2017, Dacrema–Cremonesi–Jannach 2019). Söz konusu
A/B testi Kariyer.net verisiyle yapıldı, o veri paylaşılamaz.

Buradaki iki betik **yazının iddiasının kanıtı değil, anlattığı mekanizmanın
gösterimi.** İkisi de kamuya açık veriyle ya da tamamen kurgu bir dünyayla çalışıyor.
Derste tahtada anlattığım şeyin çalışan hali; kendi makinenizde beş dakikada
tekrarlanabilir.

## Veri

`deney1_bolme.py` MovieTweetings kullanıyor — 03'teki deneyle aynı anlık görüntü,
aynı commit:

```bash
curl -L -o ratings.dat \
  https://raw.githubusercontent.com/sidooms/MovieTweetings/44c525d0c766944910686c60697203cda39305d6/latest/ratings.dat
```

`deney2_konum.py` veri istemiyor; dünyayı kendisi kuruyor.

## Çalıştırmak için

```bash
pip install numpy scipy pandas
python3 deney1_bolme.py    # ~20 saniye  -> sonuclar_bolme.csv, tavan_notu.txt
python3 deney2_konum.py    # ~10 saniye  -> sonuclar_konum.csv
```

---

## deney1_bolme.py — aynı model, iki bölme, on dört kat fark

Üç protokol, aynı veri havuzu (`< 2021-01-01`), aynı filtreler, aynı modeller:

| | bölme | değerlendirilen kullanıcı |
|---|---|---|
| **A** | zamana göre: eğitim `< 2020-01-01`, test = 2020 | 1.691 |
| **B** | rastgele, A ile aynı eğitim oranı (%92,9) | 13.873 |
| **B'** | rastgele, ama yalnızca A'nın kullanıcıları | 1.798 |

B' satırı önemli: aradaki farkın "değerlendirilen kullanıcı kümesi değişti"den
gelmediğini göstermek için var.

NDCG@10:

| Model | A (zamana göre) | B' (rastgele) | kat |
|---|---|---|---|
| Rastgele | 0,0000 | 0,0001 | — |
| Popülerlik | 0,0071 | 0,0272 | 3,8 |
| Öğe-öğe kNN | 0,0079 | 0,1141 | **14,4** |

Seviyedeki şişme bir yana — asıl mesele şu: **protokol, kazananı değiştiriyor.**
Zamana göre böldüğünüzde kNN ile popülerlik başa baş (NDCG'de kNN %11 önde, R@10'da
popülerlik hafif önde). Rastgele böldüğünüzde kNN popülerliğin 4,2 katı. Aynı veri,
aynı kod, aynı iki model.

Nedeni şu: rastgele bölme bir kullanıcının *geleceğini* eğitim setine koyuyor.
Komşuluk yöntemi bundan en çok faydalanan yöntem, çünkü işi zaten birlikte görülen
öğeleri eşleştirmek. Popülerliğin böyle bir sızıntıdan alacağı şey daha az.

### Tavan — ulaşılamaz isabetler

Aynı betik bir de şunu sayıyor: 2020 testindeki 63.115 etkileşimin **18.722'si
(%29,7)** eğitim kataloğunda hiç bulunmayan filmlere gidiyor. Bunlar hiçbir modelin
isabet edemeyeceği satırlar; 2020'de ilk kez 1.653 film görünüyor.

Yazıdaki birinci neden ("elimizdeki veri dünyanın değil, eski modelin fotoğrafı")
burada ölçülebilir hale geliyor: metriğin tavanı 1,0 değil. Katalog yenilendikçe
tavan da düşüyor ve modeliniz, ulaşamayacağı şeyler yüzünden ceza alıyor.

---

## deney2_konum.py — çevrimdışı metrik, eski modele benzeyeni ödüllendiriyor

Bu betikte gerçek veri yok, kasten yok: göstermek istediğim şey ancak gerçek alakanın
*bilindiği* bir dünyada görülebiliyor.

Kurgu, docstring'de satır satır yazılı. Özeti: 20.000 kullanıcı, 2.000 öğe, gerçek
alaka gizli bir çarpanlar modelinden geliyor; her öğenin bir de "gösterim ağırlığı"
var ve bu ağırlık alakayla ilişkisiz üretiliyor (ölçülen korelasyon +0,005). Eski
model gösterim ağırlığına göre sıralıyor. Tıklamalar konum tabanlı: inceleme
olasılığı 1. sırada 0,80, 2. sırada 0,75 (Joachims ve ark. 2005) — 3. sıradan
sonrası **varsayım**, ölçülmüş değil, betikte öyle de yazıyor. Güven yanlılığının
katsayısı aynı makaledeki 10'a 7 gözlemine kalibre ediliyor; betik ulaştığı oranı
(1,42) yazdırıyor.

Sonra beş global sıralama, iki ayrı ölçütle:

| Sıralama | çevrimdışı NDCG@10 | gerçek alaka@10 | eski modelle örtüşme |
|---|---|---|---|
| Kayıt politikası (popülerlik) | **0,2204** | 0,0886 | 10/10 |
| Ham tıklama sayısı | 0,2204 | 0,0886 | 10/10 |
| Konum IPS | 0,2193 | 0,0883 | 9/10 |
| Gösterim IPS (CTR) | 0,0430 | 0,1055 | 1/10 |
| Gerçek alaka (oracle) | 0,0038 | **0,1492** | 0/10 |

Çevrimdışı sıralama ile gerçek sıralama tam ters. **Gerçek alakayı bilen sıralama,
çevrimdışı testte en kötü.** Son sütun da nedenini veriyor: çevrimdışı skor, eski
modelin listesiyle örtüşmenin neredeyse monoton bir fonksiyonu.

Bir de beklemediğim bir şey çıktı ve bırakmaya değer buldum: **konum için IPS
düzeltmesi burada hiçbir işe yaramıyor** (0,0883, ham tıklamanın bile altında).
Çünkü bu kurguda asıl yanlılık konumda değil, *gösterilip gösterilmemekte*. Doğru
eğilim skoru "kaçıncı sıradaydı" değil, "hiç gösterildi mi" oluyor; gösterime göre
düzeltme gerçek alakayı %19 artırıyor. Yazıda "konum yanlılığını düzeltin" diye
geçen tavsiye, tek başına, bu kurguda yetmiyor.

Bu bir simülasyon; "gerçek hayatta da böyle" demiyor. Söylediği şey daha dar ve daha
sağlam: bu üç varsayım (popülerlik alakayla ilişkisiz, kayıt politikası popülerliğe
göre sıralıyor, tıklama konuma bağlı) doğruysa, çevrimdışı metrik iyi modeli
eliyor — ve elediğini fark etmenizin hiçbir yolu yok, çünkü gerçek alakayı yalnızca
simülatör biliyor.

---

## Kaynaklar

- Joachims, T. ve ark. (2005). *Accurately Interpreting Clickthrough Data as Implicit
  Feedback.* SIGIR 2005.
  <https://www.cs.cornell.edu/people/tj/publications/joachims_etal_05a.pdf>
- Joachims, T., Swaminathan, A., Schnabel, T. (2017). *Unbiased Learning-to-Rank with
  Biased Feedback.* WSDM 2017. <https://arxiv.org/abs/1608.04468>
- Dacrema, M. F., Cremonesi, P., Jannach, D. (2019). *Are We Really Making Much
  Progress? A Worrying Analysis of Recent Neural Recommendation Approaches.*
  RecSys 2019. <https://arxiv.org/abs/1907.06902>
- Dooms, S., De Pessemier, T., Martens, L. (2013). *MovieTweetings: a Movie Rating
  Dataset Collected From Twitter.* CrowdRec @ RecSys 2013.
  <https://github.com/sidooms/MovieTweetings>
