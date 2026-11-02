"""
Konum yanlılığı simülasyonu — çevrimdışı metrik neyi ödüllendiriyor?

Burada gerçek veri yok; kasten yok. Çünkü göstermek istediğim şey ancak gerçek
alakanın bilindiği bir dünyada görülebiliyor: çevrimdışı test, eski modele benzeyen
modeli mi ödüllendiriyor, yoksa gerçekten iyi olanı mı?

Kurgu
-----
* M öğe, N kullanıcı. Gerçek alaka p(u,i) = sigmoid(theta_u . beta_i).
* Her öğenin bir de "gösterim ağırlığı" w_i var (Zipf). w ile beta ilişkisiz
  üretiliyor: popüler olmak, alakalı olmak demek değil.
* Kayıt politikası (eski model) w_i'ye göre sıralıyor, kullanıcı başına Gumbel
  gürültüyle (Plackett-Luce) ilk 20 öğeyi gösteriyor.
* Tıklama modeli konum tabanlı: tıklama = (konum incelendi) ve (öğe alakalı sayıldı).
  İnceleme olasılıkları Joachims ve ark. (2005) göz izleme bulgusundan: 1. sırada
  0,80, 2. sırada 0,75. UYARI: makale yalnızca bu iki değeri veriyor; 3. sıradan
  sonrası bu betikte geometrik azalma olarak VARSAYILDI, ölçülmüş değil.
* Güven yanlılığı: üst sıraya, alakasız olsa da tıklanıyor. Katsayısı, aynı
  makaledeki "1. sıradaki gerçekten daha alakasızken bile kullanıcılar birinciye
  10, ikinciye 7 kez tıklıyor" gözlemine kalibre ediliyor; betik ulaştığı oranı
  yazdırıyor.

Karşılaştırılan sıralamalar (hepsi global öğe skoru, personalizasyon yok)
-----------------------------------------------------------------------
  Kayıt politikası     w_i  (eski modelin kendisi)
  Ham tıklama          dönem 1'de i'ye gelen tıklama sayısı
  Konum IPS            aynı tıklamalar, gösterildiği konumun inceleme olasılığına bölünmüş
  Gösterim IPS (CTR)   tıklama / gösterim sayısı, küçük bir büzüşme ile
  Gerçek alaka         ortalama_u p(u,i)  — yalnızca simülatör bilir

İki ayrı ölçüt
--------------
  ÇEVRİMDIŞI  : dönem 2'nin tıklama kaydına karşı P@10 / NDCG@10
  GERÇEK      : önerilen ilk 10 öğenin ortalama gerçek alakası

Son sütun, her listenin kayıt politikasının ilk 10'uyla kaç öğe paylaştığı.
"Çevrimdışı metrik eski modele benzeyeni ödüllendiriyor" cümlesi ancak bu sütunla
birlikte okunduğunda bir iddia; tek başına bir temenni.

Çıktı: sonuclar_konum.csv
"""
import numpy as np, pandas as pd

RNG = np.random.default_rng(20261102)

N = 20_000          # kullanıcı
M = 2_000           # öğe
D = 8               # gizli boyut
L = 20              # bir listede gösterilen öğe sayısı
K = 10              # metrik kesme noktası

# ---------------------------------------------------------------- gerçek dünya
theta = RNG.normal(0, 1, (N, D))
beta = RNG.normal(0, 1, (M, D))
logit = theta @ beta.T / np.sqrt(D) - 2.6          # ortalama alaka ~ %10
REL = 1.0 / (1.0 + np.exp(-logit))                 # p(u,i)
print(f"gerçek alaka: ortalama {REL.mean():.4f}, "
      f"öğe ortalamalarının aralığı {REL.mean(0).min():.4f}–{REL.mean(0).max():.4f}")

# gösterim ağırlığı: Zipf, alakayla ilişkisiz
w = 1.0 / (1.0 + np.arange(M))
w = w[RNG.permutation(M)]
oge_alaka = REL.mean(0)
print(f"popülerlik ile gerçek alaka korelasyonu: "
      f"{np.corrcoef(np.log(w), oge_alaka)[0,1]:+.4f}  (kurgu gereği ~0)")

# ---------------------------------------------------------------- tıklama modeli
INCELEME = np.empty(L)
INCELEME[0], INCELEME[1] = 0.80, 0.75              # Joachims ve ark. 2005
AZALMA = 0.80                                      # VARSAYIM: 3. sıradan sonrası
for k in range(2, L):
    INCELEME[k] = INCELEME[k - 1] * AZALMA


def liste_uret(n_kullanici, tohum):
    """Kayıt politikasının her kullanıcıya gösterdiği L öğe (Plackett-Luce)."""
    r = np.random.default_rng(tohum)
    skor = np.log(w)[None, :] + r.gumbel(0, 1.0, (n_kullanici, M))
    top = np.argpartition(-skor, L, axis=1)[:, :L]
    sira = np.take_along_axis(skor, top, 1)
    return np.take_along_axis(top, np.argsort(-sira, axis=1), 1)


def tiklama_uret(listeler, tau0, tohum):
    """Konum + güven yanlılıklı tıklamalar. Döner: (kullanıcı, konum) boole matrisi."""
    r = np.random.default_rng(tohum)
    n = listeler.shape[0]
    rel = np.take_along_axis(REL[:n], listeler, 1)
    tau = tau0 / (1.0 + np.arange(L))              # güven, konumla hızla sönüyor
    p_alakali = rel + tau[None, :] * (1.0 - rel)
    return r.random((n, L)) < (INCELEME[None, :] * p_alakali)


# --- güven katsayısını 10:7 gözlemine kalibre et
listeler_k = liste_uret(4_000, 1)
rel_k = np.take_along_axis(REL[:4_000], listeler_k, 1)
secim = rel_k[:, 1] > rel_k[:, 0]                  # 2. sıradaki gerçekten daha alakalı
print(f"\nkalibrasyon: 2. sıradaki daha alakalı olan {secim.sum():,} liste")
en_iyi, en_iyi_fark = 0.0, 9e9
for tau0 in np.arange(0.0, 1.01, 0.01):
    c = tiklama_uret(listeler_k, tau0, 7)
    o = c[secim, 0].sum() / max(1, c[secim, 1].sum())
    if abs(o - 10 / 7) < en_iyi_fark:
        en_iyi, en_iyi_fark = tau0, abs(o - 10 / 7)
c = tiklama_uret(listeler_k, en_iyi, 7)
oran = c[secim, 0].sum() / c[secim, 1].sum()
print(f"seçilen güven katsayısı tau0 = {en_iyi:.2f} -> ulaşılan oran "
      f"{c[secim,0].sum()}:{c[secim,1].sum()} = {oran:.2f}  (hedef 10:7 = 1,43)")

# ---------------------------------------------------------------- iki dönem
L1 = liste_uret(N, 11)
C1 = tiklama_uret(L1, en_iyi, 12)
L2 = liste_uret(N, 21)
C2 = tiklama_uret(L2, en_iyi, 22)
print(f"\ndönem 1: {C1.sum():,} tıklama ({C1.sum()/(N*L)*100:.2f}% gösterim başına)")
print(f"dönem 2: {C2.sum():,} tıklama")

# ---------------------------------------------------------------- modeller
ham = np.zeros(M)
np.add.at(ham, L1[C1], 1.0)

ips = np.zeros(M)
konum = np.broadcast_to(np.arange(L), L1.shape)
np.add.at(ips, L1[C1], 1.0 / INCELEME[konum[C1]])

# gösterim sayısı: hangi öğe dönem 1'de kaç kez listeye girdi
gosterim = np.zeros(M)
np.add.at(gosterim, L1.ravel(), 1.0)
print(f"dönem 1'de en az bir kez gösterilen öğe: {(gosterim > 0).sum():,} / {M:,}")
BUZUSME = 20.0                                     # az gösterilen öğeyi ortalamaya çeker
ctr = ham / (gosterim + BUZUSME)

modeller = {
    "Kayıt politikası (popülerlik)": np.log(w),
    "Ham tıklama sayısı": ham,
    "Konum IPS": ips,
    "Gösterim IPS (CTR, büzüşmeli)": ctr,
    "Gerçek alaka (oracle)": oge_alaka,
}

# ---------------------------------------------------------------- değerlendirme
DISC = 1.0 / np.log2(np.arange(2, K + 2))
# dönem 2'nin tıklama kaydı: kullanıcı -> tıkladığı öğeler
tiklanan = [set() for _ in range(N)]
us, ks = np.nonzero(C2)
for u, k in zip(us, ks):
    tiklanan[u].add(int(L2[u, k]))
olcumlu = np.array([u for u in range(N) if tiklanan[u]])
print(f"çevrimdışı değerlendirmede puanlanan kullanıcı: {len(olcumlu):,}")

politika_top = set(np.argsort(-np.log(w))[:K].tolist())

satirlar = []
for ad, skor in modeller.items():
    top = np.argsort(-skor)[:K]                    # global sıralama, herkese aynı liste
    gercek_alaka = REL[:, top].mean()
    ortusme = len(politika_top & set(top.tolist()))
    P = N_ = 0.0
    for u in olcumlu:
        g = tiklanan[u]
        hit = np.fromiter((int(t) in g for t in top), bool, K)
        P += hit.sum() / K
        idcg = DISC[:min(K, len(g))].sum()
        N_ += DISC[hit].sum() / idcg
    n = len(olcumlu)
    satirlar.append(dict(model=ad, cevrimdisi_P10=round(P / n, 4),
                         cevrimdisi_NDCG10=round(N_ / n, 4),
                         gercek_alaka10=round(float(gercek_alaka), 4),
                         politikayla_ortusme=ortusme))
    print(f"  {ad:<32} çevrimdışı P@10={P/n:.4f}  NDCG@10={N_/n:.4f}  "
          f"| gerçek alaka={gercek_alaka:.4f} | politikayla örtüşme {ortusme}/{K}")

tablo = pd.DataFrame(satirlar)
tablo.to_csv("sonuclar_konum.csv", index=False)

# ---------------------------------------------------------------- özet
ck = tablo.set_index("model")
print("\nçevrimdışı metriğe göre sıralama:",
      " > ".join(ck.cevrimdisi_NDCG10.sort_values(ascending=False).index))
print("gerçek alakaya göre sıralama:    ",
      " > ".join(ck.gercek_alaka10.sort_values(ascending=False).index))
print("\n-> sonuclar_konum.csv yazıldı")
