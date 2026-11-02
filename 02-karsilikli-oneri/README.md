# 02 — Karşılıklı öneri: tıkanma ve çift sayım

Yazı: **[Filmin "hayır" deme hakkı yok, işverenin var](https://medium.com/kariyertech/filmin-hay%C4%B1r-deme-hakk%C4%B1-yok-i%C5%9Fverenin-var-49d70a364c11)** · Kariyer.net Tech

## Bu klasör ne değil

Yazıdaki hiçbir sayı buradan çıkmıyor. Yazı dört farkı literatürden gösteriyor;
içindeki bütün sayılar başka makalelerden (Palomares ve ark. 2021, Yang ve ark. 2024,
Tomita–Yokoyama 2024, Bied ve ark. 2021). İşe alım verisi paylaşılamaz.

Buradaki iki betik **yazının iddiasının kanıtı değil, anlattığı iki mekanizmanın
gösterimi:** kapasite kısıtının faturası, ve tek taraflı değerlendirmenin kör noktası.

İroniyi baştan kabul edelim: tıkanma deneyi film verisiyle yapılıyor. Film "hayır"
demez, yani burada gerçek bir kapasite kısıtı yok — kısıtı biz dayatıyoruz. Gösterilen
şey kısıtın kendisi değil, **kısıt koyunca faturanın ne olduğu.**

## Veri

`deney1_tikanma.py` MovieTweetings kullanıyor — 03'teki deneyle aynı anlık görüntü,
aynı commit, aynı bölme:

```bash
curl -L -o ratings.dat \
  https://raw.githubusercontent.com/sidooms/MovieTweetings/44c525d0c766944910686c60697203cda39305d6/latest/ratings.dat
```

`deney2_cift_sayim.py` veri istemiyor; kurguyu kendisi üretiyor.

## Çalıştırmak için

```bash
pip install numpy scipy pandas
python3 deney1_tikanma.py      # ~35 saniye  -> sonuclar_tikanma.csv
python3 deney2_cift_sayim.py   # ~1 saniye   -> sonuclar_cift_sayim.csv
```

---

## deney1_tikanma.py — kota koyunca ne kaybediyoruz?

Kurulum 03'teki deneyle aynı: eğitim `< 2020-01-01`, test = 2020, 11.216 film,
1.691 değerlendirilebilir kullanıcı.

Tıkanma ölçütü Bied ve ark. (2021) tanımı:

```
MS_l(j)       = (1 / (n*l)) * |{ i : j, i'nin ilk l önerisinde }|
Congestion@l  = SUM_j  MS_l(j) * log MS_l(j)
normalize     = Congestion@l / log(m)      ->  [-1, 0]
```

−1 en iyi (yük dağılmış), 0 en kötü (tek öğeye yığılmış). Bu kurulumda tam sayı
kısıtı altında ulaşılabilecek en iyi değer **−0,9940** (16.910 yuva, 11.216 öğe);
betik bunu da hesaplayıp yazdırıyor, çünkü −1 her kurulumda erişilebilir değil.

Kota, açgözlü bir kural: bir film en çok `kota` listede görünebilir, kullanıcılar
sırayla seçer. Sıra etkisini ölçmek için her satır iki kez, iki ayrı kullanıcı
sırasıyla çalışıyor; sonuçlar üçüncü haneye kadar oynamıyor.

**Popülerlik (son 90 gün)** — yükü bir avuç filme yığan model:

| kota | R@10 | tıkanma | kapsam |
|---|---|---|---|
| yok | **0,2682** | −0,2887 | %0,25 (28 film) |
| 1000 | 0,2057 | −0,3241 | %0,31 |
| 500 | 0,1297 | −0,3858 | %0,39 |
| 100 | 0,0360 | −0,5513 | %1,53 |
| 10 | 0,0055 | −0,8006 | %16,32 |
| 2 | 0,0016 | **−0,9703** | %75,96 |

Yedi buçuk kat isabet kaybı, kotayı 100'e indirmenin bedeli. Yazıda "popülerliği
cezalandıralım, dağıtalım" cümlesinin faturası diye geçen şey bu.

**Öğe-öğe kNN** — zaten dağıtan model. Burada beklemediğim bir şey oldu:

| kota | R@10 | tıkanma | kapsam |
|---|---|---|---|
| yok | 0,0113 | −0,5122 | %5,43 |
| 200 | 0,0139 | −0,5454 | %5,65 |
| **100** | **0,0184** | **−0,5946** | %6,38 |
| 20 | 0,0171 | −0,7485 | %14,52 |
| 2 | 0,0053 | −0,9744 | %80,18 |

Orta sıkılıkta bir kota **hem isabeti hem tıkanmayı iyileştiriyor.** kNN'in kendi
başına üstte tuttuğu birkaç yüz film, zaten herkese doğru öneri değilmiş; kota onları
düşürünce yerine gelenler daha isabetli olmuş. Yani takas evrensel değil — modele
bağlı. "Çeşitliliği artırmak hep isabetten götürür" cümlesi, en azından bu kurulumda,
doğru değil.

### Bu sayılar Bied ve ark.'nın sayılarıyla karşılaştırılamaz

Üç ayrı nedenle, ve bunu yazmadan tabloyu okumak yanıltıcı olur:

1. Normalizasyon `log(m)`'e bölüyor. m burada 11.216, onlarda 14.200 — mutlak değerler
   doğrudan kıyaslanamaz.
2. Onlar optimal taşıma kullanıyor; buradaki açgözlü kota çok daha kaba bir araç.
3. Veri bambaşka: film puanı ile iş ilanı.

Ortak olan tek şey takasın **yönü**.

---

## deney2_cift_sayim.py — tek taraflı ortalamanın kör noktası

Yang ve ark. (KDD 2024) şunu söylüyor: iki tarafın NDCG'sini ayrı ayrı hesaplayıp
ortalamasını almak aynı eşleşmeyi iki kez sayıyor. Bu betik o cümleyi elle tutulur
hale getiriyor — ve bunu kurgu bir örnekle yapıyor, çünkü gösterilmek istenen şey bir
ölçütün göremediği şey; onu görmek için ölçütü sabit tutup arkasındakini değiştirmek
gerekiyor.

Kurgu: 200 aday, 200 işveren, her tarafın 6 gerçek karşılıklı eşi (toplam 1.200 çift).
Her iki taraf da 5'lik liste alıyor, her listede tam 3 gerçek eş var ve hep aynı
sıralarda. Dolayısıyla iki tarafın NDCG'si **bütün senaryolarda aynı.** Değişen tek
şey, işveren tarafının hangi 3 eşi seçtiği.

| örtüşme | tek taraflı ortalama NDCG | tek taraflı başarı | farklı çift | çift taraflı | şişme |
|---|---|---|---|---|---|
| 0,00 | 0,7227 | 1.200 | **1.200** | 0 | 1,00 |
| 0,33 | 0,7227 | 1.200 | 1.000 | 200 | 1,20 |
| 0,67 | 0,7227 | 1.200 | 800 | 400 | 1,50 |
| 1,00 | 0,7227 | 1.200 | **600** | 600 | **2,00** |

Tek taraflı ortalama dört satırda da **0,7227.** Sistemin dokunduğu farklı çift sayısı
ise 1.200'den 600'e iniyor, şişme 1,00'den 2,00'ye çıkıyor. Yani tablonuzdaki hücre
hiç kıpırdamazken sistem yarı iş yapıyor olabilir.

Bir uyarı: "doğru" iki taraflı ölçüt, platformun eşleşme tanımına bağlı. Eşleşme için
iki tarafın da karşısındakini görmesi gerekiyorsa **kesişim** anlamlı; bir tarafın
görmesi yetiyorsa **birleşim**. Buradaki iddia bunlardan hangisinin doğru olduğu
değil — tek taraflı ortalamanın ikisini de göremediği.

Betik sonunda n=6 ile elle kontrol edilebilir bir örnek de yazdırıyor: çiftler tek tek
ekranda, sayarak doğrulayabiliyorsunuz. Derste tahtaya bunu yazıyorum.

---

## Kaynaklar

- Palomares, I. ve ark. (2021). *Reciprocal Recommender Systems.* Information Fusion,
  69, 103–127. <https://doi.org/10.1016/j.inffus.2020.12.001>
- Yang, C. ve ark. (2024). *Revisiting Reciprocal Recommender Systems: Metrics,
  Formulation, and Method.* KDD 2024. <https://arxiv.org/abs/2408.09748>
- Tomita, Y., Yokoyama, T. (2024). *Fair Reciprocal Recommendation in Matching
  Markets.* RecSys 2024. <https://arxiv.org/abs/2409.00720>
- Bied, G. ve ark. (2021). *Congestion-Avoiding Job Recommendation with Optimal
  Transport.* FEAST @ ECML-PKDD 2021.
  <https://feast-ecmlpkdd.github.io/archive/2021/papers/FEAST2021_paper_4.pdf>
- Dooms, S., De Pessemier, T., Martens, L. (2013). *MovieTweetings.*
  CrowdRec @ RecSys 2013. <https://github.com/sidooms/MovieTweetings>
