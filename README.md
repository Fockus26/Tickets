# 🎫 Tickets – Web App

**English**  

A simple ticket management web application built with Python (Flask). This project was designed primarily as the frontend/API client for [BotTickets](https://github.com/fockus26/BotTickets), allowing users to create, edit, and delete tickets through a basic web interface.  

**Español**  

Una aplicación web sencilla de gestión de tickets construida con Python (Flask). Este proyecto fue diseñado principalmente como el cliente/API de [BotTickets](https://github.com/fockus26/BotTickets), permitiendo a los usuarios crear, editar y eliminar tickets a través de una interfaz básica.

---

## 🌍 Overview / Descripción

**English**  
Tickets is a lightweight web project with minimal UI, as its main purpose is to provide endpoints and a simple interface to interact with BotTickets. Users can manage tickets directly from the site, but the focus is on backend functionality rather than design.  

**Español**  
Tickets es un proyecto web ligero con una interfaz mínima, ya que su objetivo principal es proveer endpoints y una interfaz sencilla para interactuar con BotTickets. Los usuarios pueden gestionar tickets directamente desde la página, pero el enfoque está en la funcionalidad backend más que en el diseño.

---

## ✨ Features / Características

**English**  
- ➕ Add new tickets  
- ✏️ Edit existing tickets  
- ❌ Delete tickets  
- 📄 List and manage all tickets  
- 🔗 API integration with BotTickets  

**Español**  
- ➕ Crear nuevos tickets  
- ✏️ Editar tickets existentes  
- ❌ Eliminar tickets  
- 📄 Listar y administrar todos los tickets  
- 🔗 Integración como API para BotTickets  

---

## 🛠️ Tech Stack / Tecnologías  

- Backend: Flask (Python)  
- Frontend: HTML5, CSS3, JavaScript  
- Deployment: Vercel  

---

## 📂 Project Structure / Estructura del Proyecto  

```text
Tickets/
│── main.py
│── requirements.txt
│
├── static/
│ ├── assets/
│ ├── index.js
│ └── styles.css
│
├── templates/
│ ├── add_ticket.html
│ ├── edit_ticket.html
│ ├── index.html
│ └── update.html
│
└── README.md
```

---

## ⚙️ Installation & Setup / Instalación y Configuración

### Clone repo / Clonar repositorio
```bash
git clone https://github.com/fockus26/Tickets.git
cd Tickets
```

### Install dependencies / Instalar dependencias
```bash
pip install -r requirements.txt
```

### Run / Ejecutar
```bash
python main.py
```

App will run on: http://localhost:5000

---

## 📖 Case Study / Estudio de Caso

**English**

This project was created as the companion frontend/API for BotTickets. While not visually optimized, it fulfills its purpose of managing tickets and exposing endpoints that BotTickets consumes.

**Español**

Este proyecto fue creado como complemento frontend/API para BotTickets. Aunque no está optimizado visualmente, cumple con su propósito de gestionar tickets y exponer endpoints que BotTickets consume.

---

## 📈 Future Improvements / Mejoras Futuras

**English**

- 🎨 Improve UI with modern design (Bootstrap/Tailwind)

- 🗄️ Database integration for persistent storage

- 🔑 User authentication system

- 📱 Responsive redesign for mobile

**Español**

- 🎨 Mejorar la interfaz con diseño moderno (Bootstrap/Tailwind)

- 🗄️ Integración con base de datos para almacenamiento persistente

- 🔑 Sistema de autenticación de usuarios

- 📱 Rediseño responsive para móviles

---

## 📜 License / Licencia


**English**

This project is licensed under the MIT License.

**Español**

Este proyecto está licenciado bajo la Licencia MIT.
