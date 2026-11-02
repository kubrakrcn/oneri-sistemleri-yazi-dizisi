# Hiçbir şey öğrenmeyen model neden herkesi yendi?

### Temel modelin tanımında tek bir satırı değiştirdim. İsabet yirmi katına çıktı. Öğrenen model hâlâ yarı yolda.

---

Dersin uygulama saatinde popülerlik temel modelini hep bir formalite olarak koyarım. Amacı bellidir: kırılacak bir çıta. Öğrenciler kendi modellerini yazar, bu sayıyı geçer, moral olur, devam ederiz.

Bu sefer geçemediler. Ben de geçemedim.

Sonra çıtayı yanlış yere koyduğumu fark ettim — ama düşündüğüm yönde değil. Çıta alçak değildi. **Ben yanlış çıtayı ölçüyordum.**

Aşağıdaki her sayıyı sizin de çalıştırabileceğiniz bir betikten aldım; kurulumu da açıkça yazıyorum, çünkü bu yazının bütün meselesi zaten kurulumun kendisi.

---

## Deneyin kurulumu

**Veri:** MovieTweetings. İnsanların IMDb uygulaması üzerinden verip Twitter'da paylaştığı gerçek film puanlarından derlenmiş, açık bir veri kümesi. Kasım 2021 anlık görüntüsünde 921.398 puan, 71.707 kullanıcı, 38.018 film. Tarihi özellikle yazıyorum: depo her gün büyüyor, bugün indirirseniz bu sayılar tutmaz.

MovieLens yerine bunu seçmemin sebebi zaman damgasının ne anlama geldiği. MovieLens'te zaman damgası filmin ne zaman izlendiğini değil, ne zaman puanlandığını söyler — ikisinin arasında yıllar olabilir. MovieTweetings'te ise puan, film biter bitmez atılan tweet'in kendisi. Yani buradaki zaman damgası gerçekten "o kişi o hafta ne izledi" demek, ve bu yazının tamamı buna dayanıyor.

**Bölme:** Zaman tabanlı. 2020'den öncesi eğitim, 2020 yılının tamamı test. 2021 verisini hiç kullanmadım; tam ve kapalı bir takvim yılı üzerinde ölçmek istedim. Rastgele bölme yok — bir öneri sisteminde geleceği geçmişe karıştırmak zaten en sık yapılan hata.

**Filtre:** Eğitimde en az 5 kez görülmüş filmler, en az 5 etkileşimi olan kullanıcılar. Geriye 724.318 eğitim etkileşimi, 11.216 film ve puanlanabilir 1.691 kullanıcı kalıyor.

**Metrikler:** P@10, R@10, NDCG@10 — ve bir de **katalog kapsamı**: sistem, on kişilik listeleri doldururken kaç farklı filme dokundu?

**Ayar:** Ne popülerlik penceresini ne de k'yı tek bir "en iyi" değer olarak seçtim; taramanın tamamını olduğu gibi veriyorum. Sebebi basit — en iyisini test dönemine bakarak seçmek, derste öğrencilerime yasakladığım şeyin ta kendisi olurdu. Doğrusu eğitim verisinin son diliminden ayrı bir doğrulama kümesi ayırmaktır. Bu bir ders örneği olduğu için o adımı atladım ve karşılığında bütün satırları gösteriyorum.

Kullanıcının eğitimde zaten gördüğü filmler listelerden çıkarılıyor. Hepsi bu.

---

## Birinci tablo: aynı model, farklı pencere

Popülerlik modelinde öğrenilen bir şey yok. "En çok etkileşim alan on filmi herkese göster." Tek bir karar var: **hangi dönemin etkileşimlerini sayıyorsun?**

| Popülerlik penceresi | P@10 | NDCG@10 | Kapsam |
|---|---|---|---|
| Tüm geçmiş | 0,0037 | 0,0071 | %0,63 |
| Son 730 gün | 0,0134 | 0,0405 | %0,53 |
| Son 365 gün | 0,0294 | 0,0693 | %0,37 |
| Son 180 gün | 0,0657 | 0,1537 | %0,33 |
| Son 90 gün | 0,0685 | 0,1616 | %0,25 |
| Son 30 gün | 0,0748 | 0,1721 | %0,24 |

Üstten alta, aynı model. Tek satırlık bir fark. İsabet **yirmi katına** çıkıyor.

Şimdi şunu düşünün: literatürde "popülerlik temel modeli" dendiğinde neredeyse her zaman en üstteki satır kastediliyor. Yani tüm geçmiş. Yani 0,0037. Yani ezilmesi çok kolay bir rakam.

---

## Bu, benim keşfim değil

Ji, Sun, Zhang ve Li'nin SIGIR 2020'deki çalışması tam olarak bu noktayı koyuyor. Popülerliğin o güne kadarki ölçülme biçiminin iki kusuru olduğunu söylüyorlar: "kullanıcının sistemle etkileşime girdiği andaki popüler öğeleri yansıtmıyor" ve "kullanıcının son etkileşiminden sonra yayımlanmış öğeleri önerebiliyor."

İlk madde benim tablomun ta kendisi. Kullanıcı 2020 Mart'ında sisteme giriyor; siz ona 2013'ten 2019'a kadarki toplam sayımın zirvesini gösteriyorsunuz. O film o hafta kimsenin gündeminde değil.

Aynı çalışma, kullanıcının son etkileşiminden geriye bir aylık pencereyi kullanan bir popülerlik modelini MovieLens-20M üzerinde denemiş: HR@5 0,0304'ten 0,0530'a çıkmış, metrikler genelinde iyileşme "yüzde 70 ile yüzde 83 aralığında."

Benim veri kümemde oran çok daha sert çünkü MovieTweetings'te gündem daha hızlı dönüyor. Ama yön aynı ve mekanizma aynı.

---

## Peki ya öğrenen model?

Burada dürüst olmam gerekiyor, çünkü bu dizinin ilk yazısında tam da bunu eleştirmiştim: kendi modelini günlerce ayarlayıp, karşısındaki temel modeli varsayılan ayarlarla bir kez çalıştırıp geçmek.

Bu sefer tersini yapmamak için öğe-öğe kNN'i birkaç ayarla denedim.

| Model | P@10 | NDCG@10 | Kapsam | Farklı film |
|---|---|---|---|---|
| kNN, ikili matris, k=300 | 0,0047 | 0,0086 | %5,27 | 591 |
| kNN, ikili matris, k=50 | 0,0060 | 0,0114 | %6,04 | 677 |
| kNN, tazelik ağırlıklı, k=300 | 0,0379 | 0,0898 | %5,47 | 614 |
| Popülerlik, son 30 gün | 0,0748 | 0,1721 | %0,24 | 27 |

İki şeye dikkat.

**Birincisi:** kNN'e yaptığım tek anlamlı iyileştirme, eğitim etkileşimlerini yaşlarına göre ağırlıklandırmak oldu — 365 günlük yarı ömürle üstel bir sönüm. Model mimarisinde hiçbir şey değişmedi. İsabet 0,0047'den 0,0379'a, yani **sekiz katına** çıktı.

Bu arada k = 300, derste öğrencilerime verdiğim "pratikte 20 ile 200 arası" aralığının dışında. Bu veride komşuluk o kadar seyrek ki daha geniş bir komşuluk işe yarıyor — ama bu da veriye bakmadan bilinebilecek bir şey değil, tablodaki k=50 satırı tam olarak bu yüzden duruyor.

**İkincisi:** bütün bu çabadan sonra bile, hiçbir şey öğrenmeyen model hâlâ iki kat önde.

Ve şunu da söyleyeyim: eğer kNN'i bir kez, varsayılan ayarlarla, ikili matrisle çalıştırıp "0,0047" yazsaydım — ki bu gayet standart bir şeydir — sonuç tablosu bambaşka bir hikâye anlatıyor olurdu. Aynı kod, aynı veri, sekiz kat fark.

Bu, Ferrari Dacrema ve arkadaşlarının 2019'da, Anelli ve arkadaşlarının da 2022'de anlattığı şeyin küçük ölçekli bir tekrarı. Anelli ve arkadaşları on işbirlikçi filtreleme yöntemini sistematik biçimde karşılaştırdıkları çalışmada şunu yazıyor: "Değerlendirilen doğruluk ölçümlerinin hiçbirinde, ele alınan sinir ağı modellerinden herhangi biri en iyi performansı vermedi."

---

## Ama tablonun sağ tarafına bakın

İşte asıl mesele burada.

Son 30 gün popülerliği, 1.691 kullanıcıya on film önerirken **toplam 27 farklı filme** dokundu. Katalogda 11.216 film var.

Bu bir öneri sistemi değil. Bu bir afiş.

Herkese aynı şeyi gösteriyor, çünkü herkes şu sıralar aynı şeyi izliyor. Metrik bunu ödüllendiriyor, çünkü metrik "kullanıcının test döneminde yaptığı şeyi tahmin edebildin mi" diye soruyor — ve insanların çoğu, çoğu zaman, o ay çıkan filmi izliyor.

kNN 614 farklı filme dokunuyor. Yirmi üç katı. Ve bu farkın hiçbir metrikte karşılığı yok.

İkisini birleştirmeyi de denedim — tazelik ağırlıklı kNN skoru ile son 90 gün popülerliğini harmanlayan basit bir ağırlıklı toplam:

| Karma model | P@10 | Kapsam | Farklı film |
|---|---|---|---|
| λ = 0,3 (ağırlık kNN'de) | 0,0475 | %4,95 | 555 |
| λ = 0,5 | 0,0555 | %4,07 | 457 |
| λ = 0,7 (ağırlık popülerlikte) | 0,0638 | %2,86 | 321 |

Son satır ilginç: saf popülerliğe göre isabetin **%15'ini** veriyorsunuz, karşılığında dokunulan film sayısı 27'den 321'e, yani **on iki katına** çıkıyor.

Bu bir kayıp değil. Bu bir fiyat, ve fiyatı görünce tartışabiliyorsunuz.

![İsabet mi, katalog mu? — P@10 ile katalog kapsamının dağılımı](Grafik_03_isabet_kapsam.png)

*Turuncu noktalar aynı modelin farklı zaman pencereleri: sol kenarda, neredeyse dik bir çizgi üzerinde. Kapsam sabit, isabet yirmi kat değişiyor. Sağa doğru gitmenin bedeli ise yukarıdan inmek.*

---

## Dört ders

**1. Temel modeli rakip gibi kurun, süs gibi değil.**

Popülerliği tabloya "işte bakın ne kadar kötü" diye koyuyorsanız, muhtemelen onu kötü kurdunuz. Zaman pencereli, düzgün ayarlanmış bir popülerlik modeli çoğu ortamda ciddi bir rakiptir. Onu yenemiyorsanız bunu bilmek, geç öğrenmekten iyidir.

**2. Zamanı önce modele, sonra mimariye sokun.**

Benim deneyimde en büyük iki sıçrama da zaman bilgisinden geldi: popülerlik penceresinden ve tazelik ağırlığından. İkisi de birkaç satır. Yeni bir mimariye geçmeden önce elinizdeki zaman damgasını gerçekten kullanıp kullanmadığınıza bakın.

**3. İsabeti asla tek başına raporlamayın.**

P@10 = 0,0748 cümlesi, yanında "27 film" yazmıyorsa eksik bir cümledir. Bu ikisini aynı tabloda görmek, yukarıdaki takası bir karara dönüştürüyor. Ayrı görmek ise sadece iki ayrı yanılsama üretiyor.

**4. Kazandığınız farkın nereden geldiğini sorun.**

Bu, hepsinin özeti. Yeni modeliniz eskisini geçtiğinde sorulacak soru "ne kadar geçti" değil, **"neyi ekledim de geçti"**. Mimariyi mi, yoksa eski modelin hiç kullanmadığı bir bilgiyi mi? Çoğu zaman ikincisi çıkıyor — ve ikincisiyse, o bilgiyi basit modele de verip yeniden ölçmek zorundasınız.

---

## Son olarak

Derste artık popülerlik temel modelini formalite olarak koymuyorum. İlk saatin sonunda kuruyoruz, zaman penceresini beraber ayarlıyoruz, ve dönem boyunca o sayı tahtada asılı duruyor.

Çoğu hafta kimse geçemiyor. Geçtikleri hafta ise gerçekten bir şey öğrenmiş oluyorlar — çünkü neyi geçtiklerini biliyorlar.

**Sizin tablonuzdaki temel model, gerçekten yenilmesi gereken model mi?**

---

*Deneyin betiği ve ham çıktıları yazının sonundaki bağlantıda; veri kümesi herkese açık, sonuçlar Kasım 2021 anlık görüntüsüyle tekrar üretilebilir. Kurulum kasten sade tutuldu: tek bir zaman bölmesi, doğrulama kümesi olmadan sunulan bir ayar taraması, güven aralığı yok. Bir makale değil, bir ders örneği.*

*Bu yazı, bu dönem İstanbul Ticaret Üniversitesi ve Nevşehir Hacı Bektaş Veli Üniversitesi'nde verdiğim Öneri Sistemleri Algoritmaları dersinden çıkan yazı dizisinin üçüncü bölümü. Sırada: "Bir bölme işareti yüzünden kırk kat."*

---

### Kaynaklar

- Ji, Y., Sun, A., Zhang, J., Li, C. (2020). *A Re-visit of the Popularity Baseline in Recommender Systems.* SIGIR '20, s. 1749–1752. [DOI](https://doi.org/10.1145/3397271.3401233) · [arXiv:2005.13829](https://arxiv.org/abs/2005.13829)
- Anelli, V. W., Bellogín, A., Di Noia, T., Jannach, D., Pomo, C. (2022). *Top-N Recommendation Algorithms: A Quest for the State-of-the-Art.* UMAP '22. [arXiv:2203.01155](https://arxiv.org/abs/2203.01155) · [PDF](https://abellogin.github.io/2022/umap.pdf)
- Ferrari Dacrema, M., Cremonesi, P., Jannach, D. (2019). *Are We Really Making Much Progress? A Worrying Analysis of Recent Neural Recommendation Approaches.* RecSys '19. [DOI](https://doi.org/10.1145/3298689.3347058) · [arXiv:1907.06902](https://arxiv.org/abs/1907.06902)
- Dooms, S., De Pessemier, T., Martens, L. (2013). *MovieTweetings: a Movie Rating Dataset Collected From Twitter.* CrowdRec @ RecSys 2013. [Veri kümesi](https://github.com/sidooms/MovieTweetings) — bu yazıda Kasım 2021 anlık görüntüsü kullanıldı.
