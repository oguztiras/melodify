# 🎵 Melodify - TuneMentor

**Melodify** is a Django-based web application that connects music instructors with apprentices. It features two user roles, messaging, booking/scheduling, reviews, and a search functionality. Google OAuth2 login is also supported. The project is fully Dockerized, with CI through GitHub Actions for automated testing.

## 🚀 Features

- **User Roles & Profiles**:  
  - **Instructors**: 
    - Create/edit a profile (city, level, instruments taught)
    - Maintain personal Calendar for lesson availability (powered by django-scheduler) 
    - Confirm or cancel bookings made by apprentices
    - Get reviewed by apprentices 
  - **Apprentices**: 
    - Browse/search for instructors by city/level
    - Book lessons from instructors’ available schedules
    - Leave and update reviews (one per instructor, if a confirmed lesson was completed)

- **Booking & Scheduling**:  
  - **Instructors**: Each instructor has a calendar where they can create events (time slots).
  - **Events**: Instructors can create lessons/events (limited to 8 hours).
  - **Bookings**: Apprentices book available events. Bookings go through states: `scheduled -> confirmed -> cancelled`.
  - **Instructor Control**: Instructors confirm or cancel bookings with a reason.
  - **Apprentice View**: Apprentices see their upcoming/past bookings in one place.

- **Authentication**: 
  - **Custom User Model** (`User` extends `AbstractUser`) with `role` field: `'instructor'` or `'apprentice'`.
  - Email/password or Google OAuth2 login via `django-allauth`.
  - Profile pictures can be uploaded and displayed.

- **Messaging System**:  
  - Conversation-based: Two participants (instructor <-> apprentice or user <-> user) can exchange messages.  
  - Unread counts displayed, messages marked as read upon viewing.

- **Review System**: 
  - Apprentices can submit one review per instructor after having at least one `confirmed` and `completed` lesson.
  - Ratings from 1 to 5 stars, plus an optional text comment.
  - Instructors can see an average rating, along with all received reviews.

- **Search Functionality (Client-Side)**: 
  - Filter instructors by city and teaching level with JavaScript—immediate results from Django endpoints.
  - Automatic DOM updates (no page refresh).

- **Testing & CI**:  
  - Multiple unit tests covering views and models. 
  - `GitHub Actions` for automated testing on pushes or pull requests.

- **Docker Support**: 
  - PostgreSQL environment for production-like usage.
  - Docker Swarm deployment with secrets for database passwords.

---

## 🗂️ Project Structure Highlights

```bash
melodify/ 
├── .github/workflows/ 
├── media/profile_pictures/ 
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
- **Auth**: Simple E-mail/Password & Google OAuth2  
- **Database**: 
  - Development/Local: SQLite (default)
  - Production-like: PostgreSQL (via Docker)
- **Containerization**: Docker, Docker Compose, Docker Swarm  
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

### Usage Flow (Locally)

- **Register** a new user as `instructor` or `apprentice`.
- **Instructors** can:
  - Update their profile with city, level, instruments, and bio.
  - Create events (time slots) from "Create Event" page.
  - View booked events, confirm or cancel bookings.
- **Apprentices** can:
  - Search instructors by city/level.
  - Book an available time slot from an instructor's calendar.
  - Leave a review `only` if they have a confirmed and completed lesson with that instructor.

---

### 2. Run with Docker
📋 Prerequisites
- Docker Engine (Docker Desktop)
- Docker Swarm enabled (initialize with `docker swarm init` if not done already)
- Activate DATABASES for postgresql in settings.py (it is exist, command out), disactivate DATABASES for sqlite3

#### 🛠️ Setup+

```bash
# Create .env file
POSTGRES_DB=mydb
POSTGRES_USER=myuser
DB_HOST=db
DB_PORT=5432

# Prepare the Docker Secret
mkdir -p secrets
echo "your-strong-password" > secrets/postgres_password.txt

# Initialize Docker Swarm
docker swarm init

# Build the Application Image
docker build -t myapp:latest .

# Deploy the Stack
docker stack deploy -c docker-compose.yml mystack

# Run Migrations
docker exec -it $(docker ps --filter "name=mystack_web" -q) python manage.py migrate

# Then visit: http://localhost:8000

# Updating the Stack - For changes to code or configuration, remove the existing stack and redeploy:
docker stack rm mystack
docker stack deploy -c docker-compose.yml mystack
```

## 🔔 Booking & Scheduling Workflow

- **Instructor creates event**: Under their calendar, they specify start/end times (max 8 hours).
- **Apprentice books event**: The event is marked as `scheduled`.
- **Instructor confirms or cancels**:
  - **Confirmed** → Booked slot becomes valid, the apprentice can attend.
  - **Cancelled** → Instructor provides a reason, event is freed up.
- **Apprentice attends**: Once the event is over, the apprentice is eligible to leave a review.

**Note**: Instructors can see all their booked events on a dedicated page. Apprentices have their own page listing bookings.

## 🤝 Contributing

Pull requests are welcome. Feel free to fork and adapt this project.

## 📄 License

This project is open-source and available under the MIT License.