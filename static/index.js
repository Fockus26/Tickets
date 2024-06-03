function updateLink() {
    var select = document.getElementById('ticket_source');
    var selectedOption = select.options[select.selectedIndex].value;
    var link = document.getElementById('add_tickets_link');
    link.href = "/create_ticket/" + selectedOption;
}

function addSection() {
    const container = document.getElementById('section_container');
    const sectionCount = container.querySelectorAll('.section').length; // Obtener el número actual de secciones

    const section = document.createElement('div');
    section.classList.add('section');
    section.style.marginTop = '20px'; // Añadir margen superior a la sección

    const ticketId = sectionCount + 1; // Usar el número de secciones + 1 como el ID del ticket

    section.innerHTML = `
        <h3>Sección ${ticketId}</h3>
        <input type="hidden" name="ticket_id[]" value="${ticketId}">
        <button type="button" class="toggle-button" onclick="toggleContent('section-${ticketId}')"><i class="fa-solid fa-chevron-down"></i></button>
        <button type="button" class="delete-btn" onclick="removeSection(this)"><i class="fa-solid fa-x"></i></button>
        <div id="section-${ticketId}" class="toggle-content" style="display: none; padding: 10px;"> <!-- Agregar padding al contenido -->
            <label>Nombre de la Sección:</label>
            <input class="group" style="margin-bottom: 10px;" type="text" name="section_name[]" required><br>

            <div class="separate">
                <label>Tipo de Ticket</label>
                <select name="ticket_type[]">
                    <option value="Normal">Boleto Normal</option>
                    <option value="Preventa">Preventa</option>
                    <option value="Citibanamex">Citibanamex</option>
                    <option value="Fans">Fans</option>
                </select><br>
            </dim>

            <div class="ticket-options">
                <input class="group" type="number" name="num_tickets[]" placeholder="Número de Tickets" oninput="clearButtonSelection(this)" required>
                <input type="hidden" name="ticket_limit[]" value="">
            </div><br>

            <div style="display:flex; align-items: center">
                <label style="margin: 0px;">Todos los tickets disponibles:</label>
                <input style="margin-right: 20px;" type="checkbox" name="is_all_tickets_available[]">

                <label style="margin: 0px;" for="is_presale">Preventa:</label>
                <input type="checkbox" id="is_presale" name="is_presale[]"><br><br>
            </div>
            <input type="hidden" name="is_purchase[]" value="false">
        </div>
    `;

    container.appendChild(section);
}






function removeSection(button) {
    button.parentElement.remove();
}

function selectMaxTickets(button) {
    const input = button.nextElementSibling.nextElementSibling;
    const hiddenInput = button.nextElementSibling.nextElementSibling.nextElementSibling;
    if (button.classList.contains('selected')) {
        button.classList.remove('selected');
        input.disabled = false;
        hiddenInput.value = '';
    } else {
        clearButtonSelection(button);
        button.classList.add('selected');
        input.value = '';
        input.disabled = true;
        hiddenInput.value = 'max';
    }
}

function selectMinTickets(button) {
    const input = button.nextElementSibling;
    const hiddenInput = button.nextElementSibling.nextElementSibling;
    if (button.classList.contains('selected')) {
        button.classList.remove('selected');
        input.disabled = false;
        hiddenInput.value = '';
    } else {
        clearButtonSelection(button);
        button.classList.add('selected');
        input.value = '';
        input.disabled = true;
        hiddenInput.value = 'min';
    }
}

function clearButtonSelection(element) {
    const buttons = element.parentElement.querySelectorAll('button');
    buttons.forEach(button => button.classList.remove('selected'));
    element.parentElement.querySelector('input[type="number"]').disabled = false;
    element.parentElement.querySelector('input[type="hidden"]').value = '';
}

function toggleContent(sectionId) {
    const content = document.getElementById(sectionId);
    content.style.display = content.style.display === 'none' ? 'block' : 'none';
    const icon = content.previousElementSibling.querySelector('i');
    icon.classList.toggle('fa-chevron-down');
    icon.classList.toggle('fa-chevron-up');
}