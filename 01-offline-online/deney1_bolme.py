"""
Bölme protokolü deneyi — MovieTweetings (Dooms ve ark., 2013)

Aynı veri, aynı modeller, iki ayrı bölme protokolü:
  A) Zamana göre : eğitim < 2020-01-01, test = 2020 takvim yılı
  B) Rastgele    : aynı havuz (< 2021-01-01) karıştırılıp A ile aynı oranda bölünüyor
  B') Rastgele, ama yalnızca A'da değerlendirilen kullanıcılar puanlanıyor

Amaç, rastgele bölmenin aynı modeli ne kadar iyi gösterdiğini ölçmek. B' satırı,
aradaki farkın ne kadarının "değerlendirilen kullanıcı kümesi değişti"den geldiğini
ayırmak için var.

İkinci kısım: zamana göre bölmede test etkileşimlerinin ne kadarı, eğitim
kataloğunda hiç bulunmayan filmlere gidiyor. Bunlar hiçbir modelin ulaşamayacağı
isabetlerdir; çevrimdışı metriğin tavanını belirler.

Çıktı: sonuclar_bolme.csv
"""
import numpy as np, pandas as pd
from scipy.sparse import csr_matrix

RNG = np.random.default_rng(20261102)
K = 10
MIN_ITEM = 5
MIN_USER = 5
TOPN = 200          # kNN komşuluk budaması

# ---------------------------------------------------------------- veri
df = pd.read_csv("ratings.dat", sep="::", engine="python", names=["u", "i", "r", "t"])
df["d"] = pd.to_datetime(df.t, unit="s")

CUT = pd.Timestamp("2020-01-01")
END = pd.Timestamp("2021-01-01")
havuz = df[df.d < END].copy()
print(f"havuz (< 2021-01-01): {len(havuz):,} etkileşim")


# ---------------------------------------------------------------- ortak değerlendirme
def hazirla(tr, te, kisit=None):
    """Filtreleri uygular, seyrek matrisi ve test gerçeğini kurar."""
    cnt = tr.i.value_counts()
    items = cnt[cnt >= MIN_ITEM].index
    tr = tr[tr.i.isin(items)]
    te = te[te.i.isin(items)]

    ucnt = tr.u.value_counts()
    tr = tr[tr.u.isin(ucnt[ucnt >= MIN_USER].index)]

    eval_users = np.intersect1d(te.u.unique(), tr.u.unique())
    if kisit is not None:
        eval_users = np.intersect1d(eval_users, kisit)
    te = te[te.u.isin(eval_users)]

    uid = {u: k for k, u in enumerate(np.sort(tr.u.unique()))}
    iid = {i: k for k, i in enumerate(np.sort(tr.i.unique()))}
    X = csr_matrix((np.ones(len(tr), np.float32),
                    (tr.u.map(uid).to_numpy(), tr.i.map(iid).to_numpy())),
                   shape=(len(uid), len(iid)))
    X.data[:] = 1.0

    truth = {}
    for u, g in te.groupby("u"):
        idx = [iid[i] for i in g.i if i in iid]
        if idx:
            truth[uid[u]] = set(idx)
    return tr, te, X, uid, iid, truth, eval_users


DISC = 1.0 / np.log2(np.arange(2, K + 2))


def degerlendir(skor_fn, X, truth, n_i, ad):
    satirlar = np.array(sorted(truth))
    P = R = N = 0.0
    gorulen = set()
    for r in satirlar:
        s = skor_fn(r).copy()
        s[X.indices[X.indptr[r]:X.indptr[r + 1]]] = -np.inf
        top = np.argpartition(-s, K)[:K]
        top = top[np.argsort(-s[top])]
        gercek = truth[r]
        hit = np.fromiter((t in gercek for t in top), bool, K)
        P += hit.sum() / K
        R += hit.sum() / len(gercek)
        idcg = DISC[:min(K, len(gercek))].sum()
        N += (DISC[hit].sum() / idcg) if idcg > 0 else 0.0
        gorulen.update(top.tolist())
    n = len(satirlar)
    print(f"  {ad:<24} P@10={P/n:.4f}  R@10={R/n:.4f}  NDCG@10={N/n:.4f}  "
          f"kapsam={len(gorulen)/n_i*100:5.2f}%")
    return P / n, R / n, N / n, len(gorulen) / n_i


def knn_matrisi(X):
    pop = np.asarray(X.sum(axis=0)).ravel()
    norm = np.sqrt(pop); norm[norm == 0] = 1.0
    Xn = X.multiply(1.0 / norm).tocsr().astype(np.float32)
    Xc = Xn.tocsc()
    n_i = X.shape[1]
    D, I, Pt = [], [], [0]
    for j in range(n_i):
        col = np.asarray((Xc[:, j].T @ Xn).todense()).ravel()
        col[j] = 0.0
        nb = np.argpartition(-col, TOPN)[:TOPN] if col.size > TOPN else np.arange(col.size)
        nb = nb[col[nb] > 0]
        D.append(col[nb].astype(np.float32)); I.append(nb); Pt.append(Pt[-1] + nb.size)
    S = csr_matrix((np.concatenate(D), np.concatenate(I), np.array(Pt)), shape=(n_i, n_i))
    return (X @ S).tocsr()


def protokol(ad, tr, te, kisit=None):
    tr, te, X, uid, iid, truth, eval_users = hazirla(tr, te, kisit)
    n_i = X.shape[1]
    print(f"\n[{ad}]  eğitim {len(tr):,} · öğe {n_i:,} · "
          f"değerlendirilen kullanıcı {len(truth):,} · test etkileşimi {len(te):,}")

    pop = np.asarray(X.sum(axis=0)).ravel()
    rastgele = RNG.random(n_i)
    KNN = knn_matrisi(X)

    def knn_skor(r):
        s = np.zeros(n_i, np.float32)
        seg = slice(KNN.indptr[r], KNN.indptr[r + 1])
        s[KNN.indices[seg]] = KNN.data[seg]
        return s

    cikti = {}
    cikti["Rastgele"] = degerlendir(lambda r: rastgele, X, truth, n_i, "Rastgele")
    cikti["Popülerlik"] = degerlendir(lambda r: pop, X, truth, n_i, "Popülerlik")
    cikti["Öğe-öğe kNN"] = degerlendir(knn_skor, X, truth, n_i, "Öğe-öğe kNN")
    bilgi = dict(egitim=len(tr), oge=n_i, kullanici=len(truth), test=len(te))
    return cikti, bilgi


# ---------------------------------------------------------------- A: zamana göre
trA = havuz[havuz.d < CUT].copy()
teA = havuz[havuz.d >= CUT].copy()
oranA = len(trA) / len(havuz)
print(f"\nzaman bölmesi eğitim oranı: {oranA:.4f}")
A, bilgiA = protokol("A · zamana göre", trA, teA)
A_users = np.intersect1d(teA.u.unique(), trA.u.unique())

# ---------------------------------------------------------------- B: rastgele
perm = RNG.permutation(len(havuz))
kes = int(round(oranA * len(havuz)))
trB = havuz.iloc[perm[:kes]].copy()
teB = havuz.iloc[perm[kes:]].copy()
B, bilgiB = protokol("B · rastgele", trB, teB)
Bk, bilgiBk = protokol("B' · rastgele, A'nın kullanıcıları", trB, teB, kisit=A_users)

# ---------------------------------------------------------------- tavan: ulaşılamaz isabet
cnt = trA.i.value_counts()
katalog = set(cnt[cnt >= MIN_ITEM].index)
disarida = (~teA.i.isin(katalog)).sum()
yeni_film = teA.loc[~teA.i.isin(set(trA.i.unique())), "i"].nunique()
print(f"\n2020 testinde {len(teA):,} etkileşim var.")
print(f"  eğitim kataloğunda olmayan filmlere giden: {disarida:,} "
      f"(%{disarida/len(teA)*100:.1f}) — hiçbir model bunları isabet edemez")
print(f"  2020'de ilk kez görünen film sayısı: {yeni_film:,}")

# ---------------------------------------------------------------- dosyaya yaz
satirlar = []
for pro, sonuc, bilgi in [("A · zamana göre", A, bilgiA),
                          ("B · rastgele", B, bilgiB),
                          ("B' · rastgele, A kullanıcıları", Bk, bilgiBk)]:
    for model, (p, r, n, kap) in sonuc.items():
        satirlar.append(dict(protokol=pro, model=model, P10=round(p, 4), R10=round(r, 4),
                             NDCG10=round(n, 4), kapsam=round(kap, 4),
                             egitim_etkilesim=bilgi["egitim"], oge=bilgi["oge"],
                             degerlendirilen_kullanici=bilgi["kullanici"],
                             test_etkilesim=bilgi["test"]))
pd.DataFrame(satirlar).to_csv("sonuclar_bolme.csv", index=False)

with open("tavan_notu.txt", "w", encoding="utf-8") as f:
    f.write(f"2020 test etkilesimi: {len(teA)}\n")
    f.write(f"egitim katalogunda olmayan ogelere giden: {disarida} "
            f"({disarida/len(teA)*100:.2f}%)\n")
    f.write(f"2020'de ilk kez gorunen film: {yeni_film}\n")
    f.write(f"zaman bolmesi egitim orani: {oranA:.4f}\n")

print("\n-> sonuclar_bolme.csv ve tavan_notu.txt yazıldı")
