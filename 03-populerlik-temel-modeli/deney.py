"""
Popülerlik temel modeli deneyi — MovieTweetings (Dooms ve ark., 2013)
Zaman tabanlı bölme: eğitim <= 2019-12-31, test = 2020 yılı.

Karşılaştırılan modeller:
  Rastgele, Ham ortalama puan, Bayes (shrinkage) ortalama,
  Popülerlik (tüm geçmiş), Popülerlik (son 90 gün), Öğe-öğe kNN (kosinüs)

Metrikler: P@10, R@10, NDCG@10, katalog kapsamı@10
"""
import numpy as np, pandas as pd
from scipy.sparse import csr_matrix

RNG = np.random.default_rng(20260928)
K = 10
MIN_ITEM = 5        # eğitim setinde en az bu kadar etkileşim gören öğeler aday
MIN_USER = 5        # en az bu kadar eğitim etkileşimi olan kullanıcılar değerlendirilir

# ---------------------------------------------------------------- veri
df = pd.read_csv("ratings.dat", sep="::", engine="python",
                 names=["u", "i", "r", "t"])
df["d"] = pd.to_datetime(df.t, unit="s")

CUT = pd.Timestamp("2020-01-01")
END = pd.Timestamp("2021-01-01")
tr = df[df.d < CUT].copy()
te = df[(df.d >= CUT) & (df.d < END)].copy()

print(f"eğitim {len(tr):,} etkileşim | test {len(te):,} etkileşim")

# aday öğe havuzu: eğitimde yeterince görülmüş olanlar
cnt = tr.i.value_counts()
items = cnt[cnt >= MIN_ITEM].index
tr = tr[tr.i.isin(items)]
te = te[te.i.isin(items)]

ucnt = tr.u.value_counts()
users_ok = ucnt[ucnt >= MIN_USER].index
tr = tr[tr.u.isin(users_ok)]

# değerlendirilecek kullanıcılar: hem eğitimde hem testte görünenler
eval_users = np.intersect1d(te.u.unique(), tr.u.unique())
te = te[te.u.isin(eval_users)]
print(f"filtre sonrası: {tr.u.nunique():,} kullanıcı, {tr.i.nunique():,} öğe, "
      f"{len(tr):,} eğitim etkileşimi")
print(f"değerlendirilen kullanıcı: {len(eval_users):,} | test etkileşimi: {len(te):,}")

uid = {u: k for k, u in enumerate(np.sort(tr.u.unique()))}
iid = {i: k for k, i in enumerate(np.sort(tr.i.unique()))}
inv_i = np.array(sorted(iid, key=iid.get))
n_u, n_i = len(uid), len(iid)

rows = tr.u.map(uid).to_numpy()
cols = tr.i.map(iid).to_numpy()
X = csr_matrix((np.ones(len(tr), np.float32), (rows, cols)), shape=(n_u, n_i))
X.data[:] = 1.0

# test gerçeği
truth = {}
for u, g in te.groupby("u"):
    idx = [iid[i] for i in g.i if i in iid]
    if idx:
        truth[uid[u]] = set(idx)
eval_rows = np.array(sorted(truth))
print(f"skorlanacak kullanıcı: {len(eval_rows):,}")

# ---------------------------------------------------------------- skorlar
pop = np.asarray(X.sum(axis=0)).ravel()                       # eğitim frekansı

son90 = tr[tr.d >= CUT - pd.Timedelta(days=90)]
pop90 = np.zeros(n_i, np.float64)
np.add.at(pop90, son90.i.map(iid).to_numpy(), 1.0)

g = tr.groupby(tr.i.map(iid)).r
n_i_cnt = g.count().reindex(range(n_i)).fillna(0).to_numpy()
mean_i = g.mean().reindex(range(n_i)).fillna(0).to_numpy()
mu = tr.r.mean()
m = 50.0                                                       # shrinkage sabiti
bayes = (n_i_cnt / (n_i_cnt + m)) * mean_i + (m / (n_i_cnt + m)) * mu

rastgele = RNG.random(n_i)

# ---------------------------------------------------------------- değerlendirme
DISC = 1.0 / np.log2(np.arange(2, K + 2))

def degerlendir(skor_fn, ad):
    """skor_fn(satir) -> n_i uzunluğunda skor vektörü (görülmüşler maskelenmeden)"""
    P = R = N = 0.0
    gorulen = set()
    for r in eval_rows:
        s = skor_fn(r).copy()
        s[X.indices[X.indptr[r]:X.indptr[r + 1]]] = -np.inf   # eğitimde gördüğü
        top = np.argpartition(-s, K)[:K]
        top = top[np.argsort(-s[top])]
        gercek = truth[r]
        hit = np.fromiter((t in gercek for t in top), bool, K)
        P += hit.sum() / K
        R += hit.sum() / len(gercek)
        idcg = DISC[:min(K, len(gercek))].sum()
        N += (DISC[hit].sum() / idcg) if idcg > 0 else 0.0
        gorulen.update(top.tolist())
    n = len(eval_rows)
    print(f"{ad:<28} P@10={P/n:.4f}  R@10={R/n:.4f}  "
          f"NDCG@10={N/n:.4f}  kapsam={len(gorulen)/n_i*100:5.2f}%")
    return P / n, R / n, N / n, len(gorulen) / n_i

sabit = lambda v: (lambda r: v)

sonuc = {}
sonuc["Rastgele"]                    = degerlendir(sabit(rastgele), "Rastgele")
sonuc["Ham ortalama puan"]           = degerlendir(sabit(mean_i), "Ham ortalama puan")
sonuc["Bayes ortalama (m=50)"]       = degerlendir(sabit(bayes), "Bayes ortalama (m=50)")
sonuc["Popülerlik (tüm geçmiş)"]     = degerlendir(sabit(pop), "Popülerlik (tüm geçmiş)")
sonuc["Popülerlik (son 90 gün)"]     = degerlendir(sabit(pop90), "Popülerlik (son 90 gün)")

# öğe-öğe kNN (kosinüs), komşuluk 200 ile budanmış
norm = np.sqrt(pop)
norm[norm == 0] = 1.0
Xn = X.multiply(1.0 / norm).tocsr().astype(np.float32)
Xc = Xn.tocsc()

TOPN = 200
S_data, S_idx, S_ptr = [], [], [0]
for j in range(n_i):
    col = np.asarray((Xc[:, j].T @ Xn).todense()).ravel()
    col[j] = 0.0
    if col.size > TOPN:
        nb = np.argpartition(-col, TOPN)[:TOPN]
    else:
        nb = np.arange(col.size)
    nb = nb[col[nb] > 0]
    S_data.append(col[nb].astype(np.float32)); S_idx.append(nb)
    S_ptr.append(S_ptr[-1] + nb.size)
S = csr_matrix((np.concatenate(S_data), np.concatenate(S_idx), np.array(S_ptr)),
               shape=(n_i, n_i))
print(f"kNN benzerlik matrisi: {S.nnz:,} sıfır olmayan")

KNN = (X @ S).tocsr()                                  # kullanıcı x öğe skorları
def knn_skor(r):
    s = np.zeros(n_i, np.float32)
    seg = slice(KNN.indptr[r], KNN.indptr[r + 1])
    s[KNN.indices[seg]] = KNN.data[seg]
    return s
sonuc["Öğe-öğe kNN (kosinüs)"] = degerlendir(knn_skor, "Öğe-öğe kNN (kosinüs)")

# ---------------------------------------------------------------- uzun kuyruk
pay = np.sort(pop)[::-1]
pay = pay / pay.sum()
print(f"\nöğelerin en popüler %1'i eğitim etkileşimlerinin "
      f"%{pay[:max(1, n_i//100)].sum()*100:.1f}'ini topluyor")
print(f"öğelerin en popüler %10'u %{pay[:n_i//10].sum()*100:.1f}'ini topluyor")

pd.DataFrame(sonuc, index=["P@10", "R@10", "NDCG@10", "kapsam"]).T.to_csv("sonuclar.csv")
print("\n-> sonuclar.csv yazıldı")
