from flask import Flask, request, jsonify, render_template_string, redirect, url_for
import json
import os
import hashlib

app = Flask(__name__)

USERS_FILE = "usuarios.json"
ADMIN_USER = "admin"
ADMIN_PASS = "Vhj02122024$"  # Troque pela sua senha de administrador

# ====== FUNÇÕES DE USUÁRIO ======
def carregar_usuarios():
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w") as f:
            json.dump({}, f)
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def salvar_usuarios(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# ====== ROTA DE AUTENTICAÇÃO DO BOT ======
@app.route("/api/auth", methods=["POST"])
def autenticar():
    dados = request.get_json()
    usuario = dados.get("usuario")
    senha = dados.get("senha")
    if not usuario or not senha:
        return jsonify({"status": "erro", "mensagem": "Campos obrigatórios"}), 400

    users = carregar_usuarios()
    if usuario in users and users[usuario] == hash_senha(senha):
        return jsonify({"status": "ok", "mensagem": "Acesso autorizado"})
    else:
        return jsonify({"status": "erro", "mensagem": "Usuário ou senha inválidos"}), 401

# ====== INTERFACE ADMIN ======
TEMPLATE_LOGIN = """
<h2>Login Admin</h2>
<form method="post">
  Usuário: <input name="usuario"><br><br>
  Senha: <input name="senha" type="password"><br><br>
  <button type="submit">Entrar</button>
</form>
"""

TEMPLATE_ADMIN = """
<h2>Painel Admin</h2>
<a href="/admin/logout">Sair</a>
<hr>
<h3>Usuários cadastrados</h3>
<ul>
{% for u in users %}
<li>{{u}} <a href="/admin/remover/{{u}}">[Remover]</a></li>
{% endfor %}
</ul>
<hr>
<h3>Adicionar Usuário</h3>
<form method="post" action="/admin/adicionar">
  Usuário: <input name="usuario"><br><br>
  Senha: <input name="senha" type="password"><br><br>
  <button type="submit">Adicionar</button>
</form>
"""

SESSOES_ATIVAS = set()

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        usuario = request.form.get("usuario")
        senha = request.form.get("senha")
        if usuario == ADMIN_USER and senha == ADMIN_PASS:
            SESSOES_ATIVAS.add(request.remote_addr)
            return redirect(url_for("painel_admin"))
        else:
            return "Login inválido"
    return render_template_string(TEMPLATE_LOGIN)

@app.route("/admin/painel")
def painel_admin():
    if request.remote_addr not in SESSOES_ATIVAS:
        return redirect(url_for("admin_login"))
    users = carregar_usuarios()
    return render_template_string(TEMPLATE_ADMIN, users=users.keys())

@app.route("/admin/adicionar", methods=["POST"])
def admin_adicionar():
    if request.remote_addr not in SESSOES_ATIVAS:
        return redirect(url_for("admin_login"))
    usuario = request.form.get("usuario")
    senha = request.form.get("senha")
    if usuario and senha:
        users = carregar_usuarios()
        users[usuario] = hash_senha(senha)
        salvar_usuarios(users)
    return redirect(url_for("painel_admin"))

@app.route("/admin/remover/<usuario>")
def admin_remover(usuario):
    if request.remote_addr not in SESSOES_ATIVAS:
        return redirect(url_for("admin_login"))
    users = carregar_usuarios()
    if usuario in users:
        del users[usuario]
        salvar_usuarios(users)
    return redirect(url_for("painel_admin"))

@app.route("/admin/logout")
def admin_logout():
    if request.remote_addr in SESSOES_ATIVAS:
        SESSOES_ATIVAS.remove(request.remote_addr)
    return redirect(url_for("admin_login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
