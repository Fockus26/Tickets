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
                'is_multiple_tickets': ticket.is_multiple_tickets,
                'is_all_available': ticket.is_all_available,
                'is_purchase': ticket.is_purchase,
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
                'is_multiple_tickets': ticket.is_multiple_tickets,
                'is_all_available': ticket.is_all_available,
                'is_purchase': ticket.is_purchase,
                'tickets_data': json.loads(ticket.tickets_data)
            }
            tickets_data.append(ticket_info)
        return {'tickets': tickets_data}


# Crear los recursos de la API
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
    is_multiple_tickets = db.Column(db.Boolean, nullable=False)
    is_all_available = db.Column(db.Boolean, nullable=False)
    is_purchase = db.Column(db.Boolean, nullable=False)
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
        tickets_ingresados = Ticket.query.filter_by(is_purchase=False).all()
        tickets_completados = Ticket.query.filter_by(is_purchase=True).all()
        return render_template("index.html", tickets_ingresados=tickets_ingresados, tickets_completados=tickets_completados)
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

@app.route('/add_ticket', methods=['GET', 'POST'])
def add_ticket():
    global user_authenticated
    if user_authenticated:
        concert_name = request.form.get('concert_name')
        event_name = request.form.get('event_name')
        event_date_time = request.form.get('event_date_time')
        is_purchase = request.form.get('is_purchase') == 'true'
        page_name = request.form.get('page_name')
        is_multiple_tickets = request.form.get('is_multiple_tickets') == 'on'
        is_all_available = request.form.get('is_all_available') == 'on'

        date_time_parts = event_date_time.split('T')
        date_parts = date_time_parts[0].split('-')
        year_part = date_parts[0]
        month_part = date_parts[1]
        day_part = date_parts[2]
        time_part = date_time_parts[1].split(':')[0]

        # Formatear la fecha en el formato correcto
        formatted_date = f"{year_part}-{month_part}-{day_part}"

        # Convertir la fecha a un objeto datetime
        date_obj = datetime.datetime.strptime(formatted_date, '%Y-%m-%d')
        # Obtener el mes abreviado
        month_part = date_obj.strftime('%b').upper()

        tickets_data = []

        types_selected = request.form.getlist('type_selected[]')
        polygon_names = request.form.getlist('polygon_name[]')
        num_tickets = request.form.getlist('num_tickets[]')
        row_numbers = request.form.getlist('row_number[]')
        seat_numbers = request.form.getlist('seat_number[]')

        for i in range(len(types_selected)):
            if types_selected[i] == 'seats':
                tickets_data.append(["seats", polygon_names[i], int(row_numbers[i]), int(seat_numbers[i])])

        # Process polygons next
        for i in range(len(types_selected)):
            if types_selected[i] == 'polygons':
                tickets_data.append(["polygons", polygon_names[i], int(num_tickets[i])])


        tickets_data_json = json.dumps(tickets_data, ensure_ascii=False)

        new_ticket = Ticket(
            page_name=page_name,
            concert_name=concert_name,
            event_name=event_name,
            event_day=day_part,
            event_month=month_part,
            event_time=time_part,
            is_multiple_tickets=is_multiple_tickets,
            is_all_available=is_all_available,
            is_purchase=is_purchase,
            tickets_data=tickets_data_json
        )
        db.session.add(new_ticket)
        db.session.commit()

        flash("Ticket Añadido")
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
            ticket.seat_type = request.form.get('seat_type')
            ticket.is_purchase = True if request.form.get('is_purchase') == 'on' else False
            ticket.is_multiple_tickets = True if request.form.get('is_multiple_tickets') == 'on' else False
            ticket.is_all_available = True if request.form.get('is_all_available') == 'on' else False

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
