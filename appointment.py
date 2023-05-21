from flask import Flask, render_template, request, redirect, url_for, session 
from flask_session import Session
import pyodbc
import re

appointment = Flask(__name__)
appointment.config["SESSION_PERMANENT"] = False
appointment.config["SESSION_TYPE"] = "filesystem"
Session(appointment)
 

def connection():
    s = 'admat-31\developer_2014' #Your server name 
    d = 'PythonAPP' 
    u = 'smar' #Your login
    p = 'smarapd' #Your login password
    cstr = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER='+s+';DATABASE='+d+';UID='+u+';PWD='+ p
    conn = pyodbc.connect(cstr)
    return conn

def icadmin():
    conn = connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM dbo.Usuarios WHERE idUsuario = ? AND ic_admin = 1', session['idUsuario'])
    admin = cursor.fetchone()
    return admin

@appointment.route('/', methods=['GET', 'POST'])
@appointment.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''

    if request.method == 'POST' and 'email' in request.form and 'senha' in request.form:
        email = request.form['email']
        senha = request.form['senha']
        
        # Checa se a conta existe
        conn = connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dbo.Usuarios WHERE email = ? AND senha = ?', email, senha)
        
        account = cursor.fetchone()
        
        conn.close()

        # Se existir conta
        if account:
            # Cria sessão
            session['loggedin'] = True
            session['idUsuario'] = account[0]
            session['nome'] = account[1]
            # Redireciona para página de aulas
            return redirect(url_for('inicio'))
            
        
        else:
            msg = 'Usuário ou senha incorretos. Tente novamente.'

    
    return render_template('login.html', msg='')

@appointment.route('/registro', methods=['GET', 'POST'])
def registro():
    
    msg = ''
    # checa se formulário foi preenchido
    if request.method == 'POST' and 'nome' in request.form and 'email' in request.form and 'senha' in request.form:
        # Create variables for easy access
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        
        # checa no banco se já existe email cadastrado
        conn = connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM dbo.Usuarios WHERE email = ?', email)
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Conta já existe!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Email inválido!'
        elif not re.match(r'[A-Za-z0-9]+', nome):
            msg = 'Nome deve conter apenas letras ou números!'
        elif not nome or not senha or not email:
            msg = 'Preencha o formulário antes de começar!'
        else:
            # Se não existe, insere no banco e redireciona pro login
            cursor.execute('INSERT INTO dbo.Usuarios(nome, email, senha) VALUES ( ?, ?, ?)', nome, email, senha)
            conn.commit()
            conn.close()
            msg = 'Registrado com sucesso!'
            return render_template('login.html', msg=msg)
        
    elif request.method == 'POST':
        # Formulário vazio
        msg = 'Por favor, preencha os campos!'
    # 
    
    return render_template('registro.html', msg=msg)

@appointment.route('/logout')
def logout():
    # Remove sessão
   session.pop('loggedin', None)
   session.pop('idUsuario', None)
   session.pop('nome', None)
   
   return redirect(url_for('login'))

@appointment.route('/inicio')
def inicio():
    # Checa se está logado
    if 'loggedin' in session:
        return render_template('inicio.html', nome=session['nome'], idUsuario=session['idUsuario'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@appointment.route("/aulas")
def aulas():
    aulas = []
    conn = connection()
    cursor = conn.cursor()
    admin = icadmin()
    if admin:
        cursor.execute('SELECT a.idAula, a.nome, a.descricao,p.nome, a.data, a.horaInicio  FROM dbo.Aulas a JOIN dbo.Usuarios p ON p.idUsuario = a.idProfessor')
        #se for admin, chama o template com botões restritos
        template = "listaaulasadmin.html"
    else :
        cursor.execute('SELECT a.idAula, a.nome, a.descricao, p.nome, a.data, a.horaInicio  FROM dbo.Aulas a JOIN dbo.Usuarios p ON p.idUsuario = a.idProfessor JOIN dbo.AulaAlunos aa ON aa.idAula = a.idAula WHERE aa.idAluno = ?' , session['idUsuario'])
        #se não for admin, chama o template sem botões restritos
        template = "listaaulas.html"
    for row in cursor.fetchall():
        aulas.append({"idAula": row[0], "nome": row[1], "descricao": row[2], "professor": row[3], "data": row[4], "horaInicio": row[5]})
    conn.close()
    
    return render_template(template, aulas = aulas) 

@appointment.route("/novaaula", methods = ['GET','POST'])
def novaaula():
    if request.method == 'GET':
        return render_template("novaaula.html", aulas = {})
    if request.method == 'POST':
       #id = int(request.form["id"])
        nome = request.form["nome"]
        descricao = request.form["descricao"]
        idProfessor = request.form["idProfessor"]
        data = request.form["data"]
        horaInicio = request.form["horaInicio"]
        horaTermino = request.form["horaTermino"]
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO dbo.Aulas (nome, descricao, idProfessor, data, horaInicio, horaTermino) VALUES (?, ?, ?, ?, ?, ?)", nome, descricao,idProfessor, data, horaInicio, horaTermino)
        conn.commit()
        conn.close()
        return redirect(url_for('aulas'))


    
@appointment.route('/alteraraula/<int:id>',methods = ['GET','POST'])
def alteraraula(id):
    aula = []
    conn = connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT * FROM dbo.Aulas WHERE idAula = ?", id)
        for row in cursor.fetchall():
            aula.append({"idAula": row[0], "nome": row[1], "descricao": row[2], "data": row[3], "horaInicio": row[4], "horaTermino": row[5]})
        conn.close()
        return render_template("novaaula.html", aulas = aula[0])
    if request.method == 'POST':
        nome = str(request.form["nome"])
        descricao = str(request.form["descricao"])
        data = str(request.form["data"])
        horaInicio = str(request.form["horaInicio"])
        horaTermino = str(request.form["horaTermino"])
        cursor.execute("UPDATE dbo.Aulas SET nome = ?, descricao = ?, data = ?, horaInicio = ?, horaTermino = ? WHERE idAula = ?", nome, descricao, data, horaInicio, horaTermino, id)
        conn.commit()
        conn.close()
        return redirect('/aulas')


@appointment.route('/deletaraula/<int:id>',methods = ['GET','POST'])
def deletaraula(id):
    aula = []
    conn = connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT idaula, nome, descricao FROM dbo.Aulas WHERE idAula = ?", id)
        row = cursor.fetchone()
        aula.append({"idAula": row[0], "nome": row[1], "descricao": row[2]})
        conn.close()
        return render_template("deletaraula.html", aulas = aula[0])
     

@appointment.route('/deletaraula/confirmadeletaraula/<int:id>',methods = ['GET'])
def confirmadeletaraula(id):
    conn = connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute("DELETE FROM dbo.AulasUsuarios WHERE idAula = ? DELETE FROM dbo.Aulas WHERE idAula = ? ", id, id)
        conn.commit()
        conn.close()
    return redirect('/aulas')
    

@appointment.route('/listaalunos/<int:id>',methods = ['GET','POST'])
def listaalunos(id):
    aula = []
    alunos = []
    conn = connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT a.idAula, a.nome, a.descricao, p.nome FROM dbo.Aulas a JOIN dbo.Usuarios p ON p.idUsuario = a.idProfessor WHERE A.idAula = ?" ,  id)
        row = cursor.fetchone()
        aula.append({"idAula": row[0], "nome": row[1], "descricao": row[2], "professor": row[3]})
        conn.close()

        conn = connection()
        cursor = conn.cursor()
        cursor.execute("SELECT u.idUsuario, u.nome FROM dbo.Usuarios u JOIN dbo.AulaAlunos aa ON aa.IdAluno = u.idUsuario WHERE aa.idAula = ?" ,  id)
        rows = cursor.fetchall()
        for row in rows:
            alunos.append({"idUsuario": row[0], "nome": row[1]})
        conn.close()
        
        return render_template("listaalunos.html", aulas = aula[0], alunos = alunos)
    



@appointment.route('/perfil')
def perfil():
     return render_template("perfil.html")

@appointment.route('/sobre')
def sobre():
     return render_template("sobre.html")


if(__name__ == "__main__"):
    appointment.run()