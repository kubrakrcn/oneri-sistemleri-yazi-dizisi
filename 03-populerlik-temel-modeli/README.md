# 03 — Popülerlik temel modeli

Yazı: **Hiçbir şey öğrenmeyen model neden herkesi yendi?**

Popülerlik temel modelinin tanımındaki tek bir karar — hangi dönemin etkileşimlerini saydığınız —
isabeti yirmi katına çıkarıyor. Aynı veride öğe-öğe kNN, bütün ayarlarına rağmen bu modeli
geçemiyor; ama kataloğun yirmi üç katı kadar öğeye dokunuyor.

## Veri

MovieTweetings (Dooms, De Pessemier, Martens, 2013) — insanların IMDb uygulaması üzerinden
verip Twitter'da paylaştığı film puanları.

Bu deneyde **24 Kasım 2021** tarihli anlık görüntü kullanıldı: 921.398 puan, 71.707 kullanıcı,
38.018 film. Verinin toplanması 2021 sonunda durdu, dolayısıyla depodaki `latest/` klasörü o
tarihten beri değişmiyor. Yine de tekrar üretilebilirlik için commit sabitlenmiş hali veriliyor:

```bash
curl -L -o ratings.dat \
  https://raw.githubusercontent.com/sidooms/MovieTweetings/44c525d0c766944910686c60697203cda39305d6/latest/ratings.dat
```

Kaggle'daki "MovieTweetings 200K / 80K" gibi kopyalar farklı büyüklükte alt kümelerdir;
onlarla bu sayılar çıkmaz.

## Çalıştırmak için

```bash
pip install numpy scipy pandas
python3 deney.py     # temel karşılaştırma     -> sonuclar.csv
python3 deney2.py    # pencere + kNN taraması  -> sonuclar2.csv
```

İki betik de `ratings.dat` dosyasını bulundukları klasörde arar ve çıktıyı yine oraya yazar.
Depoda duran `sonuclar.csv` ve `sonuclar2.csv`, yazıdaki tabloların alındığı ham çıktılardır.

## Kurulum

- **Bölme:** zaman tabanlı. Eğitim `< 2020-01-01`, test 2020 takvim yılı. 2021 verisi kullanılmadı.
- **Filtre:** eğitimde en az 5 kez görülmüş öğeler, en az 5 etkileşimi olan kullanıcılar.
  Geriye 724.318 eğitim etkileşimi, 11.216 film ve değerlendirilebilir 1.691 kullanıcı kalıyor.
- **Eleme:** kullanıcının eğitimde gördüğü öğeler öneri listesinden çıkarılıyor.
- **Metrikler:** P@10, R@10, NDCG@10 ve katalog kapsamı@10.
- **Tohum:** `20260928`.

## Ayar taraması hakkında

Popülerlik penceresi de k da tek bir "en iyi" değer olarak seçilmedi; taramanın tamamı
`sonuclar2.csv` içinde duruyor. En iyisini test dönemine bakarak seçmek, derste anlattığım
gizli sızıntının ta kendisi olurdu. Doğrusu eğitim verisinin son diliminden ayrı bir doğrulama
kümesi ayırmaktır; bu bir ders örneği olduğu için o adım atlandı ve karşılığında bütün satırlar
yayımlandı.

`sonuclar2.csv` yazıda yer almayan satırlar da içeriyor — α = 0,8 taraması, ham ortalama puan,
Bayes ortalaması gibi. Bunlar bilerek bırakıldı.

## Kaynak

Dooms, S., De Pessemier, T., Martens, L. (2013). *MovieTweetings: a Movie Rating Dataset
Collected From Twitter.* CrowdRec @ RecSys 2013.
<https://github.com/sidooms/MovieTweetings>
