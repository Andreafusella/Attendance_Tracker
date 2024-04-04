from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, SelectField, IntegerField, DateField
from wtforms.validators import InputRequired

class LoginForm(FlaskForm):
    email = EmailField(validators=[InputRequired()])
    password = PasswordField(validators=[InputRequired()])

class CreaUsersForm(FlaskForm):
    nome = StringField(validators=[InputRequired()])
    cognome = StringField(validators=[InputRequired()])
    tipo = SelectField(choices=[('Admin','Admin'),('Docente','Docente'),('Studente','Studente')], validators=[InputRequired()])
    avatar = SelectField(choices=[(1,'Avatar 1'),
                                  (2,'Avatar 2'),
                                  (3,'Avatar 3'),
                                  (4,'Avatar 4'),
                                  (5,'Avatar 5')], validators=[InputRequired()])
    email = StringField(validators=[InputRequired()])
    password = StringField(validators=[InputRequired()])

class CreaCorsoForm(FlaskForm):
    nome = StringField(validators=[InputRequired()])
    durata = IntegerField(validators=[InputRequired()])

class ModificaUserForm(FlaskForm):
    nome = StringField()
    cognome = StringField()
    tipo = SelectField(choices=[('Admin','Admin'),('Docente','Docente'),('Studente','Studente')])
    email = EmailField()
    password = PasswordField()


class ModificaCorso(FlaskForm):
    nome = StringField()
    durata = IntegerField(validators=[InputRequired()])

class CreaLezioneForm(FlaskForm):
    argomento = StringField(validators=[InputRequired()])
    data = DateField(validators=[InputRequired()], format='%Y-%m-%d')
    corso = SelectField(validators=[InputRequired()], coerce=int)
    professore = SelectField(validators=[InputRequired()])

    def __init__(self, *args, **kwargs):
        super(CreaLezioneForm, self).__init__(*args, **kwargs)
        from app import Corso
        from app import Utente
        self.corso.choices = [(corso.id_corso, corso.nome) for corso in Corso.query.all()]

        docenti = Utente.query.filter_by(tipo='Docente').all()
        self.professore.choices = [(f"{docente.nome} {docente.cognome}", f"{docente.nome} {docente.cognome}") for docente in docenti]

class CreaLezioneDocenteForm(FlaskForm):
    argomento = StringField(validators=[InputRequired()])
    data = DateField(validators=[InputRequired()], format='%Y-%m-%d')
    corso = SelectField(validators=[InputRequired()], coerce=int)

    def __init__(self, *args, **kwargs):
        super(CreaLezioneDocenteForm, self).__init__(*args, **kwargs)
        from app import Corso
        self.corso.choices = [(corso.id_corso, corso.nome) for corso in Corso.query.all()]

class ModificaLezioneForm(FlaskForm):
    argomento = StringField()
    data = DateField(validators=[InputRequired()], format='%Y-%m-%d')
    corso = SelectField('Corso', coerce=int)
    professore = SelectField()

    def __init__(self, *args, **kwargs):
        corso_choices = kwargs.pop('corso_choices', [])
        professore_choices = kwargs.pop('professore_choices', [])
        super(ModificaLezioneForm, self).__init__(*args, **kwargs)
        self.corso.choices = corso_choices
        self.professore.choices = professore_choices

class ModificaLezioneDocenteForm(FlaskForm):
    argomento = StringField()
    data = DateField(validators=[InputRequired()], format='%Y-%m-%d')
    corso = SelectField('Corso', coerce=int)

    def __init__(self, *args, **kwargs):
        corso_choices = kwargs.pop('corso_choices', [])
        super(ModificaLezioneDocenteForm, self).__init__(*args, **kwargs)
        self.corso.choices = corso_choices

class RicCorsoForm(FlaskForm):
    id_corso = IntegerField(validators=[InputRequired()])

class EliminaUserForm(FlaskForm):
    id_utente = IntegerField(validators=[InputRequired()])