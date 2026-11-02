"""
İkinci tur: temel modele hakkını vermek.
Hem popülerlik penceresini hem de kNN'i ayarlıyoruz ki karşılaştırma adil olsun.
"""
import numpy as np, pandas as pd
from scipy.sparse import csr_matrix

RNG = np.random.default_rng(20260928)
K, MIN_ITEM, MIN_USER = 10, 5, 5

df = pd.read_csv("ratings.dat", sep="::", engine="python", names=["u","i","r","t"])
df["d"] = pd.to_datetime(df.t, unit="s")
CUT, END = pd.Timestamp("2020-01-01"), pd.Timestamp("2021-01-01")
tr, te = df[df.d < CUT].copy(), df[(df.d >= CUT) & (df.d < END)].copy()

cnt = tr.i.value_counts(); items = cnt[cnt >= MIN_ITEM].index
tr, te = tr[tr.i.isin(items)], te[te.i.isin(items)]
ucnt = tr.u.value_counts(); tr = tr[tr.u.isin(ucnt[ucnt >= MIN_USER].index)]
te = te[te.u.isin(tr.u.unique())]

uid = {u:k for k,u in enumerate(np.sort(tr.u.unique()))}
iid = {i:k for k,i in enumerate(np.sort(tr.i.unique()))}
n_u, n_i = len(uid), len(iid)
rows, cols = tr.u.map(uid).to_numpy(), tr.i.map(iid).to_numpy()
X = csr_matrix((np.ones(len(tr), np.float32), (rows, cols)), shape=(n_u, n_i))

# tazelik ağırlıklı kullanıcı-öğe matrisi (yarı ömür 365 gün)
yas = (CUT - tr.d).dt.days.to_numpy()
w = np.exp(-np.log(2) * yas / 365.0).astype(np.float32)
Xw = csr_matrix((w, (rows, cols)), shape=(n_u, n_i))

truth = {}
for u, g in te.groupby("u"):
    idx = [iid[i] for i in g.i if i in iid]
    if idx: truth[uid[u]] = set(idx)
eval_rows = np.array(sorted(truth))
print(f"eğitim {len(tr):,} | test {len(te):,} | öğe {n_i:,} | "
      f"değerlendirilen kullanıcı {len(eval_rows):,}")

DISC = 1.0/np.log2(np.arange(2, K+2))
def degerlendir(skor_fn, ad, yaz=True):
    P=R=N=0.0; gor=set()
    for r in eval_rows:
        s = skor_fn(r).copy()
        s[X.indices[X.indptr[r]:X.indptr[r+1]]] = -np.inf
        top = np.argpartition(-s, K)[:K]; top = top[np.argsort(-s[top])]
        gercek = truth[r]
        hit = np.fromiter((t in gercek for t in top), bool, K)
        P += hit.sum()/K; R += hit.sum()/len(gercek)
        idcg = DISC[:min(K,len(gercek))].sum()
        N += DISC[hit].sum()/idcg if idcg>0 else 0.0
        gor.update(top.tolist())
    n=len(eval_rows); out=(P/n,R/n,N/n,len(gor)/n_i)
    if yaz: print(f"{ad:<34} P@10={out[0]:.4f}  R@10={out[1]:.4f}  "
                  f"NDCG@10={out[2]:.4f}  kapsam={out[3]*100:5.2f}%")
    return out

sabit = lambda v: (lambda r: v)
res = {}

print("\n--- popülerlik penceresi ---")
for gun in (30, 90, 180, 365, 730, None):
    if gun is None:
        p = np.asarray(X.sum(axis=0)).ravel(); ad = "Popülerlik (tüm geçmiş)"
    else:
        sub = tr[tr.d >= CUT - pd.Timedelta(days=gun)]
        p = np.zeros(n_i); np.add.at(p, sub.i.map(iid).to_numpy(), 1.0)
        ad = f"Popülerlik (son {gun} gün)"
    res[ad] = degerlendir(sabit(p), ad)

print("\n--- öğe-öğe kNN ayarları ---")
pop = np.asarray(X.sum(axis=0)).ravel()

def knn_kur(M, alpha, topn, shrink):
    """alpha: popülerlik normalizasyon üssü (0.5 = kosinüs)"""
    norm = np.power(np.maximum(np.asarray(M.sum(axis=0)).ravel(), 1e-9), alpha)
    Mn = M.multiply(1.0/norm).tocsr().astype(np.float32)
    Mc = Mn.tocsc()
    d,ix,pt = [],[],[0]
    for j in range(n_i):
        col = np.asarray((Mc[:, j].T @ Mn).todense()).ravel()
        col[j] = 0.0
        if shrink: col *= 1.0/(1.0+shrink/np.maximum(pop, 1.0))
        nb = np.argpartition(-col, topn)[:topn] if col.size > topn else np.arange(col.size)
        nb = nb[col[nb] > 0]
        d.append(col[nb].astype(np.float32)); ix.append(nb); pt.append(pt[-1]+nb.size)
    S = csr_matrix((np.concatenate(d), np.concatenate(ix), np.array(pt)), shape=(n_i,n_i))
    return (M @ S).tocsr()

def skorlayici(Z):
    def f(r):
        s = np.zeros(n_i, np.float32)
        seg = slice(Z.indptr[r], Z.indptr[r+1])
        s[Z.indices[seg]] = Z.data[seg]
        return s
    return f

for M, mad in ((X,"ikili"), (Xw,"tazelik ağırlıklı")):
    for alpha in (0.5, 0.8):
        for topn in (50, 300):
            ad = f"kNN {mad}, a={alpha}, k={topn}"
            res[ad] = degerlendir(skorlayici(knn_kur(M, alpha, topn, 0.0)), ad)

print("\n--- karma: tazelik ağırlıklı kNN + son 90 gün popülerliği ---")
sub = tr[tr.d >= CUT - pd.Timedelta(days=90)]
p90 = np.zeros(n_i); np.add.at(p90, sub.i.map(iid).to_numpy(), 1.0)
p90n = p90/max(p90.max(),1)
Zw = knn_kur(Xw, 0.5, 300, 0.0)
fw = skorlayici(Zw)
for lam in (0.3, 0.5, 0.7):
    def karma(r, lam=lam):
        s = fw(r); s = s/max(s.max(), 1e-9)
        return (1-lam)*s + lam*p90n
    res[f"Karma (lambda={lam})"] = degerlendir(karma, f"Karma (lambda={lam})")

pd.DataFrame(res, index=["P@10","R@10","NDCG@10","kapsam"]).T.to_csv("sonuclar2.csv")
print("\n-> sonuclar2.csv")
