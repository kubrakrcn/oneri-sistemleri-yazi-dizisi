# Offline kazandım, online kaybettim

### Modelim geçmiş verilerde açık ara önde bitirdi. Gerçek kullanıcılarda hiçbir şey olmadı. Bu bir kaza değilmiş.

---

Geçen sene bir model üzerinde uzunca bir süre çalıştım.

Elimizdeki geçmiş verilerde, bütün testlerde, eski modelden belirgin biçimde daha iyiydi. Sayılar güzeldi. Grafikler güzeldi. Sunumu yaptım, sorular geldi, cevapladım, herkes memnun ayrıldı. O hafta kendimi fena hissetmedim doğrusu.

Sonra gerçek kullanıcılarla test ettik.

Hiçbir şey değişmedi. Sıfır. Ne daha fazla tıklama, ne daha fazla başvuru. İki grubun eğrileri üst üste bindi, aradaki fark gürültüden ibaretti.

İlk tepkim "bir yerde hata yaptık" oldu. Bölmeyi kontrol ettim. Metrik fonksiyonunu kontrol ettim. Deney kurulumunu baştan aşağı bir daha okudum. Hata yoktu.

Sonra anladım ki bu bir kaza değil, bir kural. Alanın uzun süredir bildiği, konuştuğu, üstüne makaleler yazdığı bir şey. Ben o güne kadar denk gelmemiştim — ya da denk gelmiştim de yeterince ciddiye almamıştım.

Bu yazı, o hafta öğrenmek zorunda kaldığım şeyleri anlatıyor.

---

## Çevrimdışı test tam olarak ne yapıyor?

Kısaca hatırlayalım, çünkü sorunun kaynağı burada.

Elinizde geçmiş etkileşim kayıtları var: kim, neye, ne zaman tıkladı. Bunu ikiye bölüyorsunuz — belli bir tarihe kadar olanlar eğitim, sonrası test. Modeli eğitim kısmıyla eğitiyor, test kısmında "bakalım kullanıcının yaptığı şeyi tahmin edebilecek mi" diye ölçüyorsunuz.

Ucuz, hızlı, tekrarlanabilir. Bir öğleden sonra otuz model deneyebilirsiniz. Bu yüzden herkes bununla çalışıyor ve bu yüzden vazgeçmek de mümkün değil.

Sorun şu ki bu düzenek, üç ayrı yerden sessizce sızdırıyor.

---

## Sebep 1 — Elimizdeki veri, dünyanın değil, eski modelin fotoğrafı

Test setiniz nereden geliyor? Kullanıcıların geçmişte yaptıklarından.

Peki kullanıcılar neye tıklayabildi? Yalnızca kendilerine gösterilen şeylere.

Yani test verisi, dünyanın tarafsız bir kesiti değil. **Eski modelin ne gösterdiğinin kaydı.**

Şimdi düşünün. Yeni modeliniz, hiç gösterilmemiş harika bir ilanı listenin başına koydu. Bunu ödüllendirebilir misiniz?

Hayır. Çünkü o ilanın tıklanıp tıklanmayacağını bilmiyorsunuz. Kullanıcı onu hiç görmedi ki bir tepki versin. Veride yok, dolayısıyla isabet sayılmıyor, dolayısıyla modeliniz ceza alıyor.

Sonuç: çevrimdışı test, eski modele benzeyen modelleri ödüllendirir; farklı bir şey deneyenleri cezalandırır. Ve bu tam olarak duymak istemediğiniz şeydir, çünkü yenilik dediğiniz şey zaten "farklı bir şey denemek"tir.

---

## Sebep 2 — Listenin başındaki her zaman kazanır

Bu benim en sevdiğim kısım, çünkü kanıtı çok net.

Joachims ve arkadaşları 2005'te bir çalışma yaptı: kullanıcıları arama motoru kullanırken göz izleme cihazıyla takip ettiler, sonra da sonuçların sırasıyla oynadılar.

İki bulgu var ve ikisi de rahatsız edici.

**Birincisi:** insanlar birinci ve ikinci sonuca neredeyse aynı oranda bakıyor. Sonuç sayfalarının yaklaşık %80'inde birinci sıraya, yaklaşık %75'inde ikinci sıraya göz atılmış. Yani ikinci sonuç görülmüyor değil, gayet de görülüyor. Ama birinciye çok daha fazla tıklanıyor.

**İkincisi, asıl çarpıcı olanı:** araştırmacılar ilk iki sonucun yerini gizlice değiştirdiler. Yani daha alakasız olanı birinci sıraya koydular.

Kullanıcılar yine birinciye tıkladı.

Makalenin kendi ifadesiyle: yer değiştirilmiş durumda bile, ikinci özet daha alakalı olsa da birinci bağlantıya tıklama yönünde güçlü bir eğilim var. Sayılara bakalım: birinci sıradaki sonucun ikinciden gerçekten daha alakasız olduğu durumlarda bile, kullanıcılar birinciye 10 kez, gerçekten daha alakalı olan ikinciye yalnızca 7 kez tıklamış.

İnsanlar sadece sonuca güvenmiyor. **Sıralamanın kendisine güveniyorlar.**

Şimdi bunun modelinize ne yaptığını düşünün. Eğitim verinizdeki tıklamaların bir kısmı "bu iyi bir öneriydi" demiyor, "bu üstteydi" diyor. Siz de farkında olmadan modelinize şunu öğretiyorsunuz: *üste ne konursa o tıklanıyor, o zaman popüler olanı üste koy.*

Ve bu model, çevrimdışı testte harika görünür. Çünkü geçmişte de popüler olanlar üstteydi ve tıklanmıştı. Kendi kuyruğunu yiyen bir döngü.

---

## Sebep 3 — Ölçtüğümüz şey, istediğimiz şey değil

Üçüncüsü en sinsisi, çünkü teknik değil.

Bir iş ilanı öneri sisteminde gerçekten istediğimiz şey ne? Adayın işe girmesi. İşverenin doğru kişiyi bulması.

Peki biz neyi ölçüyoruz? Tıklamayı. Olsa olsa başvuruyu.

Aradaki mesafe uçurum gibi. Tıklama anında ölçülüyor — anlık, temiz, bol. Başvurunun sonucu haftalar sonra belli oluyor. Görüşme yapıldı mı, teklif verildi mi, kişi işe başladı mı? Bunların çoğu sistemin dışında yaşanıyor ve bize hiç geri dönmüyor.

Bu yüzden ölçebildiğimizi optimize ediyoruz. Ve bir vekil ölçütü yeterince uzun süre optimize ederseniz, bir noktada vekil iyileşmeye devam ederken asıl hedef yerinde saymaya başlar.

Bu, sadece öneri sistemlerinin değil, uygulamalı makine öğrenmesinin tamamının en eski tuzağı.

---

## Peki çevrimdışı testi çöpe mi atalım?

Hayır. Çöpe atarsanız her fikri A/B testine sokmak zorunda kalırsınız; bu da haftalar, trafik ve çoğu zaman sabır demek. Kimsede o kadar yok.

Çevrimdışı testin işlevini değiştirmek lazım. **Karar aracı değil, eleme aracı.**

Dört pratik şey:

**1. Her zaman bir temel model koyun — ve onu düzgün ayarlayın.**

Bu, alanın kendi içinde yaptığı bir özeleştirinin de merkezinde. Dacrema, Cremonesi ve Jannach'ın 2019'daki çalışması üst düzey konferanslarda yayımlanmış on sekiz derin öneri modelini yeniden üretmeye çalıştı. Yalnızca yedisi makul bir çabayla yeniden üretilebildi. O yedinin altısı ise, iyi ayarlanmış basit komşuluk yöntemleriyle çoğu durumda geçilebildi.

Dikkat: bu, derin öğrenme işe yaramaz demek değil. Bu, **karşılaştırmalarımızın çoğunun adil olmadığı** demek. Kendi yönteminizi günlerce ayarlayıp, karşısındaki temel modeli varsayılan ayarlarla bir kez çalıştırıp geçerseniz, sonuç baştan bellidir. Kimse kötü niyetli değil; sadece insan böyle.

**2. Konum yanlılığını düzeltin, görmezden gelmeyin.**

Bunun için geliştirilmiş yöntemler var. Joachims, Swaminathan ve Schnabel'in 2017'deki çalışması, tıklama verisindeki konum yanlılığını ters eğilim ağırlıklandırmasıyla düzeltip yansız bir sıralama öğrenme çerçevesi kuruyor. Fikir basit: bir öğenin tıklanma ihtimalini, o öğenin *bulunduğu konumdan dolayı* görülme ihtimaline bölüyorsunuz.

Uygulaması basit değil, ama en azından ne ölçtüğünüzü biliyorsunuz.

**3. Küçük bir keşif bütçesi ayırın.**

Trafiğin çok küçük bir kısmında sıralamayı bilinçli olarak biraz karıştırın. Kısa vadede biraz performans kaybedersiniz. Karşılığında, eski modelinizin hiç göstermediği öğeler hakkında veri toplarsınız — yani gelecekteki çevrimdışı testlerinizin kör noktasını küçültürsünüz.

Bunu yapmayan her sistem, zamanla kendi geçmişinin içine kapanıyor.

**4. A/B testini baştan planlayın.**

Hangi metriğe bakacağınıza, ne kadar süre bekleyeceğinize ve hangi farkı "gerçek" sayacağınıza testi başlatmadan önce karar verin. Test bittikten sonra verilere bakıp anlamlı çıkanı seçmek, kendinizi kandırmanın en zarif yolu.

---

## Son olarak

O modeli hiç yayına almadık. Öğrendiğim şey ise dönem boyunca peşimi bırakmadı, ve şimdi öğrencilerime de aynı soruyu soruyorum:

**Ölçtüğünüz şey, gerçekten önemsediğiniz şey mi?**

Cevap çoğu zaman "tam olarak değil" oluyor. Sorun burada değil — bir vekil ölçüt kullanmak zorundayız, başka çaremiz yok. Sorun, aradaki farkı unuttuğumuz an başlıyor.

---

*Bu yazı, bu dönem İstanbul Ticaret Üniversitesi ve Nevşehir Hacı Bektaş Veli Üniversitesi'nde verdiğim Öneri Sistemleri Algoritmaları dersinden çıkan bir yazı dizisinin ilk bölümü. Sırada: "Filmin hayır deme hakkı yok, işverenin var."*

---

### Kaynaklar

- Joachims, T. ve ark. (2005). *Accurately Interpreting Clickthrough Data as Implicit Feedback.* SIGIR 2005. [PDF](https://www.cs.cornell.edu/people/tj/publications/joachims_etal_05a.pdf)
- Joachims, T., Swaminathan, A., Schnabel, T. (2017). *Unbiased Learning-to-Rank with Biased Feedback.* WSDM 2017. [arXiv:1608.04468](https://arxiv.org/abs/1608.04468)
- Dacrema, M. F., Cremonesi, P., Jannach, D. (2019). *Are We Really Making Much Progress? A Worrying Analysis of Recent Neural Recommendation Approaches.* RecSys 2019. [arXiv:1907.06902](https://arxiv.org/abs/1907.06902)

**Daha fazla okuma** — çevrimdışı ve çevrimiçi sonuçların karşılaştırıldığı iki çalışma:

- Garcin, F. ve ark. (2014). *Offline and Online Evaluation of News Recommender Systems at swissinfo.ch.* RecSys 2014. [DOI](https://dl.acm.org/doi/10.1145/2645710.2645745)
- Rossetti, M., Stella, F., Zanker, M. (2016). *Contrasting Offline and Online Results when Evaluating Recommendation Algorithms.* RecSys 2016. [DOI](https://dl.acm.org/doi/10.1145/2959100.2959176)
