"""
Tıkanma–isabet takası — MovieTweetings (Dooms ve ark., 2013)

Film verisi üzerinde, çünkü iş ilanı verisi paylaşılamıyor. Film "hayır" demez,
dolayısıyla burada gerçek bir kapasite kısıtı yok; kısıtı biz dayatıyoruz.
Gösterilmek istenen şey şu: bir öğenin kaç listede görünebileceğine üst sınır
koyduğunuzda isabet ne kadar düşüyor, tıkanma ne kadar iyileşiyor.

Tıkanma ölçütü, Bied ve ark. (2021) tanımı:
    MS_l(j)        = (1 / (n*l)) * |{ i : j, i'nin ilk l önerisinde }|
    Congestion@l   = SUM_j MS_l(j) * log MS_l(j)
    normalize      = Congestion@l / log(m)          -> [-1, 0]
m = aday öğe havuzunun büyüklüğü. -1 en iyi (yük dağılmış), 0 en kötü (tek öğeye yığılmış).

DİKKAT — bu sayılar Bied ve ark.'nın sayılarıyla karşılaştırılamaz:
  * normalizasyon log(m)'e bölüyor, m burada 11.216, onlarda 14.200;
  * onlar optimal taşıma kullanıyor, burada açgözlü bir kota var;
  * veri bambaşka (film puanı / iş ilanı).
Ortak olan tek şey takasın yönü.

Kurulum 03'teki deneyle aynı: eğitim < 2020-01-01, test = 2020.

Çıktı: sonuclar_tikanma.csv
"""
import numpy as np, pandas as pd
from scipy.sparse import csr_matrix

RNG = np.random.default_rng(20261102)
K = 10
MIN_ITEM = 5
MIN_USER = 5
TOPN = 200
KOTALAR = [None, 2000, 1000, 500, 200, 100, 50, 20, 10, 5, 2]

# ---------------------------------------------------------------- veri (03 ile aynı)
df = pd.read_csv("ratings.dat", sep="::", engine="python", names=["u", "i", "r", "t"])
df["d"] = pd.to_datetime(df.t, unit="s")
CUT, END = pd.Timestamp("2020-01-01"), pd.Timestamp("2021-01-01")
tr = df[df.d < CUT].copy()
te = df[(df.d >= CUT) & (df.d < END)].copy()

cnt = tr.i.value_counts()
items = cnt[cnt >= MIN_ITEM].index
tr = tr[tr.i.isin(items)]
te = te[te.i.isin(items)]
ucnt = tr.u.value_counts()
tr = tr[tr.u.isin(ucnt[ucnt >= MIN_USER].index)]
eval_users = np.intersect1d(te.u.unique(), tr.u.unique())
te = te[te.u.isin(eval_users)]

uid = {u: k for k, u in enumerate(np.sort(tr.u.unique()))}
iid = {i: k for k, i in enumerate(np.sort(tr.i.unique()))}
n_u, n_i = len(uid), len(iid)
X = csr_matrix((np.ones(len(tr), np.float32),
                (tr.u.map(uid).to_numpy(), tr.i.map(iid).to_numpy())), shape=(n_u, n_i))
X.data[:] = 1.0

truth = {}
for u, g in te.groupby("u"):
    idx = [iid[i] for i in g.i if i in iid]
    if idx:
        truth[uid[u]] = set(idx)
satirlar_u = np.array(sorted(truth))
print(f"eğitim {len(tr):,} · öğe {n_i:,} · değerlendirilen kullanıcı {len(satirlar_u):,}")

# ---------------------------------------------------------------- skor kaynakları
pop = np.asarray(X.sum(axis=0)).ravel()
son90 = tr[tr.d >= CUT - pd.Timedelta(days=90)]
pop90 = np.zeros(n_i)
np.add.at(pop90, son90.i.map(iid).to_numpy(), 1.0)

norm = np.sqrt(pop); norm[norm == 0] = 1.0
Xn = X.multiply(1.0 / norm).tocsr().astype(np.float32)
Xc = Xn.tocsc()
D, I, Pt = [], [], [0]
for j in range(n_i):
    col = np.asarray((Xc[:, j].T @ Xn).todense()).ravel()
    col[j] = 0.0
    nb = np.argpartition(-col, TOPN)[:TOPN] if col.size > TOPN else np.arange(col.size)
    nb = nb[col[nb] > 0]
    D.append(col[nb].astype(np.float32)); I.append(nb); Pt.append(Pt[-1] + nb.size)
S = csr_matrix((np.concatenate(D), np.concatenate(I), np.array(Pt)), shape=(n_i, n_i))
KNN = (X @ S).tocsr()


def skor_vektoru(kaynak, r):
    if kaynak == "knn":
        s = np.zeros(n_i, np.float32)
        seg = slice(KNN.indptr[r], KNN.indptr[r + 1])
        s[KNN.indices[seg]] = KNN.data[seg]
        return s
    return (pop90 if kaynak == "pop90" else pop).astype(np.float64)


# ---------------------------------------------------------------- ölçütler
DISC = 1.0 / np.log2(np.arange(2, K + 2))


def tikanma(sayim):
    """Bied ve ark. (2021) normalize tıkanma göstergesi; [-1, 0], -1 iyi."""
    ms = sayim / sayim.sum()
    nz = ms[ms > 0]
    return float((nz * np.log(nz)).sum() / np.log(len(sayim)))


def taban_tikanma(n_slot, m):
    """Tam sayı kısıtı altında ulaşılabilir en iyi (en düşük) tıkanma."""
    taban = np.full(m, n_slot // m, dtype=float)
    taban[: n_slot % m] += 1
    return tikanma(taban)


def listeler_uret(kaynak, kota, sira):
    """Her kullanıcıya K öğe. kota=None ise serbest; değilse bir öğe en çok
    'kota' listede görünebilir. Açgözlü: kullanıcılar 'sira' düzeninde seçiyor."""
    kalan = None if kota is None else np.full(n_i, kota, dtype=np.int64)
    out = {}
    for r in sira:
        s = skor_vektoru(kaynak, r).copy()
        s[X.indices[X.indptr[r]:X.indptr[r + 1]]] = -np.inf
        if kalan is None:
            top = np.argpartition(-s, K)[:K]
            top = top[np.argsort(-s[top])]
        else:
            duzen = np.argsort(-s)
            top = []
            for j in duzen:
                if s[j] == -np.inf:
                    break
                if kalan[j] > 0:
                    top.append(j); kalan[j] -= 1
                    if len(top) == K:
                        break
            top = np.array(top, dtype=np.int64)
        out[r] = top
    return out


def olc(listeler):
    P = R = N = 0.0
    sayim = np.zeros(n_i)
    for r, top in listeler.items():
        gercek = truth[r]
        hit = np.fromiter((t in gercek for t in top), bool, len(top))
        P += hit.sum() / K
        R += hit.sum() / len(gercek)
        idcg = DISC[:min(K, len(gercek))].sum()
        N += DISC[:len(top)][hit].sum() / idcg if idcg > 0 else 0.0
        np.add.at(sayim, top, 1.0)
    n = len(listeler)
    return (P / n, R / n, N / n, tikanma(sayim), (sayim > 0).sum() / n_i)


# ---------------------------------------------------------------- tarama
duz = satirlar_u
karisik = RNG.permutation(satirlar_u)
print(f"\nulaşılabilir en iyi tıkanma ({len(duz)}x{K} yuva, {n_i} öğe): "
      f"{taban_tikanma(len(duz) * K, n_i):.4f}")

cikti = []
for kaynak, ad in [("pop90", "Popülerlik (son 90 gün)"), ("knn", "Öğe-öğe kNN")]:
    print(f"\n[{ad}]")
    for kota in KOTALAR:
        p, r, n, tik, kap = olc(listeler_uret(kaynak, kota, duz))
        p2, r2, n2, tik2, _ = olc(listeler_uret(kaynak, kota, karisik))
        etiket = "kota yok" if kota is None else f"kota={kota}"
        print(f"  {etiket:<10} R@10={r:.4f}  NDCG@10={n:.4f}  tıkanma={tik:+.4f}  "
              f"kapsam={kap*100:5.2f}%   (karışık sırayla R@10={r2:.4f}, tıkanma={tik2:+.4f})")
        cikti.append(dict(model=ad, kota=("yok" if kota is None else kota),
                          P10=round(p, 4), R10=round(r, 4), NDCG10=round(n, 4),
                          tikanma=round(tik, 4), kapsam=round(kap, 4),
                          R10_karisik_sira=round(r2, 4), tikanma_karisik_sira=round(tik2, 4)))

pd.DataFrame(cikti).to_csv("sonuclar_tikanma.csv", index=False)
print("\n-> sonuclar_tikanma.csv yazıldı")
