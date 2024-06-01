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
            tickets = Ticket.query.filter_by(page_name=filter_value).all()
        else:
            tickets = Ticket.query.all()

        tickets_data = []
        for ticket in tickets:
            sections = json.loads(ticket.tickets_data)
            filtered_sections = [section for section in sections if not section.get("is_purchase", False)]
            if filtered_sections:
                ticket_info = {
                    'id': ticket.id,
                    'page_name': ticket.page_name,
                    'concert_name': ticket.concert_name,
                    'event_name': ticket.event_name,
                    'event_day': ticket.event_day,
                    'event_month': ticket.event_month,
                    'event_time': ticket.event_time,
                    'tickets_data': filtered_sections
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
            tickets = Ticket.query.filter_by(page_name=filter_value).all()
        else:
            tickets = Ticket.query.all()

        tickets_data = []
        for ticket in tickets:
            sections = json.loads(ticket.tickets_data)
            filtered_sections = [section for section in sections if section.get("is_purchase", False)]
            if filtered_sections:
                ticket_info = {
                    'id': ticket.id,
                    'page_name': ticket.page_name,
                    'concert_name': ticket.concert_name,
                    'event_name': ticket.event_name,
                    'event_day': ticket.event_day,
                    'event_month': ticket.event_month,
                    'event_time': ticket.event_time,
                    'tickets_data': filtered_sections
                }
                tickets_data.append(ticket_info)
        return {'tickets': tickets_data}


class UpdateTicket(Resource):
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('api_key', type=str, required=True, location='args')
        self.reqparse.add_argument('id', type=int, required=True, location='args')
        self.reqparse.add_argument('id_section', type=int, required=True, location='args')
        self.reqparse.add_argument('message', type=str, required=False, location='args')
        self.reqparse.add_argument('attempts', type=int, required=False, location='args')

    def put(self):
        args = self.reqparse.parse_args()
        api_key = args['api_key']
        ticket_id = args['id']
        section_id = args['id_section']
        message = args.get('message')
        attempts = args.get('attempts')

        if api_key != os.getenv('API_KEY'):
            return {'message': 'Unauthorized access'}, 401

        ticket = Ticket.query.get(ticket_id)
        if not ticket:
            return {'message': 'Ticket not found'}, 404

        # Buscar la sección por section_id en los datos del ticket
        tickets_data = json.loads(ticket.tickets_data)
        section_found = False
        for section in tickets_data:
            if section.get('section_id') == section_id:
                section['attempts'] = attempts
                section['message'] = message
                section_found = True
                break

        if not section_found:
            return {'message': 'Section not found in ticket'}, 404

        # Actualizar los datos del ticket
        ticket.tickets_data = json.dumps(tickets_data)

        db.session.commit()

        return {'message': 'Ticket updated successfully'}

api.add_resource(GetTickets, '/get_tickets')
api.add_resource(GetBuyTickets, '/get_buy_tickets')
api.add_resource(UpdateTicket, '/update_ticket')

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(100), nullable=False)
    concert_name = db.Column(db.String(100), nullable=False)
    event_name = db.Column(db.String(100), nullable=False)
    event_day = db.Column(db.String(10), nullable=False)
    event_month = db.Column(db.String(5), nullable=False)
    event_time = db.Column(db.String(5), nullable=False)
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
        tickets_ingresados = []
        tickets_completados = []

        all_tickets = Ticket.query.all()

        for ticket in all_tickets:
            sections = json.loads(ticket.tickets_data)
            if all(section["is_purchase"] for section in sections):
                tickets_completados.append(ticket)
            else:
                tickets_ingresados.append(ticket)

        return render_template(
            "index.html",
            tickets_ingresados=tickets_ingresados,
            tickets_completados=tickets_completados
        )
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
        page_name = request.form.get('page_name')

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
        is_purchases = request.form.getlist('is_purchase[]')

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
            is_purchase_value = is_purchases[i].lower() == 'true'

            # Obtener el ID de la sección
            section_id = i + 1

            # Crear los datos de la sección
            section_data = {
                "section_id": section_id,
                "section_name": section_names[i],
                "ticket_type": ticket_types[i],
                "num_tickets": num_ticket_value,
                "is_all_tickets_available": is_all_tickets_available_value == 'on',
                "is_presale": presales_value == 'on',
                'attempts': 0,
                'message': "Buscando Ticket",
                "is_purchase": is_purchase_value
            }
            sections_data.append(section_data)

        tickets_data = sections_data

        new_ticket = Ticket(
            concert_name=concert_name,
            event_name=event_name,
            event_day=day_part,
            event_month=month_part,
            event_time=time_part,
            page_name=page_name,
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
            ticket.is_all_tickets_available = True if request.form.get('is_all_tickets_available') == 'on' else False

            sections_data = []
            section_names = request.form.getlist('section_name[]')
            ticket_types = request.form.getlist('ticket_type[]')
            num_tickets = request.form.getlist('num_tickets[]')
            ticket_limits = request.form.getlist('ticket_limit[]')
            attempts = request.form.getlist('attempts[]')
            is_all_tickets_available = request.form.getlist('is_all_tickets_available[]')
            presales = request.form.getlist('is_presale[]')
            is_purchase = request.form.getlist('section_is_purchase[]')
            attempts = request.form.getlist('attempts[]')
            message = request.form.getlist('message[]')

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
                is_purchase_value = is_purchase[i] if i < len(is_purchase) else False

                attempt_value = attempts[i]
                message_value = message[i]

                section_data = {
                    "section_name": section_names[i],
                    "ticket_type": ticket_types[i],
                    "num_tickets": num_ticket_value,
                    "is_all_tickets_available": is_all_tickets_available_value == 'on',
                    "is_presale": presales_value == 'on',
                    "attempts": attempt_value,
                    "message": message_value,
                    "is_purchase": is_purchase_value == 'on'
                }
                sections_data.append(section_data)

            ticket.tickets_data = json.dumps(sections_data)

            db.session.commit()
            flash("Ticket Actualizado")
            return redirect(url_for('home'))
        else:
            sections = json.loads(ticket.tickets_data)
            return render_template('edit.html', ticket=ticket, sections=sections)
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
