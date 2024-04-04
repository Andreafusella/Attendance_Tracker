from flask import Flask, render_template, url_for, flash, request, redirect, session
from forms import LoginForm, CreaUsersForm, EliminaUserForm, ModificaUserForm, RicCorsoForm, ModificaLezioneDocenteForm
from forms import CreaCorsoForm, ModificaCorso, CreaLezioneForm, ModificaLezioneForm, CreaLezioneDocenteForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, ForeignKey, not_, func, extract
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.exc import IntegrityError
from datetime import datetime, date, timedelta

app  = Flask(__name__ , static_folder='templates')

app.config['SECRET_KEY'] = 'hardsecretkey'

#SqlAlchemy Database Configuration With Mysql
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:Arianna05.@localhost:3306/brief'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#MODELLI VARI
#UTENTE
class Utente(db.Model):
    __tablename__ = 'Utente'
    id_utente = db.Column(db.Integer, primary_key = True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=False)
    cognome = db.Column(db.String(200), nullable=False)
    tipo = db.Column(db.String(200), nullable=False)
    avatar = db.Column(db.Integer, nullable=False)

    def __init__(self, nome, cognome, tipo, avatar):
        self.nome = nome
        self.cognome = cognome
        self.tipo = tipo
        self.avatar = avatar

class Credenziali(db.Model):
    __tablename__ = 'Credenziali'
    id_utente = db.Column(db.Integer, ForeignKey('Utente.id_utente'), primary_key=True)
    email = db.Column(db.String(100), unique = True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

    def __init__(self, id_utente, email, password):
        self.id_utente = id_utente
        self.email = email
        self.password = password

class Iscritto(db.Model):
    __tablename__ = 'Iscritto'
    id = db.Column(db.Integer, primary_key=True)
    id_utente = db.Column(db.Integer, db.ForeignKey('Utente.id_utente'), nullable=False)
    id_corso = db.Column(db.Integer, db.ForeignKey('Corso.id_corso'), nullable=False)

    def __init__(self, id_utente, id_corso):
        self.id_utente = id_utente
        self.id_corso = id_corso

class Corso(db.Model):
    __tablename__ = 'Corso'
    id_corso = db.Column(db.Integer, primary_key = True, autoincrement=True)
    nome = db.Column(db.String(100), unique = True, nullable = False)
    durata = db.Column(db.Integer, nullable = False)

    def __init__(self, nome, durata):
        self.nome = nome
        self.durata = durata

class Lezione(db.Model):
    __tablename__ = 'Lezione'
    id_lezione = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_corso = db.Column(db.Integer, db.ForeignKey('Corso.id_corso'),nullable=False)
    argomento = db.Column(db.String(255), nullable=False)
    professore = db.Column(db.String(50), nullable=False)
    data = db.Column(db.Date, nullable=False)

    def __init__(self, id_corso, argomento, data, professore):
        self.id_corso = id_corso
        self.argomento = argomento
        self.professore = professore
        self.data = data   

class Registrazione(db.Model):
    __tablename__ = 'Registrazione'
    id_utente = db.Column(db.Integer, db.ForeignKey('Utente.id_utente'), primary_key=True)
    id_lezione = db.Column(db.Integer, db.ForeignKey('Lezione.id_lezione'), primary_key=True)
    data = db.Column(db.Date, nullable=False)
    presenza = db.Column(db.String(1), default='F')


    def __init__(self, id_utente, id_lezione, data, presenza):
        self.id_utente = id_utente
        self.id_lezione = id_lezione
        self.data = data
        self.presenza = presenza


#LOGIN
@app.route('/login', methods = ['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        session.clear()
        credential = Credenziali.query.filter_by(email = request.form['email'], password = request.form['password']).first()
        if credential:
            flag = False
            user = Utente.query.get(credential.id_utente)
            session['nome'] = user.nome
            session['cognome'] = user.cognome
            global tipo_definitivo
            global nome_definitivo
            global cognome_definitivo
            id_definitivo = user.id_utente
            tipo_definitivo = user.tipo
            nome_definitivo = user.nome
            cognome_definitivo = user.cognome
            avatar_definitivo = user.avatar
            session['id_definitivo'] = id_definitivo
            session['tipo_definitivo'] = tipo_definitivo
            session['nome_definitivo'] = nome_definitivo
            session['avatar_definitivo'] = avatar_definitivo
            session['cognome_definitivo'] = cognome_definitivo
            return redirect(url_for('dashboard'))
        else:
            error_message = 'Credenziali non valide'
            flag = True
            return render_template('login.html', form = form, error_message = error_message, flag = flag)
    print("non va")
    return render_template('login.html', form = form)



#------- (USER CREA) -------#
#METODO CREAZIONE USER
@app.route('/crud_utente/newutente', methods = ['GET', 'POST'])
def new():
    form = CreaUsersForm()
    if form.validate_on_submit():
        user = Utente(
            nome = request.form['nome'],
            cognome = request.form['cognome'],
            tipo = request.form['tipo'],
            avatar = request.form['avatar']
        )
        try:
            db.session.add(user)
            db.session.commit()
            id_utente = user.id_utente
            credential = Credenziali(
                id_utente = id_utente, 
                email = request.form['email'],
                password = request.form['password']
            )
            db.session.add(credential)
            db.session.commit()
            session['conferme'] = "Aggiunta_utente"
            return redirect(url_for('conferme'))
        except IntegrityError:
            db.session.rollback()
            return render_template('crud_utente/newutente.html', form = form, error_message="ID già esistente")

    return render_template('crud_utente/newutente.html', form = form)





#------- (USER ELIMINA) -------#
# PAGINA DI RICHIESTA DI CONFERMA ELIMINAZIONE
@app.route("/crud_utente/conteliminautenti/<id>")
def conteliminautenti(id):
    utente = Utente.query.get(id)
    credenziali = Credenziali.query.get(id)
    session['id'] = id
    session['controllo'] = False
    return render_template('crud_utente/conteliminautenti.html', utente=utente, credenziali=credenziali)

# ELIMINA USER DAL DB
@app.route("/crud_utente/eliminadefinitiva/<id>")
def eliminadefinitiva(id):
    utente = Utente.query.get(id)
    if utente:
        try:
            Iscritto.query.filter(Iscritto.id_utente == id).delete()
            db.session.delete(utente)
            db.session.commit()
            session['conferme'] = 'Eliminazione_utente'
            return redirect(url_for('conferme'))
        except Exception as e:
            db.session.rollback()
            
            return render_template('/crud_utente/eliminadefinitiva.html', message=str(e))
    return render_template('dashboard.html')


#------- (USER AGGIORNA) -------#
#RICERCA UTENTE PER ID 
@app.route("/crud_utente/aggiornautente", methods=['GET', 'POST'])
def aggiornautente():
    form = EliminaUserForm() #stesso form di eliminauser, campo da rilevare 1 (id)
    
    if request.method == 'POST' and form.validate_on_submit():
        id_utente = form.id_utente.data 
        utente = Utente.query.filter_by(id_utente=id_utente).first()  
        if utente:
            tabcredenziali = Credenziali.query.get(utente.id_utente)
            tabutente = Utente.query.get(utente.id_utente)
            
            #tabutente
            session['id_utente'] = tabutente.id_utente
            session['nome'] = tabutente.nome
            session['cognome'] = tabutente.cognome
            session['tipo'] = tabutente.tipo
            #tabcredenziali
            session['controlloagg'] = False
            session['email'] = tabcredenziali.email
            session['password'] = tabcredenziali.password
            return redirect(url_for('aggiornadefinitiva'))

    return render_template('crud_utente/aggiornautente.html', form = form)

#AGGIORNA CAMPI UTENTE  
@app.route("/crud_utente/aggiornacampi/<id>", methods = ['GET','POST'])
def aggiornacampi(id):
    form = ModificaUserForm()
    if request.method == 'POST' and form.validate_on_submit():
        session['controlloagg'] = False
        utente = Utente.query.get(id)
        credenziali = Credenziali.query.get(id)
        if utente and credenziali:
            nome = request.form['nome']
            if nome:
                utente.nome = nome
            cognome = request.form['cognome']
            if cognome:
                utente.cognome = cognome
            email = request.form['email']
            if email:
                credenziali.email = email
            password = request.form['password']
            if password:
                credenziali.password = password
            tipo = request.form['tipo']
            if tipo:
                utente.tipo = tipo

            try:
                
                db.session.commit()
                session['conferme'] = 'Modifica_utente'
                return redirect(url_for('conferme'))
            except IntegrityError as e:
                db.session.rollback()
                
                return render_template('crud_utente/aggiornacampi.html', form=form, error_message="Email già esistente")

    return render_template('crud_utente/aggiornacampi.html', form = form)

#MODIFICA CORSI
@app.route("/crud_corsi/corsi_modifica/<id>", methods = ['GET','POST'])
def aggiorna_corsi(id):
    form = ModificaCorso()
    if request.method == 'POST' and form.validate_on_submit():
        session['controlloagg'] = False
        corso = Corso.query.get(id)
        if corso:
            durata = request.form['durata']
            nome = request.form['nome']
            if nome:
                corso.nome = nome
            if durata:
                corso.durata = durata
            try:
                db.session.commit()
                session['conferme'] = "Modifica_corso"
                return redirect(url_for('conferme'))
            except IntegrityError as e:
                pass
            #     db.session.rollback()
            #     if 'nome' in str(e.orig):
            #         return render_template('crud_corsi/corsi_modifica.html', form = form, error_message="Nome già esistente")
            #     elif 'id_utente' in str(e.orig):
            #         return render_template('crud_corsi/corsi_modifica.html', form = form, error_message="ID già esistente")
            #     elif 'nome' in str(e.orig) and 'id_utente' in str(e.orig):
            #         return render_template('crud_corsi/corsi_modifica.html', form = form, error_message="Entrambi già esistenti")
            #     return render_template('crud_corsi/corsi_modifica.html', form = form, error_message="ID già esistente")

    return render_template('crud_corsi/corsi_modifica.html', form = form)


#PAGINA DI REINDIRIZZAMENTO
@app.route("/crud_utente/aggiornadefinitiva")
def aggiornadefinitiva():
    return render_template('crud_utente/aggiornadefinitiva.html')





#------- (USER INFO) -------#
#METODO INFO USER
@app.route("/crud_utente/infoutenti", methods=['GET', 'POST'])
def infoutenti():
    form = EliminaUserForm() #stesso form di eliminauser, campo da rilevare 1 (id)
    
    if request.method == 'POST' and form.validate_on_submit():
        id_utente = form.id_utente.data 
        utente = Utente.query.filter_by(id_utente=id_utente).first()  
        if utente:
            tabcredenziali = Credenziali.query.get(utente.id_utente)
            tabutente = Utente.query.get(utente.id_utente)
            
            #tabutente
            session['id_utente'] = tabutente.id_utente
            session['nome'] = tabutente.nome
            session['cognome'] = tabutente.cognome
            session['tipo'] = tabutente.tipo
            #tabcredenziali
            session['controlloagg'] = False
            session['email'] = tabcredenziali.email
            session['password'] = tabcredenziali.password
            return redirect(url_for('infoutente_def'))
        
    return render_template('crud_utente/ric_infoutente.html', form = form)

#PAGINA INFO
@app.route("/crud_utente/infoutente_def/<id>")
def infoutente_def(id):
    utente = Utente.query.get(id)
    credenziali = Credenziali.query.get(id)
    return render_template('/crud_utente/infoutente_def.html', utente = utente,  credenziali = credenziali)

#METODO RITORNO INFORMAZIONI ORIGINARIE USER LOG
@app.route("/return_info_userlogged")
def info_user():
    session['tipo'] = session.get('real_tipo')
    session['nome'] = session.get('real_nome')
    session['cognome'] = session.get('real_cognome')
    utenti_list = Utente.query.order_by(desc(Utente.id_utente)).all() 
    return render_template('dashboard.html', utenti_list = utenti_list)




#------- (CORSO) -------#
@app.route("/corsi")
def corsi():
    if 'conferme' in session:
        session.pop('conferme')
    corso_list = Corso.query.order_by(desc(Corso.id_corso)).all()    
    return render_template('corsi.html', corso_list = corso_list)


#LEZIONI NEL CORSO
@app.route("/crud_corsi/info_corsi/<id>")
def info_corsi(id):
    print(id)
    lezioni_list = Lezione.query.filter_by(id_corso=id).all()
    corso = Corso.query.filter_by(id_corso=id).first()
    nome_corso = corso.nome
    session['idp'] = id
    session['nome_corso'] = corso.nome
    
    return render_template('crud_corsi/info_corsi.html', lezioni_list=lezioni_list, nome_corso = nome_corso)


#REMOVE CORSO
@app.route("/crud_corsi/corsi_delete/<id>")
def corsi_delete(id):

    lezioni_list = Lezione.query.filter_by(id_corso=id).all()
    corso = Corso.query.filter_by(id_corso=id).first()
    nome_corso = corso.nome
    session['idp'] = id
    session['nome_corso'] = corso.nome
    
    return render_template('crud_corsi/corsi_delete.html', lezioni_list=lezioni_list, nome_corso = nome_corso)

#REMOVE CORSO DB
@app.route("/crud_corsi/corsi_delete_db/<nome>")
def corsi_delete_db(nome):
    print (nome)
    corso = Corso.query.filter_by(nome=nome).first()

    
    if corso:
        db.session.delete(corso)
        db.session.commit()
        session['conferme'] = "Eliminazione_corso"
        return redirect(url_for('conferme'))
    corso_list = Corso.query.order_by(desc(Corso.id_corso)).all()  
    return render_template('corsi.html', corso_list = corso_list)


#AGGIUNGI CORSO
@app.route("/crud_corsi/corsi_agg", methods=['GET', 'POST'])
def corsi_agg():
    form = CreaCorsoForm()

    if form.validate_on_submit():
        corso = Corso(
            durata = request.form['durata'],
            nome = request.form['nome'],
        )
        try:
            db.session.add(corso)
            db.session.commit()
            session['conferme'] = 'Aggiunta_corso'
            
            return redirect(url_for('conferme'))
        except IntegrityError:
            db.session.rollback()
            return render_template('crud_corsi/corsi_agg.html', form = form, error_message="ID già esistente")

    return render_template('crud_corsi/corsi_agg.html', form= form)

#LISTA UTENTI NEL CORSO
@app.route("/crud_corsi/corsi_lista_utenti")
def corsi_lista_utenti():
    nome_corso = session.get('nome_corso')
    id_corso = session.get('idp')
    utenti_corso = Utente.query.join(Iscritto).filter_by(id_corso=id_corso).all()
    return render_template('crud_corsi/corsi_lista_utenti.html', utenti_corso=utenti_corso, nome_corso = nome_corso)

#AGGIUNGI UTENTI NEL CORSO DB
@app.route("/utenti_list_corsi_add/<id>", methods=['GET', 'POST'])
def utenti_list_corsi_add(id):
    if request.method == 'POST':
        utenti_selezionati = request.form.getlist('utente_selezionato')

        
        lezioni_corso = Lezione.query.filter_by(id_corso=id).all()
        if utenti_selezionati:
            for utente_id in utenti_selezionati:
                iscritto = Iscritto(id_utente=utente_id, id_corso=id)
                db.session.add(iscritto)

                for lezione in lezioni_corso:
                    registrazione = Registrazione(
                        id_utente=utente_id,
                        id_lezione=lezione.id_lezione,
                        data=lezione.data,
                        presenza='F'
                    )
                    db.session.add(registrazione)

            db.session.commit()
            session['conferme'] = 'Aggiunta_utente_corso'
            return redirect(url_for('conferme'))
        else:
            return redirect(url_for('utenti_list_corsi_add', id=id))


    utenti_list = Utente.query \
        .filter(Utente.tipo.in_(["Studente", "Docente"])) \
        .outerjoin(Iscritto, (Utente.id_utente == Iscritto.id_utente) & (Iscritto.id_corso == id)) \
        .filter(Iscritto.id_corso == None) \
        .order_by(desc(Utente.id_utente)) \
        .all()

    return render_template('crud_corsi/utenti_list_corsi_add.html', utenti_list = utenti_list)

#RIMOZIONE STUDENTI DAL CORSO
@app.route("/utenti_remove/<id>", methods=['GET', 'POST'])
def utenti_remove(id):
    if request.method == 'POST':
        utenti_selezionati = request.form.getlist('utente_selezionato')
        for utente_id in utenti_selezionati:
            iscritto = Iscritto.query.filter_by(id_utente=utente_id, id_corso=id).first()
            if iscritto:
                Registrazione.query.filter_by(id_utente=utente_id, id_lezione=iscritto.id_corso).delete()
                db.session.delete(iscritto)
        db.session.commit()
        session['conferme'] = 'Rimuovi_utente_corso'
        return redirect(url_for('conferme'))
    utenti_list = Utente.query.join(Iscritto).filter_by(id_corso=id).all()
    return render_template('crud_corsi/utenti_remove.html', utenti_list=utenti_list)


#------- (LEZIONI) -------#
@app.route("/lezioni")
def lezioni():
    lezioni_list = Lezione.query.order_by(desc(Lezione.id_lezione)).all()    
    return render_template('lezioni.html', lezioni_list = lezioni_list)

#CREA LEZIONE
@app.route("/crud_lezioni/lezioni_agg", methods=['GET','POST'])
def lezioni_agg():
    form = CreaLezioneForm()
    form.data.data = datetime.now().date()
    if form.validate_on_submit():
        lezione = Lezione(
            data = request.form['data'],
            argomento = request.form['argomento'],
            professore = request.form['professore'],
            id_corso = request.form['corso']
        )
        db.session.add(lezione)
        db.session.commit()
        db.session.refresh(lezione)
        id_lezione = lezione.id_lezione
        utenti = Utente.query.join(Iscritto).filter(Iscritto.id_corso == request.form['corso'], Utente.tipo == 'Studente').all()
        for student in utenti:
            registrazione = Registrazione(
                id_utente = student.id_utente,
                id_lezione = id_lezione,
                data = request.form['data'],
                presenza = 'F'
            )
            db.session.add(registrazione)
        db.session.commit()
        session['conferme'] = 'Aggiunta_lezione'
        return redirect(url_for('conferme'))
    return render_template('crud_lezioni/lezioni_agg.html', form = form)

#VIEW LEZIONE
@app.route("/crud_lezioni/lezioni_view/<id>", methods=['GET','POST'])
def lezioni_view(id):
    lezione = Lezione.query.get(id)
    corso = Corso.query.get(lezione.id_corso)
    return render_template('/crud_lezioni/lezioni_view.html', lezione = lezione, corso = corso)

#REMOVE LEZIONE
@app.route("/crud_lezioni/lezioni_remove/<id>", methods=['GET','POST'])
def lezioni_remove(id):
    lezione = Lezione.query.get(id)
    corso = Corso.query.get(lezione.id_corso)
    return render_template('/crud_lezioni/lezioni_remove.html', lezione = lezione, corso = corso)

#REMOVE LEZIONE DB
@app.route("/crud_lezioni/lezioni_remove_db/<lezione>", methods=['GET','POST'])
def lezioni_remove_db(lezione):
    lezione = Lezione.query.get(lezione)
    if lezione:
        db.session.delete(lezione)
        db.session.commit()
        session['conferme'] = 'Elimina_lezione'
        return redirect(url_for('conferme'))
    return render_template('/crud_lezioni/lezioni_remove.html')

#MODIFICA LEZIONE
@app.route("/crud_lezioni/lezioni_aggiorna/<id>", methods=['GET','POST'])
def lezioni_aggiorna(id):
    lezione = Lezione.query.get(id)

    form = ModificaLezioneForm(obj=lezione)
    form.corso.choices = [(corso.id_corso, corso.nome) for corso in Corso.query.all()]
    form.corso.data = lezione.id_corso
    
    docenti = Utente.query.filter_by(tipo='Docente').all()
    form.professore.choices = [(f"{docente.nome} {docente.cognome}", f"{docente.nome} {docente.cognome}") for docente in docenti]
    if request.method == 'POST' and form.validate_on_submit():
        lezione = Lezione.query.get(id)
        registrazione = Registrazione.query.filter_by(id_lezione = id).all()
        if lezione:
            argomento = request.form['argomento']
            if argomento:
                lezione.argomento = argomento
            data = request.form['data']
            if data:
                for registra in registrazione:
                    registra.data = data
                db.session.commit()
                lezione.data = data
            id_corso =request.form['corso']
            if id_corso:
                lezione.id_corso = id_corso
            professore = request.form['professore']
            if professore:
                lezione.professore = professore
            try:
                db.session.commit()
                session['conferme'] = 'Modifica_lezione'
                return redirect(url_for('conferme'))
            except IntegrityError as e:
                db.session.rollback()
                return render_template('/crud_lezioni/lezioni_aggiorna.html', form = form, error_message = "ID già esistente")
    
    return render_template('/crud_lezioni/lezioni_aggiorna.html', form = form)

#LEZIONI DOCENTI
@app.route("/lezioni_docenti")
def lezioni_docenti():
    id_docente = session.get('id_definitivo')
    nome = session.get('nome_definitivo')
    cognome = session.get('cognome_definitivo')
    nome_completo = nome + " " + cognome
    session['nome_completo'] = nome_completo
    print(type(nome_completo))
    print(nome_completo)
    lezioni_list = Lezione.query.filter_by(professore=nome_completo).order_by(desc(Lezione.data)).all()
    return render_template('/docenti/lezioni_docente.html', lezioni_list=lezioni_list)

#MODIFICA LEZIONI DOCENTE
@app.route("/docenti/lezioni_aggiorna_docente/<id>", methods=['GET','POST'])
def lezioni_aggiorna_docente(id):
    lezione = Lezione.query.get(id)

    form = ModificaLezioneDocenteForm(obj=lezione)
    form.corso.choices = [(corso.id_corso, corso.nome) for corso in Corso.query.all()]
    form.corso.data = lezione.id_corso
    
    if request.method == 'POST' and form.validate_on_submit():
        lezione = Lezione.query.get(id)
        registrazione = Registrazione.query.filter_by(id_lezione = id).all()
        if lezione:
            argomento = request.form['argomento']
        if argomento:
            lezione.argomento = argomento
        data = request.form['data']
        if data:
            for registra in registrazione:
                registra.data = data
            db.session.commit()
            lezione.data = data
        try:
            db.session.commit()
            session['conferme'] = 'Modifica_lezione_docente'
            return redirect(url_for('conferme'))
        except IntegrityError as e:
            db.session.rollback()
            return render_template('/docenti/lezioni_aggiorna.html', form = form, error_message = "ID già esistente")
    
    return render_template('/docenti/lezioni_aggiorna_docente.html', form = form)

#NEW LEZIONI DOCENTI
@app.route("/docenti/new_lezione_doc", methods=['GET','POST'])
def new_lezione_doc():
    nomeProf = session.get('nome_completo')
    form = CreaLezioneDocenteForm()
    form.data.data = datetime.now().date()
    if form.validate_on_submit():
        lezione = Lezione(
            data = request.form['data'],
            argomento = request.form['argomento'],
            id_corso = request.form['corso'],
            professore = nomeProf
        )
        db.session.add(lezione)
        db.session.commit()
        db.session.refresh(lezione)
        id_lezione = lezione.id_lezione
        utenti = Utente.query.join(Iscritto).filter(Iscritto.id_corso == request.form['corso'], Utente.tipo == 'Studente').all()
        for student in utenti:
            registrazione = Registrazione(
                id_utente = student.id_utente,
                id_lezione = id_lezione,
                data = request.form['data'],
                presenza = 'F'
            )
            db.session.add(registrazione)
        db.session.commit()
        session['conferme'] = 'Aggiunta_lezione_docente'
        return redirect(url_for('conferme'))
    return render_template('docenti/new_lezione_doc.html', form = form)

#DELETE LEZIONE DOCENTI
@app.route("/docenti/lezione_remove_docente/<id>", methods=['GET','POST'])
def lezione_remove_docente(id):
    lezione = Lezione.query.get(id)
    if lezione:
        
        corso = Corso.query.get(lezione.id_corso)
        
    return render_template('/docenti/lezione_remove_docente.html', lezione = lezione, corso = corso)

#DELETE LEZIONE DOCENTI DB
@app.route("/docenti/lezione_remove_docente_db/<lezione>", methods=['GET','POST'])
def lezione_remove_docente_db(lezione):
    lezione = Lezione.query.get(lezione)
    if lezione:
        db.session.delete(lezione)
        db.session.commit()
        session['conferme'] = 'Elimina_lezione_docente'
        return redirect(url_for('conferme'))
    return render_template('/docenti/lezione_remove_docente.html')

#------- (PRESENZE) -------#
#PRESENZA ADMIN
@app.route('/presenze/<id>', methods=['GET','POST'])
def presenze(id):
    if request.method == 'POST':
        utenti = request.form.getlist('studente_selezionato')
        for utente_id in utenti:
            registrazione = Registrazione.query.filter_by(id_utente = utente_id, id_lezione = id).first()
            if registrazione:
                if registrazione.presenza == 'T':
                    registrazione.presenza = 'F'
                elif registrazione.presenza == 'F':
                    registrazione.presenza = 'T'
                db.session.commit()
        session['conferme'] = 'Inserite_presenze'
        return redirect(url_for('conferme'))
    lezione = Lezione.query.filter_by(id_lezione = id).first()
    corso_lezione = Corso.query.join(Lezione).filter_by(id_lezione=id).first()
    print(corso_lezione.id_corso)
    utenti_corso = Utente.query.join(Iscritto).filter(Iscritto.id_corso == corso_lezione.id_corso, Utente.tipo == 'Studente').all()   
    return render_template('presenze.html', lista_studenti = utenti_corso, lezione = lezione)

#PRESENZA DOCENTE
@app.route('/docenti/presenze_docente/<id>', methods=['GET','POST'])
def presenze_docente(id):
    if request.method == 'POST':
        utenti = request.form.getlist('studente_selezionato')
        for utente_id in utenti:
            registrazione = Registrazione.query.filter_by(id_utente = utente_id, id_lezione = id).first()
            if registrazione:
                if registrazione.presenza == 'T':
                    registrazione.presenza = 'F'
                elif registrazione.presenza == 'F':
                    registrazione.presenza = 'T'
                db.session.commit()
        session['conferme'] = 'Inserite_presenze_docente'
        return redirect(url_for('conferme'))
    lezione = Lezione.query.filter_by(id_lezione = id).first()
    corso_lezione = Corso.query.join(Lezione).filter_by(id_lezione=id).first()
    print(corso_lezione.id_corso)
    utenti_corso = Utente.query.join(Iscritto).filter(Iscritto.id_corso == corso_lezione.id_corso, Utente.tipo == 'Studente').all()   
    return render_template('docenti/presenze_docente.html', lista_studenti = utenti_corso, lezione = lezione)

#PRESENZA STUDENTE
@app.route("/studenti/presenze_studente")
def presenze_studente():
    id_student = session.get('id_definitivo')
    lezioni_list = db.session.query(Lezione, Corso, Registrazione).\
        join(Registrazione).filter(Registrazione.id_utente == id_student).\
        join(Corso, Lezione.id_corso == Corso.id_corso).\
        order_by(Lezione.data.desc()).all()
    
    return render_template('/studenti/presenze_studente.html', lezioni_list = lezioni_list)

#LEZIONI STUDENTI
@app.route("/lezioni_studente")
def lezioni_studente():
    id_studente = session.get('id_definitivo')
    if 'data' in request.args:
        selected_date = request.args['data']
        lezioni_list = Lezione.query.filter_by(data=selected_date).order_by(desc(Lezione.id_lezione)).all()
        return render_template('studenti/lezioni_table.html', lezioni_list=lezioni_list)
    else:
        lezioni_list = Lezione.query\
        .join(Iscritto, Lezione.id_corso == Iscritto.id_corso)\
        .filter(Iscritto.id_utente == id_studente)\
        .order_by(desc(Lezione.id_lezione))\
        .all()
        return render_template('studenti/lezioni_studente.html', lezioni_list=lezioni_list)

#LEZIONI STUDENTI RICERCA
@app.route("/lezioni_studente_ricerca/<data>")
def lezioni_studente_ricerca(data):
    id_studente = session.get('id_definitivo')
    lezioni_list = Lezione.query\
        .join(Iscritto, Lezione.id_corso == Iscritto.id_corso)\
        .join(Registrazione, Lezione.id_lezione == Registrazione.id_lezione)\
        .filter(Iscritto.id_utente == id_studente)\
        .filter(Lezione.data == datetime.strptime(data, '%Y-%m-%d').date())\
        .all()
    return render_template('studenti/lezioni_studente_ricerca.html', lezioni_list=lezioni_list)
    
#CORSI STUDENTI
@app.route("/studenti/corsi_studente")
def corsi_studente():
    id_utente = session.get('id_definitivo')

    corsi_utente = Corso.query \
        .join(Iscritto, Iscritto.id_corso == Corso.id_corso) \
        .join(Utente, Utente.id_utente == Iscritto.id_utente) \
        .filter(Utente.id_utente == id_utente) \
        .all()
    
    return render_template('studenti/corsi_studente.html', corsi_utente = corsi_utente)

#CORSI STUDENTI INFO
@app.route("/studenti/corsi_studente_info/<nome_corso>")
def corsi_studente_info(nome_corso):
    id_utente = session.get('id_definitivo')
    corso = Corso.query.filter_by(nome = nome_corso).first()

    
    return render_template('studenti/corsi_stxudente_info.html')

#------- (VARIE ROUTE) -------#
@app.route("/")
def initialpage():
    session.clear()
    return render_template('initial.html')

@app.route("/homepage")
def homepage():
    return render_template('home.html')

#DA FINIRE
@app.route("/newpassword")
def newpassword():
    return render_template('newpassword.html')

@app.route('/utenti')
def utenti():
    utenti_list = Utente.query.order_by(desc(Utente.id_utente)).all()
    return render_template('utenti.html', utenti_list = utenti_list)

@app.route("/dashboard", methods = ['GET','POST'])
def dashboard():
    if request.method == 'POST':
        selected_month = int(request.form['selected_month'])
        
        numero_assenze_mese_selezionato = db.session.query(func.count()) \
            .filter(extract('month', Registrazione.data) == selected_month, Registrazione.presenza == 'T') \
            .scalar()

        return render_template('dashboard.html', numero_assenze_mese_selezionato=numero_assenze_mese_selezionato)
    
    id_studente = session.get('id_definitivo')
    id_docente = session.get('id_definitivo')
    docente = Utente.query.filter_by(id_utente = id_docente).first()
    data_odierne = date.today()
    data_otto_giorni_fa = datetime.now() - timedelta(days=8)
    nomedoc = docente.nome
    cognomedoc = docente.cognome
    nomecompleto = nomedoc + " " + cognomedoc

    numero_lezioni_odierne = db.session.query(func.count()).filter(Lezione.professore == nomecompleto, Lezione.data == data_odierne).scalar()

    argomenti_lezioni_odierne = db.session.query(Lezione.argomento).filter(Lezione.professore == nomecompleto, Lezione.data == data_odierne).all()
    argomenti = [argomento[0] for argomento in argomenti_lezioni_odierne]

    argomenti_ultime_8_lezioni = db.session.query(Lezione.argomento) \
    .filter(Lezione.professore == nomecompleto, Lezione.data >= data_otto_giorni_fa) \
    .order_by(Lezione.data.desc()) \
    .limit(8) \
    .all()

    ultime_lezioni = db.session.query(Lezione.argomento)\
        .filter(Lezione.professore == docente.nome + ' ' + docente.cognome)\
        .order_by(Lezione.data.desc())\
        .limit(8)\
        .all()

    # Estrai gli argomenti dalla query
    argomenti_ultime_lezioni = [lezione[0] for lezione in ultime_lezioni]

    #conta numero presenza  
    presenze_studente = db.session.query(func.count()).filter(Registrazione.id_utente == id_studente, Registrazione.presenza == 'T').scalar()

    #conta numero assenze
    assenze_studente = db.session.query(func.count()).filter(Registrazione.id_utente == id_studente, Registrazione.presenza == 'F').scalar()
    somma = presenze_studente + assenze_studente  

    

    
    
    presenza_gennaio = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'T', 
                            extract('month', Registrazione.data) == 1)\
                    .scalar()
    presenza_febbraio = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'T', 
                            extract('month', Registrazione.data) == 2)\
                    .scalar()
    presenza_marzo = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'T', 
                            extract('month', Registrazione.data) == 3)\
                    .scalar()
    presenza_aprile = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'T', 
                            extract('month', Registrazione.data) == 4)\
                    .scalar()
    presenza_maggio = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'T', 
                            extract('month', Registrazione.data) == 5)\
                    .scalar()
    presenza_giugno = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'T', 
                            extract('month', Registrazione.data) == 6)\
                    .scalar()
    presenza_luglio = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'T', 
                            extract('month', Registrazione.data) == 7)\
                    .scalar()
    presenza_agosto = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'T', 
                            extract('month', Registrazione.data) == 8)\
                    .scalar()
    presenza_settembre = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'T', 
                            extract('month', Registrazione.data) == 9)\
                    .scalar()
    presenza_ottobre = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'T', 
                            extract('month', Registrazione.data) == 10)\
                    .scalar()
    presenza_novembre = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'T', 
                            extract('month', Registrazione.data) == 11)\
                    .scalar()
    presenza_dicembre = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'T', 
                            extract('month', Registrazione.data) == 12)\
                    .scalar()
    
    assenza_gennaio = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'F', 
                            extract('month', Registrazione.data) == 1)\
                    .scalar()
    assenza_febbraio = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'F', 
                            extract('month', Registrazione.data) == 2)\
                    .scalar()
    assenza_marzo = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'F', 
                            extract('month', Registrazione.data) == 3)\
                    .scalar()
    assenza_aprile = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'F', 
                            extract('month', Registrazione.data) == 4)\
                    .scalar()
    assenza_maggio = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'F', 
                            extract('month', Registrazione.data) == 5)\
                    .scalar()
    assenza_giugno = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'F', 
                            extract('month', Registrazione.data) == 6)\
                    .scalar()
    assenza_luglio = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'F', 
                            extract('month', Registrazione.data) == 7)\
                    .scalar()
    assenza_agosto = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'F', 
                            extract('month', Registrazione.data) == 8)\
                    .scalar()
    assenza_settembre = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'F', 
                            extract('month', Registrazione.data) == 9)\
                    .scalar()
    assenza_ottobre = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'F', 
                            extract('month', Registrazione.data) == 10)\
                    .scalar()
    assenza_novembre = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'F', 
                            extract('month', Registrazione.data) == 11)\
                    .scalar()
    assenza_dicembre = db.session.query(func.count())\
                    .filter(Registrazione.id_utente == id_studente, 
                            Registrazione.presenza == 'F', 
                            extract('month', Registrazione.data) == 12)\
                    .scalar()
    
    return render_template('dashboard.html', 
                           argomenti_ultime_lezioni = argomenti_ultime_lezioni, 
                           argomenti_ultime_8_lezioni = argomenti_ultime_8_lezioni, 
                           argomenti_lezioni_odierne = argomenti, 
                           numero_lezioni_odierne = numero_lezioni_odierne, 
                           presenze = presenze_studente, assenze = assenze_studente, 
                           somma = somma, presenza_gennaio = presenza_gennaio, 
                           presenza_febbraio = presenza_febbraio,
                           presenza_marzo = presenza_marzo, 
                           presenza_aprile = presenza_aprile, 
                           presenza_maggio = presenza_maggio,
                           presenza_giugno = presenza_giugno, 
                           presenza_luglio = presenza_luglio, 
                           presenza_agosto = presenza_agosto,
                           presenza_settembre = presenza_settembre, 
                           presenza_ottobre = presenza_ottobre,
                           presenza_novembre = presenza_novembre, 
                           presenza_dicembre = presenza_dicembre,
                           assenza_gennaio = assenza_gennaio, assenza_febbraio = assenza_febbraio,
                           assenza_marzo = assenza_marzo, assenza_aprile = assenza_aprile, assenza_maggio= assenza_maggio,
                           assenza_giugno = assenza_giugno, assenza_luglio = assenza_luglio, assenza_agosto= assenza_agosto,
                           assenza_settembre = assenza_settembre, assenza_ottobre = assenza_ottobre,
                           assenza_novembre = assenza_novembre, assenza_dicembre = assenza_dicembre)

@app.route("/conferme")
def conferme():
    conferme = session.get('conferme')
    return render_template('conferme.html', conferme = conferme)

@app.route("/error404")
def error404():
    return render_template('error404.html')


#ELIMINA DATI DALLA SESSIONE
@app.route("/logout")
def logout():
    session.clear()
    return render_template('home.html')

