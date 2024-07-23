function updateLink() {
    const source = document.getElementById('ticket_source').value;
    const addTicketLink = document.getElementById('add-ticket-link');
    addTicketLink.href = `/create_ticket/${source}`;
}

function addSection(source) {
    const container = document.getElementById('section_container');
    const sectionCount = container.querySelectorAll('.section').length; // Obtener el número actual de secciones

    const section = document.createElement('div');
    section.classList.add('section');
    section.style.marginTop = '20px'; // Añadir margen superior a la sección

    const ticketId = sectionCount + 1; // Usar el número de secciones + 1 como el ID del ticket

    if (source == "ticketmaster") {
        section.innerHTML = `
        <h3>Sección ${ticketId}</h3>
        <input type="hidden" name="ticket_id[]" value="${ticketId}">
        <button type="button" class="toggle-button" onclick="toggleContent('section-${ticketId}')"><i class="fa-solid fa-chevron-down"></i></button>
        <button type="button" class="delete-btn" onclick="removeSection(this)"><i class="fa-solid fa-x"></i></button>
        <div id="section-${ticketId}" class="toggle-content" style="display: none; padding: 10px;"> <!-- Agregar padding al contenido -->
            <label>Nombre de la Sección:</label>
            <input class="group" style="margin-bottom: 10px;" type="text" name="section_name[]" required><br>

            <div class="separate"></dim>

            <div class="ticket-options">
                <input class="group" type="number" name="num_tickets[]" placeholder="Número de Tickets" required>
                <input type="hidden" name="ticket_limit[]" value="">
            </div><br>

        </div>
    `;
    } else {
        section.innerHTML = `
        <h3>Sección ${ticketId}</h3>
        <input type="hidden" name="ticket_id[]" value="${ticketId}">
        <button type="button" class="toggle-button" onclick="toggleContent('section-${ticketId}')"><i class="fa-solid fa-chevron-down"></i></button>
        <button type="button" class="delete-btn" onclick="removeSection(this)"><i class="fa-solid fa-x"></i></button>
        <div id="section-${ticketId}" class="toggle-content" style="display: none; padding: 10px;"> <!-- Agregar padding al contenido -->
            <label>Nombre de la Sección:</label>
            <input class="group" style="margin-bottom: 10px;" type="text" name="section_name[]" required><br>

            <div class="separate"></dim>
            
            <div class="ticket-options">
                <input class="group" type="number" name="num_tickets[]" placeholder="Número de Tickets" required>
                <input type="hidden" name="ticket_limit[]" value="">
            </div><br>

            <div class="form-group">
                <label for="event_date_time2">Fecha y Hora del Evento:</label>
                <input type="datetime-local" id="event_date_time2" name="event_date_time_tickets[]" required>
            </div>

        </div>
    `;
    }

    container.appendChild(section);
}


function removeSection(button) {
    button.parentElement.remove();
}

function toggleContent(sectionId) {
    const content = document.getElementById(sectionId);
    content.style.display = content.style.display === 'none' ? 'block' : 'none';
    const icon = content.previousElementSibling.querySelector('i');
    icon.classList.toggle('fa-chevron-down');
    icon.classList.toggle('fa-chevron-up');
}