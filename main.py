from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm
from flask_restful import Api, Resource, reqparse
import os
from dotenv import load_dotenv
import json
import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL')
db = SQLAlchemy(app)
api = Api(app)

class GetTickets(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('api_key', type=str, required=True, location='args')
        self.reqparse.add_argument('filter', type=str, required=False, location='args')

    def get(self):
        args = self.reqparse.parse_args()
        api_key = args['api_key']
        filter_value = args['filter']

        if api_key != os.getenv('API_KEY'):
            return {'message': 'Unauthorized access'}, 401

        if filter_value:
            tickets = Ticket.query.filter_by(page_name=filter_value, is_purchase=False).all()
        else:
            tickets = Ticket.query.filter_by(is_purchase=False).all()

        tickets_data = []
        for ticket in tickets:
            ticket_info = {
                'id': ticket.id,
                'page_name': ticket.page_name,
                'concert_name': ticket.concert_name,
                'event_name': ticket.event_name,
                'event_day': ticket.event_day,
                'event_month': ticket.event_month,
                'event_time': ticket.event_time,
                'is_multiple_section': ticket.is_multiple_section,
                'is_purchase': ticket.is_purchase,
                'attempts': ticket.attempts,
                'message': ticket.message,
                'tickets_data': json.loads(ticket.tickets_data)
            }
            tickets_data.append(ticket_info)
        return {'tickets': tickets_data}

class GetBuyTickets(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('api_key', type=str, required=True, location='args')
        self.reqparse.add_argument('filter', type=str, required=False, location='args')

    def get(self):
        args = self.reqparse.parse_args()
        api_key = args['api_key']
        filter_value = args['filter']

        if api_key != os.getenv('API_KEY'):
            return {'message': 'Unauthorized access'}, 401

        if filter_value:
            tickets = Ticket.query.filter_by(page_name=filter_value, is_purchase=True).all()
        else:
            tickets = Ticket.query.filter_by(is_purchase=True).all()

        tickets_data = []
        for ticket in tickets:
            ticket_info = {
                'id': ticket.id,
                'page_name': ticket.page_name,
                'concert_name': ticket.concert_name,
                'event_name': ticket.event_name,
                'event_day': ticket.event_day,
                'event_month': ticket.event_month,
                'event_time': ticket.event_time,
                'is_multiple_section': ticket.is_multiple_section,
                'is_purchase': ticket.is_purchase,
                'attempts': ticket.attempts,
                'message': ticket.message,
                'tickets_data': json.loads(ticket.tickets_data)
            }
            tickets_data.append(ticket_info)
        return {'tickets': tickets_data}

class UpdateTicket(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('api_key', type=str, required=True, location='args')
        self.reqparse.add_argument('id', type=int, required=True, location='args')
        self.reqparse.add_argument('message', type=str, required=False, location='args')
        self.reqparse.add_argument('attempts', type=int, required=False, location='args')

    def put(self):
        args = self.reqparse.parse_args()
        api_key = args['api_key']
        ticket_id = args['id']
        message = args.get('message')
        attempts = args.get('attempts')

        if api_key != os.getenv('API_KEY'):
            return {'message': 'Unauthorized access'}, 401

        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return {'message': 'Ticket not found'}, 404

        if message is not None:
            ticket.message = message
        if attempts is not None:
            ticket.attempts = attempts

        db.session.commit()

        return {'message': 'Ticket updated successfully'}

# Crear los recursos de la API
api.add_resource(UpdateTicket, '/update_ticket')
api.add_resource(GetTickets, '/get_tickets')
api.add_resource(GetBuyTickets, '/get_buy_tickets')

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(100), nullable=False)
    concert_name = db.Column(db.String(100), nullable=False)
    event_name = db.Column(db.String(100), nullable=False)
    event_day = db.Column(db.String(10), nullable=False)
    event_month = db.Column(db.String(5), nullable=False)
    event_time = db.Column(db.String(5), nullable=False)
    is_multiple_section = db.Column(db.Boolean, nullable=False)
    is_purchase = db.Column(db.Boolean, nullable=False)
    attempts = db.Column(db.Integer, nullable=False)
    message = db.Column(db.String(255), nullable=False)
    tickets_data = db.Column(db.Text, nullable=False)

# Para crear la base de datos, ejecuta:
with app.app_context():
    db.create_all()

user_email = os.getenv('USER_EMAIL')
user_password = os.getenv('USER_PASSWORD')
user_authenticated = False

@app.route('/', methods=['GET', 'POST'])
def home():
    global user_authenticated
    if user_authenticated:
        tickets_ingresados = Ticket.query.filter((Ticket.is_purchase == False) & (Ticket.attempts < 3)).all()
        tickets_completados = Ticket.query.filter_by(is_purchase=True).all()
        tickets_en_revision = Ticket.query.filter_by(attempts=3, is_purchase=False).all()
        return render_template("index.html", tickets_ingresados=tickets_ingresados, tickets_completados=tickets_completados, tickets_en_revision=tickets_en_revision)
    else:
        flash("No estás autorizado")
        return redirect(url_for("login"))


@app.route('/login', methods=['GET', 'POST'])
def login():
    global user_authenticated
    user_authenticated = False
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.lower()
        password = form.password.data

        if email != user_email:
            flash("Email Erroneo")
            return redirect(url_for("login"))
        elif password != user_password:
            flash("Contraseña Erronea")
            return redirect(url_for("login"))
        else:
            user_authenticated = True
            return redirect(url_for("home"))

    return render_template("login.html", form=form)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    global user_authenticated
    user_authenticated = False
    return redirect(url_for("login"))

@app.route('/create_ticket/<source>', methods=['GET', 'POST'])
def create_ticket(source):
    global user_authenticated
    if user_authenticated:
        return render_template("tickets.html", source=source)
    else:
        flash("No estás autorizado")
        return redirect(url_for("login"))

@app.route('/add_ticket', methods=['POST'])
def add_ticket():
    global user_authenticated
    if user_authenticated:
        concert_name = request.form.get('concert_name')
        event_name = request.form.get('event_name')
        event_date_time = request.form.get('event_date_time')
        is_purchase = request.form.get('is_purchase') == 'on'
        page_name = request.form.get('page_name')
        is_multiple_section = request.form.get('is_multiple_section') == 'on'

        date_time_parts = event_date_time.split('T')
        date_parts = date_time_parts[0].split('-')
        year_part = date_parts[0]
        month_part = date_parts[1]
        day_part = date_parts[2]
        time_part = f"{date_time_parts[1].split(':')[0]}:00"

        # Diccionario para la traducción de meses
        month_translation = {
            'Jan': 'Ene', 'Feb': 'Feb', 'Mar': 'Mar', 'Apr': 'Abr', 'May': 'May', 'Jun': 'Jun',
            'Jul': 'Jul', 'Aug': 'Ago', 'Sep': 'Sep', 'Oct': 'Oct', 'Nov': 'Nov', 'Dec': 'Dic'
        }

        # Formatear la fecha en el formato correcto
        formatted_date = f"{year_part}-{month_part}-{day_part}"

        # Convertir la fecha a un objeto datetime
        date_obj = datetime.datetime.strptime(formatted_date, '%Y-%m-%d')
        # Obtener el mes abreviado y traducirlo
        month_part = month_translation[date_obj.strftime('%b')]

        sections_data = []

        section_names = request.form.getlist('section_name[]')
        ticket_types = request.form.getlist('ticket_type[]')
        num_tickets = request.form.getlist('num_tickets[]')
        ticket_limits = request.form.getlist('ticket_limit[]')
        is_all_tickets_available = request.form.getlist('is_all_tickets_available[]')
        presales = request.form.getlist('is_presale[]')

        for i in range(len(section_names)):
            num_ticket_value = None
            if ticket_limits[i] == 'max':
                num_ticket_value = 'Max'
            elif ticket_limits[i] == 'min':
                num_ticket_value = 'Min'
            else:
                num_ticket_value = int(num_tickets[i]) if num_tickets[i] else None

            is_all_tickets_available_value = is_all_tickets_available[i] if i < len(is_all_tickets_available) else False
            presales_value = presales[i] if i < len(presales) else False

            section_data = {
                "section_name": section_names[i],
                "ticket_type": ticket_types[i],
                "num_tickets": num_ticket_value,
                "is_all_tickets_available": is_all_tickets_available_value == 'on',
                "is_presale": presales_value == 'on'
            }
            sections_data.append(section_data)

        tickets_data = sections_data

        new_ticket = Ticket(
            concert_name=concert_name,
            event_name=event_name,
            event_day=day_part,
            event_month=month_part,
            event_time=time_part,
            is_purchase=is_purchase,
            page_name=page_name,
            is_multiple_section=is_multiple_section,
            attempts=0,
            message="Buscando Ticket",
            tickets_data=json.dumps(tickets_data)
        )

        db.session.add(new_ticket)
        db.session.commit()
        return redirect(url_for('home'))
    else:
        flash("No estás autorizado")
        return redirect(url_for("login"))


@app.route('/edit_ticket/<int:ticket_id>', methods=['GET', 'POST'])
def edit_ticket(ticket_id):
    global user_authenticated
    if user_authenticated:
        ticket = Ticket.query.get(ticket_id)
        if request.method == "POST":
            ticket.concert_name = request.form.get('concert_name')
            ticket.event_name = request.form.get('event_name')
            ticket.event_date_time = request.form.get('event_date_time')
            ticket.is_purchase = True if request.form.get('is_purchase') == 'on' else False
            ticket.is_multiple_section = True if request.form.get('is_multiple_section') == 'on' else False
            ticket.is_all_tickets_available = True if request.form.get('is_all_tickets_available') == 'on' else False
            ticket.attempts = request.form.get('attempts')
            ticket.message = request.form.get('message')

            db.session.commit()
            flash("Ticket Actualizado")
            return redirect(url_for('home'))
        else:
            return render_template('edit.html', ticket=ticket)
    else:
        flash("No estás autorizado")
        return redirect(url_for("login"))


@app.route('/delete_ticket/<int:ticket_id>', methods=['POST'])
def delete_ticket(ticket_id):
    global user_authenticated
    if user_authenticated:
        ticket = Ticket.query.get_or_404(ticket_id)
        db.session.delete(ticket)
        db.session.commit()
        flash('Ticket eliminado exitosamente.')
        return redirect(url_for('home'))
    else:
        flash("No estás autorizado")
        return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
