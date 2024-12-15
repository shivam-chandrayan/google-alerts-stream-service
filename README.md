# **MegaFeed API Service**

A backend service built using **FastAPI**, designed to handle RESTful API for Google Alerts RSS Feed.

[demo link](https://google-alerts-stream-service.onrender.com "demo link")

---

## **API Documentation**

FastAPI provides auto-generated interactive API documentation:

- **Swagger UI**:  
  Access at [/doc](https://google-alerts-stream-service.onrender.com/docs"/doc")

- **ReDoc**:  
  Access at [/redoc](https://google-alerts-stream-service.onrender.com/redoc "/redoc")
  
---

## **Features**
- Manage multiple RSS feeds easily
- Bookmark entries
- Auto update alerts

---

## **Getting Started**

### **Prerequisites**
Ensure you have the following installed on your machine:
- **Python** (version 3.9 or later)
- **pip** (Python package manager)
- **virtualenv** (optional but recommended)

---

### **Installation**

1. Clone the repository:
   ```bash
   gh repo clone shivam-chandrayan/google-alerts-stream-service
   cd google-alerts-stream-service
   ```

2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: .\env\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

### **Running the Application**

To start the development server:
```bash
uvicorn app.main:app --reload
```
---

## **Deployment**

This service can be deployed using platforms like **Render**, **Heroku**, or **AWS**.

### Example Deployment on Render:
1. Push your code to a GitHub repository.
2. Link the repo to your Render account.
3. Set the environment variables in the Render dashboard.
4. Deploy using a Gunicorn or Uvicorn worker.

---

## **License**

This project is licensed under the [MIT License](LICENSE).
