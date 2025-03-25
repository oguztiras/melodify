# 🎵 Melodify - TuneMentor

**Melodify** is a Django-based web application that connects music instructors with apprentices. It features two user types, messaging, reviews, search functionality, and Google OAuth login. The project includes a Dockerized setup and GitHub Actions CI for automated testing.

## 🚀 Features

- **User Roles**:  
  - **Instructors**: Can create/edit profiles, receive and manage messages, and get reviewed by apprentices.  
  - **Apprentices**: Can browse instructors, leave and edit reviews, and send messages.

- **Authentication**: Email/password or Google OAuth2 login using `django-allauth`.

- **Client-Side Interactivity**:  
  - Search instructors by city and teaching level (client-side search with JavaScript).  
  - Review and message forms use JavaScript with Django API endpoints (no page refresh).  
  - Live average rating updates.

- **Messaging System**: Instructors can view and delete received messages.

- **Review System**: Apprentices can submit one review per instructor and update it anytime.

- **Testing & CI**:  
  - 15+ unit tests for views and models.  
  - GitHub Actions configured to run tests on every push.

- **Docker Support**: Fully Dockerized using PostgreSQL.

---

## 🗂️ Project Structure Highlights

```bash
melodify/ 
├── tunementor/        
│ ├── static/        
│ ├── templates/    
│ ├── models.py       
│ ├── views.py        
│ ├── tests.py         
│ ├── urls.py 
├── manage.py 
├── requirements.txt 
├── Dockerfile 
├── docker-compose.yml 
├── .gitignore 
├── db.sqlite3
├── LICENSE  
```

---

## ⚙️ Tech Stack

- **Backend**: Django 
- **Frontend**: HTML, CSS, JavaScript (Vanilla JS)  
- **Auth**: Simple E-mail, Django-allauth (Google OAuth2)  
- **Database**: SQLite (Local), PostgreSQL (Docker)  
- **Containerization**: Docker, Docker Compose  
- **CI/CD**: GitHub Actions  

---

## 📦 Getting Started

You can run this project locally (recommended for development) or with Docker (to simulate production environment).

### 1. Run Locally

> 💡 The `db.sqlite3` file is included so you can test the app with existing data.

#### 🛠️ Setup

```bash
# Clone the repository
git clone https://github.com/oguztiras/melodify.git
cd melodify

# Create virtual environment
python -m venv venv

# Activate it
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
SECRET_KEY=your-django-secret-key

# Run the app
python manage.py migrate
python manage.py runserver

# Then go to: http://127.0.0.1:8000

# Run Tests
python manage.py test
```

---

### 2. Run with Docker
📋 Prerequisites
- Docker Engine (Docker Desktop)

#### 🛠️ Setup+

```bash
# Create .env file
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=db
DB_PORT=5432

# Build and Run
docker-compose up --build
docker-compose exec web python manage.py migrate

# Then visit: http://localhost:8000
```

## 🤝 Contributing

Pull requests are welcome. Feel free to fork and adapt this project.

## 📄 License

This project is open-source and available under the MIT License.