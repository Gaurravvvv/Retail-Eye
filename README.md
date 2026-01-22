# 🛒 Retail Audit - AI-Powered Inventory Management

An intelligent retail shelf auditing system that uses **YOLOv8** for object detection and **ResNet50** for visual product recognition. Built with Django, PostgreSQL + PGVector, and Docker.

---

## ✨ Features

- **📷 AI Shelf Scanning** - Capture shelf images to automatically detect and identify products
- **🎯 Visual Product Recognition** - Match detected products using deep learning embeddings
- **📊 Inventory Management** - Full CRUD operations for product catalog
- **⚠️ Low Stock Alerts** - Automated threshold monitoring and restock recommendations
- **🔐 User Authentication** - Secure login system
- **🐳 Docker Ready** - One-command deployment with Docker Compose

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Django 4.2+ |
| Database | PostgreSQL 16 with PGVector |
| Object Detection | YOLOv8 (Ultralytics) |
| Feature Extraction | ResNet50 (PyTorch) |
| Containerization | Docker & Docker Compose |

---

## 📂 Project Structure

```
Inventory/
├── docker-compose.yaml          # Multi-container orchestration
├── retail_audit_django/
│   ├── Dockerfile               # Django app container
│   ├── manage.py
│   ├── requirements.txt
│   ├── yolov8n.pt               # YOLOv8 nano model
│   ├── audit_app/
│   │   ├── models.py            # Product model with embeddings
│   │   ├── views.py             # CRUD & scanning views
│   │   ├── ai_utils.py          # YOLOv8 & ResNet50 utilities
│   │   ├── urls.py
│   │   └── templates/           # HTML templates
│   ├── retail_audit/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   └── media/                   # Uploaded images
└── venv/                        # Python virtual environment
```

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Inventory
   ```

2. **Start the application**
   ```bash
   docker-compose up --build
   ```

3. **Run migrations** (first time only)
   ```bash
   docker exec -it retail_django_app python manage.py migrate
   ```

4. **Create a superuser**
   ```bash
   docker exec -it retail_django_app python manage.py createsuperuser
   ```

5. **Access the application**
   - Web App: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

---

## 📖 How It Works

### 1️⃣ Product Registration
When adding a product with a reference image:
- **YOLOv8** detects objects in the reference image
- **ResNet50** generates a 2048-dimensional feature vector
- The embedding is stored for future matching

### 2️⃣ Shelf Scanning
When scanning a shelf image:
1. **Detection**: YOLOv8 identifies all objects in the image
2. **Recognition**: Each detection gets a ResNet50 embedding
3. **Matching**: Cosine similarity compares against registered products
4. **Visualization**: Annotated image with bounding boxes and labels

### 3️⃣ Inventory Alerts
- Products below shelf threshold trigger **restock alerts**
- System checks backroom stock for fulfillment options

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Dashboard |
| `/scan/` | GET/POST | Shelf scanning interface |
| `/manage/` | GET/POST | Add products |
| `/products/` | GET | Product list |
| `/products/<id>/` | GET | Product details |
| `/products/<id>/update/` | GET/POST | Update product |
| `/products/<id>/delete/` | POST | Delete product |
| `/inventory/` | GET | Stock overview |
| `/login/` | GET/POST | User login |

---

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | `db` | PostgreSQL host |
| `DB_NAME` | `retail_db` | Database name |
| `DB_USER` | `user` | Database user |
| `DB_PASSWORD` | `password` | Database password |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Allowed hosts |

---

## 🧪 Development

### Local Setup (without Docker)

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
cd retail_audit_django
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

---

## 📋 Requirements

```
django>=4.2
ultralytics
torch
torchvision
numpy
pillow
opencv-python-headless
psycopg2-binary
pgvector
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙋 Support

For issues or questions, please open an issue in the repository.
