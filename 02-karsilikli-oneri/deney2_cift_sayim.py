"""
Tek taraflı değerlendirme neyi göremiyor? — kurgu örnek

Yang ve ark. (KDD 2024) şunu söylüyor: karşılıklı bir sistemde iki tarafın NDCG'sini
ayrı ayrı hesaplayıp ortalamasını almak, aynı eşleşmeyi iki kez saymaya yol açıyor.
Bu betik o cümleyi elle tutulur hale getiriyor.

Burada veri yok, kurgu var — ve kasten öyle. Çünkü gösterilmek istenen şey bir
ölçütün *kör noktası*: iki tarafın NDCG'si sabit tutulurken, sistemin gerçekte kaç
farklı çifti bir araya getirdiği iki katına çıkabiliyor. Ölçüt bunu göremiyor.

Kurgu
-----
n aday, n işveren. Gerçek karşılıklı ilgi çiftleri: her aday a için
b = (a + s) mod n,  s = 0..g-1.  Yani her adayın g, her işverenin de g gerçek eşi var.

Her iki taraf da k uzunluğunda liste alıyor ve her listede tam h gerçek eş var,
hep aynı sıralarda (1..h). Dolayısıyla NDCG_aday ve NDCG_isveren bütün senaryolarda
AYNI. Değişen tek şey, işveren tarafının hangi h eşi seçtiği:

  ortusme = 1,0  -> işverenler, adayların listelerinde zaten yakalanmış çiftleri seçiyor
  ortusme = 0,0  -> işverenler tamamen başka çiftleri seçiyor

Ölçütler
--------
  tek_tarafli_basari : |aday isabetleri| + |işveren isabetleri|  (bağımsız değerlendirmenin saydığı)
  farkli_cift        : iki tarafın isabetlerinin BİRLEŞİMİ      (kaç farklı çifte dokunuldu)
  cift_tarafli       : KESİŞİM — iki tarafın birbirini gördüğü çiftler
  sisme              : tek_tarafli_basari / farkli_cift         (1,00 = çifte sayım yok)

Not: "doğru" iki taraflı ölçüt, platformun eşleşme tanımına bağlı. Eşleşme için iki
tarafın da karşısındakini görmesi gerekiyorsa kesişim, yalnızca bir tarafın görmesi
yetiyorsa birleşim anlamlı. Buradaki iddia bunlardan hangisinin doğru olduğu değil:
tek taraflı ortalama ikisini de göremiyor.

Çıktı: sonuclar_cift_sayim.csv
"""
import numpy as np, pandas as pd
from itertools import product

K = 5          # liste uzunluğu
G = 6          # her tarafın gerçek eş sayısı
H = 3          # her listede yakalanan gerçek eş sayısı
N = 200        # her taraftan kişi sayısı

DISC = 1.0 / np.log2(np.arange(2, K + 2))


def ndcg(isabet_siralari, gercek_sayisi):
    """isabet_siralari: 0 tabanlı sıralar. İdeal: ilk min(K, g) sıra dolu."""
    dcg = sum(DISC[r] for r in isabet_siralari)
    idcg = DISC[: min(K, gercek_sayisi)].sum()
    return dcg / idcg


def kur(n, g, h, ortusme_payi):
    """İki tarafın listelerini kurar. Döner: (aday_isabetleri, isveren_isabetleri)
    küme olarak (aday, isveren) çiftleri."""
    # aday tarafı: her a, s = 0..h-1 olan eşlerini yakalıyor
    aday = {(a, (a + s) % n) for a in range(n) for s in range(h)}

    # işveren tarafı: her b, h eş seçiyor. Seçimin kaçı adayın yakaladıklarından?
    kac_ortak = int(round(h * ortusme_payi))
    isveren = set()
    for b in range(n):
        esler = [((b - s) % n, b) for s in range(g)]
        ortak = [c for c in esler if c in aday]          # h tane
        digerleri = [c for c in esler if c not in aday]  # g-h tane
        secim = ortak[:kac_ortak] + digerleri[: h - kac_ortak]
        assert len(secim) == h, "seçim kurulamadı: h, g-h'den büyük olmasın"
        isveren.update(secim)
    return aday, isveren


print(f"kurulum: n={N} aday / {N} işveren, her tarafın {G} gerçek eşi, "
      f"liste uzunluğu {K}, listede {H} isabet")
print(f"gerçek karşılıklı çift sayısı: {N*G:,}\n")

satirlar = []
for pay in [0.0, 1 / 3, 2 / 3, 1.0]:
    aday, isveren = kur(N, G, H, pay)
    # NDCG: her iki tarafta da isabetler 1..H sıralarında
    nd_a = ndcg(range(H), G)
    nd_b = ndcg(range(H), G)
    tek = len(aday) + len(isveren)
    birlesim = len(aday | isveren)
    kesisim = len(aday & isveren)
    satirlar.append(dict(
        ortusme=round(pay, 4),
        NDCG_aday=round(nd_a, 4), NDCG_isveren=round(nd_b, 4),
        tek_tarafli_ortalama=round((nd_a + nd_b) / 2, 4),
        tek_tarafli_basari=tek, farkli_cift=birlesim, cift_tarafli=kesisim,
        sisme=round(tek / birlesim, 4)))
    print(f"örtüşme={pay:.2f} | NDCG aday={nd_a:.4f}  işveren={nd_b:.4f}  "
          f"ortalama={(nd_a+nd_b)/2:.4f}  || tek taraflı başarı={tek:,}  "
          f"farklı çift={birlesim:,}  çift taraflı={kesisim:,}  şişme={tek/birlesim:.2f}")

tablo = pd.DataFrame(satirlar)
tablo.to_csv("sonuclar_cift_sayim.csv", index=False)

print(f"\ntek taraflı ortalama bütün satırlarda aynı mı: "
      f"{tablo.tek_tarafli_ortalama.nunique() == 1}  "
      f"(değer {tablo.tek_tarafli_ortalama.iloc[0]:.4f})")
print(f"farklı çift sayısı aralığı: {tablo.farkli_cift.min():,} – {tablo.farkli_cift.max():,}")
print(f"şişme aralığı: {tablo.sisme.min():.2f} – {tablo.sisme.max():.2f}")

# ---------------------------------------------------------------- elle takip edilebilir örnek
print("\n--- elle kontrol edilebilir küçük örnek: n=6, g=4, h=2 ---")
for pay in [0.0, 1.0]:
    a6, i6 = kur(6, 4, 2, pay)
    print(f"\nörtüşme={pay:.0f}")
    print("  aday tarafının yakaladığı çiftler  :", sorted(a6))
    print("  işveren tarafının yakaladığı çiftler:", sorted(i6))
    print(f"  tek taraflı başarı={len(a6)+len(i6)}  farklı çift={len(a6|i6)}  "
          f"çift taraflı={len(a6&i6)}  şişme={(len(a6)+len(i6))/len(a6|i6):.2f}")

print("\n-> sonuclar_cift_sayim.csv yazıldı")
