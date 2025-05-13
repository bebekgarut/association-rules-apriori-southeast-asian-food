from flask import Flask, render_template, request
import pandas as pd
import pickle

app = Flask(__name__)

with open('./model/aturan_per_negara.pkl', 'rb') as f:
    aturan_per_negara = pickle.load(f)

df = pd.read_csv('./dataset/resep_masakan.csv')
df['bahan'] = df['bahan'].apply(lambda x: [b.strip() for b in x.split(',')])
print(df.columns)



@app.route('/', methods=['GET', 'POST'])
def index():
    hasil = None
    if request.method == 'POST':
        bahan_input = request.form.getlist('bahan')
        negara = request.form.get('negara')
        hasil = rekomendasi_dan_resep(bahan_input, negara)
    return render_template('index.jinja', hasil=hasil)

def rekomendasi_dan_resep(bahan_input, negara):
    if negara not in aturan_per_negara:
        return {"error": "Negara tidak ditemukan"}

    rules_df = aturan_per_negara[negara]
    bahan_input_set = set(bahan_input)
    cocok_rules = []

    for _, row in rules_df.iterrows():
        if row['antecedents'].issubset(bahan_input_set) and not row['consequents'].issubset(bahan_input_set):
            cocok_rules.append(row)

    if not cocok_rules:
        return {"error": "Tidak ada rekomendasi ditemukan"}

    top_rule = sorted(cocok_rules, key=lambda x: x['confidence'], reverse=True)[0]
    tambahan = list(top_rule['consequents'])
    rekomendasi_set = bahan_input_set.union(tambahan)

    df_negara = df[df['negara'] == negara].copy()
    df_negara['jumlah_cocok'] = df_negara['bahan'].apply(lambda x: len(rekomendasi_set.intersection(set(x))))
    df_cocok = df_negara[df_negara['jumlah_cocok'] > 0].sort_values(by='jumlah_cocok', ascending=False)

    if not df_cocok.empty:
        top_resep = df_cocok.iloc[0]
        return {
            "rekomendasi_bahan": tambahan,
            "nama_resep": top_resep['masakan'],
            "negara": top_resep['negara'],
            "bahan_resep": top_resep['bahan'],
            "gambar" : top_resep['gambar']
        }
    else:
        return {"error": "Tidak ada resep cocok ditemukan"}
  

@app.route('/nasi-goreng')
def nasi_goreng():
    return render_template('detail/nasi-goreng.html')

@app.route('/nasi-lemak')
def nasi_lemak():
    return render_template('detail/nasi-lemak.html')

@app.route('/gaeng-keow-wan')
def gaeng_keow_wan():
    return render_template('detail/gaeng-keow-wan.html')

@app.route('/pho')
def pho():
    return render_template('detail/pho.html')

@app.route('/ohn-no-khao-swe')
def ohn_no_khao_swe():
    return render_template('detail/ohn-no-khao-swe.html')

@app.route('/larb')
def larb():
    return render_template('detail/larb.html')

@app.route('/ambuyat')
def ambuyat():
    return render_template('detail/ambuyat.html')

@app.route('/lok-lak')
def lok_lak():
    return render_template('detail/lok-lak.html')

@app.route('/carna-assada')
def carna_assada():
    return render_template('detail/carna-assada.html')

@app.route('/adobo')
def adobo():
    return render_template('detail/adobo.html')

@app.route('/hainanese-chicken-rice')
def hainanese_chicken_rice():
    return render_template('detail/hainanese-chicken-rice.html')

if __name__ == '__main__':
    app.run(debug=True)
