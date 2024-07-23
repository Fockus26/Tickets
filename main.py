from flask import Flask, render_template, redirect, url_for, flash, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource, reqparse
import os
from dotenv import load_dotenv
import json
import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_KEY')

# INTERNAL API
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

    def put(self):
        args = self.reqparse.parse_args()
        api_key = args['api_key']
        ticket_id = args['id']
        section_id = args['id_section']

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

# DATABASE

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URL')
db = SQLAlchemy(app)

class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_name = db.Column(db.String(100), nullable=False)
    concert_name = db.Column(db.String(100), nullable=False)
    event_name = db.Column(db.String(100), nullable=False)
    event_day = db.Column(db.JSON(10), nullable=False)
    event_month = db.Column(db.String(5), nullable=False)
    event_time = db.Column(db.String(5), nullable=False)
    tickets_data = db.Column(db.Text, nullable=False)


with app.app_context():
    db.create_all()


# ROUTES

@app.route('/', methods=['GET', 'POST'])
def home():
    tickets_ingresados = []
    tickets_completados = []

    # Obtener todos los tickets
    all_tickets = Ticket.query.all()

    # Obtener el valor seleccionado del formulario si se envió
    selected_source = request.form.get('ticket_source')

    for ticket in all_tickets:
        sections = json.loads(ticket.tickets_data)
        if all(section["is_purchase"] for section in sections):
            tickets_completados.append(ticket)
        else:
            tickets_ingresados.append(ticket)

    # Filtrar los tickets según el page_name seleccionado si existe
    if selected_source:
        tickets_ingresados = [ticket for ticket in tickets_ingresados if ticket.page_name == selected_source]
        tickets_completados = [ticket for ticket in tickets_completados if ticket.page_name == selected_source]

    return render_template(
        "index.html",
        tickets_ingresados=tickets_ingresados,
        tickets_completados=tickets_completados
    )


@app.route('/create_ticket/<source>', methods=['GET', 'POST'])
def create_ticket(source):
    return render_template("add_ticket.html", source=source)


@app.route('/add_ticket/<source>', methods=['POST'])
def add_ticket(source):
    concert_name = request.form.get('concert_name')
    event_name = request.form.get('event_name')
    page_name = request.form.get('page_name')
    event_date_time = request.form.get('event_date_time')
    date_time_parts = event_date_time.split('T')
    date_parts = date_time_parts[0].split('-')
    year_part, month_part, day_part = date_parts[0], date_parts[1], date_parts[2]
    time_part = f"{date_time_parts[1]}"

    if source == "ticketmaster":
        # Diccionario para la traducción de meses
        month_translation = {
            'Jan': 'Ene', 'Feb': 'Feb', 'Mar': 'Mar', 'Apr': 'Abr', 'May': 'May', 'Jun': 'Jun',
            'Jul': 'Jul', 'Aug': 'Ago', 'Sep': 'Sep', 'Oct': 'Oct', 'Nov': 'Nov', 'Dec': 'Dic'
        }
    else:
        # Diccionario para la traducción de meses al español completo
        month_translation = {
            'Jan': 'Enero', 'Feb': 'Febrero', 'Mar': 'Marzo', 'Apr': 'Abril', 'May': 'Mayo', 'Jun': 'Junio',
            'Jul': 'Julio', 'Aug': 'Agosto', 'Sep': 'Septiembre', 'Oct': 'Octubre', 'Nov': 'Noviembre', 'Dec': 'Diciembre'
        }
        event_date_time2 = request.form.get('event_date_time2')
        date_time_parts2 = event_date_time2.split('T')
        date_parts2 = date_time_parts2[0].split('-')
        year_part2, month_part2, day_part2 = date_parts2[0], date_parts2[1], date_parts2[2]
        time_part2 = f"{date_time_parts2[1]}"

        formatted_date2 = f"{year_part2}-{month_part2}-{day_part2}"

        # Convertir la fecha a un objeto datetime
        date_obj = datetime.datetime.strptime(formatted_date2, '%Y-%m-%d')
        # Obtener el mes abreviado y traducirlo
        month_part2 = month_translation[date_obj.strftime('%b')]

        event_dates_time_tickets = request.form.getlist('event_date_time_tickets[]')

    # Formatear la fecha en el formato correcto
    formatted_date = f"{year_part}-{month_part}-{day_part}"

    # Convertir la fecha a un objeto datetime
    date_obj = datetime.datetime.strptime(formatted_date, '%Y-%m-%d')
    # Obtener el mes abreviado y traducirlo
    month_part = month_translation[date_obj.strftime('%b')]

    tickets_data = []

    print(day_part, day_part2)

    if day_part2 == day_part:
        day_part = [int(day_part)]
    else:
        day_part = [int(day_part), int(day_part2)]

    section_names = request.form.getlist('section_name[]')
    num_tickets = request.form.getlist('num_tickets[]')

    for i in range(len(section_names)):

        num_ticket_value = int(num_tickets[i]) if num_tickets[i] else None

        # Obtener el ID de la sección
        section_id = i + 1

        if source == "superboletos":
            event_date_time_ticket = event_dates_time_tickets[i]
            date_time_parts_ticket = event_date_time_ticket.split('T')
            date_parts2 = date_time_parts_ticket[0].split('-')
            day_part2 = date_parts2[2]
            time_part2 = f"{date_time_parts_ticket[1]}"

            # Crear los datos de la sección
            section_data = {
                "section_id": section_id,
                "section_name": section_names[i],
                "num_tickets": num_ticket_value,
                'ticket_day': day_part2,
                'ticket_month': month_part,
                'ticket_time': time_part2,
                "is_purchase": False
            }
        else:
            # Crear los datos de la sección
            section_data = {
                "section_id": section_id,
                "section_name": section_names[i],
                "num_tickets": num_ticket_value,
                "is_purchase": False
            }
        tickets_data.append(section_data)

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


@app.route('/edit_ticket/<int:ticket_id>', methods=['GET', 'POST'])
def edit_ticket(ticket_id):
    ticket = Ticket.query.get(ticket_id)
    if request.method == "POST":
        ticket.concert_name = request.form.get('concert_name')
        ticket.event_name = request.form.get('event_name')
        ticket.is_purchase = True if request.form.get('is_purchase') == 'on' else False

        sections_data = []
        section_names = request.form.getlist('section_name[]')
        num_tickets = request.form.getlist('num_tickets[]')
        is_purchase = request.form.getlist('section_is_purchase[]')

        for i in range(len(section_names)):
            num_ticket_value = None
            num_ticket_value = int(num_tickets[i]) if num_tickets[i] else None

            is_purchase_value = is_purchase[i] if i < len(is_purchase) else False

            section_data = {
                "section_name": section_names[i],
                "num_tickets": num_ticket_value,
                "is_purchase": is_purchase_value == 'on'
            }
            sections_data.append(section_data)

        ticket.tickets_data = json.dumps(sections_data)

        db.session.commit()
        flash("Ticket Actualizado")
        return redirect(url_for('home'))
    else:
        sections = json.loads(ticket.tickets_data)
        return render_template('edit_ticket.html', ticket=ticket, sections=sections)


@app.route('/delete_ticket/<int:ticket_id>', methods=['POST'])
def delete_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    db.session.delete(ticket)
    db.session.commit()
    flash('Ticket eliminado exitosamente.')
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
