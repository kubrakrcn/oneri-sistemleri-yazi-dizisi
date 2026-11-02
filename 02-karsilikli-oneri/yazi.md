# Filmin "hayır" deme hakkı yok, işverenin var

### Öneri sistemleri literatürünün büyük kısmı, önerilen şeyin sessiz olduğunu varsayıyor. İş ilanı sessiz değil.

---

Derste MovieLens'i açıyorum. Herkes açıyor, ben de açıyorum; ücretsiz, temiz, küçük, herkesin bildiği bir veri kümesi. Kullanıcılar, filmler, puanlar. Matris çarpımını gösteriyorum, komşuluk hesabını gösteriyorum, ilk öneri listesi ekranda çıkıyor, güzel oluyor.

Sonra işe dönüyorum ve aynı mantığı iş ilanlarına uygulamaya çalışıyorum.

Burada bir şey tıkırdıyor. İlk başta ne olduğunu tam anlamıyorsunuz, sadece bir şeyin oturmadığını hissediyorsunuz. Sonra fark ediyorsunuz:

**Film, kendisine önerilen kullanıcıyı reddedemez.**

*Esaretin Bedeli*'ni birine önerdiniz. Film bundan rahatsız olmaz. "Ben bu izleyiciyle çalışmak istemiyorum" demez. Aynı filmi aynı akşam yüz bin kişiye önerseniz, film yorulmaz, tükenmez, dolmaz. Yarın yine orada durur.

İş ilanı öyle değil. İlanın arkasında bir insan var. O insanın bir kontenjanı, bir takvimi, bir de fikri var. Siz o ilanı beş yüz kişiye "harika uyum" diye gösterdiğinizde, ilan sahibi beş yüz başvuru alıyor — ve bu onun için iyi bir haber olmuyor.

Yani bizim alanda öğrettiğimiz her şeyin altında sessiz bir varsayım yatıyor: **önerilen şey pasiftir.** İşe alımda bu varsayım çöküyor. Ve çöktüğü anda, isabetli bulduğunuz her şey yeniden tanımlanmak zorunda kalıyor.

Bu yazı, o yeniden tanımlamanın dört adımını anlatıyor.

---

## Fark 1 — "Başarı" artık tek taraflı tanımlanamaz

Buna literatürde **karşılıklı öneri** (reciprocal recommendation) deniyor ve tanımı çok net.

Palomares ve arkadaşlarının 2021'deki derleme çalışmasında şöyle geçiyor: bir önerinin işe yaramış sayılması için "her iki kullanıcının da karşılıklılık göstermesi, yani ikisinin de diğeriyle bağlantı kurma önerisinden memnun olması" gerekiyor.

Aynı derleme, klasik öneri sistemleriyle farkı da tek cümlede toparlıyor: geleneksel sistemde "hedef kullanıcı, başarıyı belirleyen tek aktördür."

Tek aktör. İşe alımda böyle bir lüks yok.

Şimdi bunun pratikte ne demek olduğuna bakalım. Yang ve arkadaşlarının KDD 2024'te sunduğu çalışmada gerçek bir işe alım platformundan alınmış bir veri kümesi var: bir tarafta 32.161 aday, diğer tarafta 25.665 işveren tarafı kullanıcısı, aralarında 790.725 etkileşim. Bu etkileşimlerden karşılıklı eşleşmeye dönüşen: 224.636.

Kabaca her dört etkileşimden biri. Yani sistemin ürettiği ilgi sinyallerinin büyük kısmı, diğer taraf "evet" demediği için havada kalıyor.

Bir film öneri sisteminde böyle bir kayıp kalemi yok. Kullanıcı tıkladıysa tıkladı, iş bitti.

---

## Fark 2 — İyi ilan kaybolur, iyi film kaybolmaz

İkinci fark, ilk duyduğumda beni en çok şaşırtan oldu, çünkü bu kadar basit bir şeyin literatürde ayrı bir başlık olmasını beklemiyordum.

Aynı derleme, farkı şöyle koyuyor: klasik sistemlerde ürünler "başarılı bir öneriden sonra da sistemin parçası olmaya devam edebilir", karşılıklı sistemlerde ise taraflar "artık başkasına önerilmek için müsait değildir."

Düşünün. Pozisyon doldu. İlan kapandı. Ama sizin modelinizin son eğitim anındaki hâlinde o ilan hâlâ hayatta, hâlâ gayet alakalı ve hâlâ listelerin başında.

Bu, öneri sisteminizin en iyi tahminlerinin en hızlı bozulan tahminler olması demek. En iyi ilan, en çabuk kapanan ilandır. Bu tuhaf bir denklem ve klasik değerlendirme düzeneğinizde hiç görünmüyor, çünkü geçmiş veride o ilan hâlâ açıktı.

Kapasite tarafı da işin içinde. Tomita ve Yokoyama'nın RecSys 2024 çalışmasında çok net bir cümle var: son derece popüler bir kullanıcı karşı taraftan çok sayıda kişiye önerilse ve çok sayıda ilgi beyanı alsa bile, "anlamlı biçimde ilgilenebileceği bağlantı sayısı fiziksel olarak sınırlıdır."

Fiziksel olarak sınırlı. Bir işe alım uzmanının günü yirmi dört saat, mülakat takvimi de sonlu.

---

## Fark 3 — Popülerlik burada sadece sıkıcı değil, doğrudan zararlı

Popülerlik yanlılığını hepimiz biliyoruz ve klasik anlatıda bunun kötü tarafı çeşitlilik ve keşif oluyor. Herkese aynı on filmi önerirseniz sistem sıkıcılaşır, uzun kuyruk ölür, kullanıcı yeni bir şey bulamaz. Ciddi bir problem ama sonuçta bir *kalite* problemi.

İşe alımda aynı davranış bir *işleyiş* problemine dönüşüyor.

Bied ve arkadaşlarının çalışması buna **tıkanma** (congestion) diyor ve gerekçesini şöyle yazıyor: "aynı karşı konulamaz iş ilanını çok sayıda iş arayana önermek yerinde değildir: bu, nüfus düzeyinde bir tıkanma olgusuna ve bireysel düzeyde zayıf bir nihai memnuniyete yol açar."

Buradaki ifade önemli: *nihai* memnuniyet. Öneri anında herkes memnun. Herkese gerçekten uygun, gerçekten cazip bir ilan gösterdiniz. Sorun, o beş yüz kişinin dördü hariç hepsinin reddedilecek olması. Siz de bunu kendi elinizle organize ettiniz.

Aynı çalışma tıkanmayı ölçülebilir hâle de getiriyor: her ilanın "kaç kullanıcının ilk ℓ önerisinde yer aldığı" oranını alıyor, bunların entropisine bakıyor. Ölçek −1 ile 0 arasında; −1'e yakın olması yükün ilanlara dağıldığı, 0'a yakın olması bir avuç ilana yığıldığı anlamına geliyor.

Ve şimdi rahatsız edici kısım. Aynı makale, 110.000 iş arayan ve 14.200 ilandan oluşan bir veri kümesinde şu tabloyu veriyor: başlangıçtaki gradyan artırma modeli Recall@10 = %31,40 ve tıkanma = −0,62. Yükü dağıtmak için optimal taşıma tabanlı bir yeniden dağıtım uyguladıklarında tıkanma −0,78'e iniyor — ama Recall@10 da %15,31'e düşüyor.

Yarı yarıya isabet kaybı. Tıkanmayı azaltmanın bedeli, en azından bu kurulumda, hiç şakaya gelmiyor.

Bunu neden anlatıyorum? Çünkü "popülerliği cezalandıralım, dağıtalım" cümlesi toplantıda çok makul duyuluyor. Faturasını gören az.

---

## Fark 4 — Metrikler de iki taraflı olmak zorunda

Bu, alanın en yeni ve bence en az konuşulan kısmı.

Karşılıklı bir sistem kurup değerlendirmeye geldiğinizde çoğu ekip şunu yapıyor: aday tarafı için NDCG hesaplıyor, işveren tarafı için NDCG hesaplıyor, ikisinin ortalamasını alıyor, tablonun bir hücresine yazıyor.

Yang ve arkadaşları bunun neden yanlış olduğunu gösteriyor. Problem, "iki tarafın öneri sonuçları birbirine bağlıyken, tek taraflı değerlendirme sürecinin birbirinden bağımsız olması."

Somut örneği de makalenin kendisinden: bir aday ile bir işveren birbirine önerildi ve eşleştiler. Bağımsız değerlendirme bunu iki başarılı öneri sayıyor — "oysa bu, sistemin kurduğu toplam eşleşme sayısını artırmıyor."

Aynı eşleşmeyi iki kere alkışlıyorsunuz. Tablo şişiyor, iş yerinde duruyor.

Makale bunun yerine beş metrik öneriyor; mantığı üç başlıkta toplanıyor: iki tarafın isabetlerinin *birleşimini* ölçen kapsam metrikleri, yalnızca gerçekten çift taraflı olan isabetleri ölçen kararlılık metrikleri, ve iki tarafı büyüklüklerine göre ağırlıklayan bir karşılıklı NDCG.

Ayrıntıdan çok şu fikir önemli: **eşleşme sayısı, iki ayrı sıralama kalitesinin toplamı değil.** Metriğiniz bu ikisini birbirinden ayırt edemiyorsa, neyi iyileştirdiğinizi de bilemezsiniz.

---

## Peki ne yapmalı?

Dört şey, ilk yazıdaki gibi.

**1. Başarı tanımını en baştan çift taraflı yazın.**

Projenin ilk gününde, kod yazılmadan önce. "Başarı = tıklama" diye başlarsanız geri dönüşü zor oluyor; o tanım bütün veri hattına, bütün panolara, bütün hedef değişkenlerine sızıyor. Karşılıklı bir olay tanımlayın: adayın başvurusu *ve* işveren tarafının pozitif bir aksiyonu.

**2. Kapasiteyi model sonrası bir kısıt olarak kabul edin.**

Model bir skor üretir; listeyi kuran katman ise bir kaynağı paylaştırır. Bunlar iki ayrı iştir ve ikincisi genelde hiç yazılmamış olur. Bir ilanın belirli bir pencerede kaç öneri listesinde görünebileceğine dair bir üst sınır, kulağa ilkel gelen ama şaşırtıcı biçimde iyi çalışan bir başlangıçtır.

**3. Tıkanmayı da ölçün — ve isabetle birlikte raporlayın.**

Tek başına bir isabet sayısı, işe alımda eksik bir cümledir. Yanına "bu öneriler kaç farklı ilana dağıldı" sorusunun cevabını koyun. İkisini aynı tabloda görmek, yukarıdaki takası tartışılabilir hâle getiriyor; ayrı ayrı görmek ise sadece iki ayrı yanılgı üretiyor.

**4. Kapanan ilanı, model yenilenmesini beklemeden düşürün.**

Bu bir modelleme işi değil, bir mühendislik işi. Ama karşılıklı bir sistemde en çok değer üreten müdahalelerden biri, çoğu zaman en zarif olanı değil: ölmüş bir ilanı listeden hızlıca çıkarmak.

---

## Son olarak

MovieLens'i dersten çıkarmıyorum, çıkarmam da lazım değil. Mekaniği öğretmenin en temiz yolu o.

Ama artık ikinci saatte şu soruyu soruyorum:

**Önerdiğiniz şeyin "hayır" deme hakkı var mı?**

Cevap "evet" ise, elinizdeki literatürün yarısının varsayımı sizin probleminizde geçerli değil. Bunu bilerek başlamak, sonradan keşfetmekten çok daha ucuz.

---

*Bu yazı, bu dönem İstanbul Ticaret Üniversitesi ve Nevşehir Hacı Bektaş Veli Üniversitesi'nde verdiğim Öneri Sistemleri Algoritmaları dersinden çıkan yazı dizisinin ikinci bölümü. Sırada: "Hiçbir şey öğrenmeyen model neden herkesi yendi?"*

---

### Kaynaklar

- Palomares, I., Porcel, C., Pizzato, L., Guy, I., Herrera-Viedma, E. (2021). *Reciprocal Recommender Systems: Analysis of state-of-art literature, challenges and opportunities towards social recommendation.* Information Fusion, 69, 103–127. [DOI](https://doi.org/10.1016/j.inffus.2020.12.001) · [arXiv:2007.16120](https://arxiv.org/abs/2007.16120)
- Yang, C., Dai, S., Hou, Y., Zhao, W. X., Xu, J., Song, Y., Zhu, H. (2024). *Revisiting Reciprocal Recommender Systems: Metrics, Formulation, and Method.* KDD 2024. [DOI](https://doi.org/10.1145/3637528.3671734) · [arXiv:2408.09748](https://arxiv.org/abs/2408.09748)
- Tomita, Y., Yokoyama, T. (2024). *Fair Reciprocal Recommendation in Matching Markets.* RecSys 2024. [arXiv:2409.00720](https://arxiv.org/abs/2409.00720)
- Bied, G., Perennes, E., Alfonso Naya, V., Caillou, P., Crépon, B., Gaillac, C., Sebag, M. (2021). *Congestion-Avoiding Job Recommendation with Optimal Transport.* FEAST @ ECML-PKDD 2021. [PDF](https://feast-ecmlpkdd.github.io/archive/2021/papers/FEAST2021_paper_4.pdf)
