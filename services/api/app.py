import os, psycopg2, psycopg2.extras
from flask import Flask, jsonify, request

app = Flask(__name__)

def get_conn():
    return psycopg2.connect(
        host     = os.getenv('POSTGRES_HOST', 'postgres'),
        port     = int(os.getenv('POSTGRES_PORT', 5432)),
        dbname   = os.getenv('POSTGRES_DB',   'inventaire'),
        user     = os.getenv('POSTGRES_USER',  'admin'),
        password = os.getenv('POSTGRES_PASSWORD', ''),
        cursor_factory=psycopg2.extras.RealDictCursor
    )

@app.route('/health')
def health():
    try:
        conn = get_conn(); conn.close()
        return jsonify({'statut': 'ok', 'db': 'connectee'})
    except Exception as e:
        return jsonify({'statut': 'erreur', 'detail': str(e)}), 503

@app.route('/articles')
def liste():
    conn = get_conn(); cur = conn.cursor()
    cur.execute(
        'SELECT a.id, a.reference, a.nom, a.quantite, a.prix_unitaire,'
        ' c.nom AS categorie FROM articles a'
        ' LEFT JOIN categories c ON a.categorie_id = c.id'
        ' WHERE a.actif = TRUE ORDER BY a.nom'
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return jsonify({'articles': rows, 'total': len(rows)})

@app.route('/articles/<int:aid>')
def detail(aid):
    conn = get_conn(); cur = conn.cursor()
    cur.execute('SELECT * FROM articles WHERE id=%s AND actif=TRUE', (aid,))
    row = cur.fetchone(); conn.close()
    if not row:
        return jsonify({'erreur': 'introuvable'}), 404
    return jsonify(dict(row))

@app.route('/articles', methods=['POST'])
def creer():
    d = request.get_json()
    if not d or not d.get('reference') or not d.get('nom'):
        return jsonify({'erreur': 'reference et nom requis'}), 400
    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute(
            'INSERT INTO articles(reference, nom, description, quantite,'
            ' prix_unitaire, categorie_id) VALUES(%s,%s,%s,%s,%s,%s) RETURNING id',
            (d['reference'], d['nom'], d.get('description'),
             d.get('quantite', 0), d.get('prix_unitaire', 0), d.get('categorie_id'))
        )
        nid = cur.fetchone()['id']; conn.commit(); conn.close()
        return jsonify({'id': nid, 'message': 'cree'}), 201
    except psycopg2.IntegrityError:
        conn.rollback(); conn.close()
        return jsonify({'erreur': 'reference en double'}), 409

@app.route('/articles/<int:aid>', methods=['PATCH'])
def modifier(aid):
    d = request.get_json()
    champs = {k: v for k, v in d.items()
              if k in ('nom', 'description', 'quantite', 'prix_unitaire', 'actif')}
    if not champs:
        return jsonify({'erreur': 'aucun champ valide'}), 400
    sets = ', '.join(f'{k}=%s' for k in champs)
    conn = get_conn(); cur = conn.cursor()
    cur.execute(f'UPDATE articles SET {sets} WHERE id=%s RETURNING id',
                list(champs.values()) + [aid])
    ok = cur.fetchone(); conn.commit(); conn.close()
    if not ok:
        return jsonify({'erreur': 'introuvable'}), 404
    return jsonify({'message': 'mis a jour', 'id': aid})

@app.route('/articles/<int:aid>', methods=['DELETE'])
def supprimer(aid):
    conn = get_conn(); cur = conn.cursor()
    cur.execute('UPDATE articles SET actif=FALSE WHERE id=%s RETURNING id', (aid,))
    ok = cur.fetchone(); conn.commit(); conn.close()
    if not ok:
        return jsonify({'erreur': 'introuvable'}), 404
    return jsonify({'message': 'supprime', 'id': aid})

@app.route('/stats')
def stats():
    conn = get_conn(); cur = conn.cursor()
    cur.execute(
        'SELECT COUNT(*) nb, SUM(quantite) stock,'
        ' ROUND(SUM(quantite*prix_unitaire)::numeric, 2) valeur'
        ' FROM articles WHERE actif=TRUE'
    )
    return jsonify(dict(cur.fetchone()))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('API_PORT', 5000)))
