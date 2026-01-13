from init_db import init_db
from init_exam_db import init_exam_db
from init_institute import init_institute
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from flask_cors import CORS
from routes.student_routes import student_bp
from routes.attendance_routes import attendance_bp
from routes.auth_routes import auth_bp
from routes.fees_routes import fees_bp
from routes.dashboard_routes import dashboard_bp
from routes.invoice_routes import invoice_bp
from routes.exam_routes import exam_bp
from routes.student_profile_routes import profile_bp
from routes.report_card_routes import report_bp
from routes.report_card_pdf_routes import report_pdf_bp
from routes.performance_routes import performance_bp
from routes.weekly_report_pdf_routes import weekly_pdf_bp
from routes.monthly_report_pdf_routes import monthly_pdf_bp
from routes.performance_graph_pdf_routes import performance_graph_bp
from routes.parent_dashboard_routes import parent_dashboard_bp
from routes.parent_auth_routes import parent_auth_bp
from routes.whatsapp_send_routes import whatsapp_send_bp
from routes.monthly_analytics_routes import monthly_analytics_bp
from routes.admin_dashboard_routes import admin_dashboard_bp

app = Flask(__name__)
CORS(app)

# Auto-create database on server start
init_db()
init_exam_db()
init_institute()

# 🔴 REGISTER BLUEPRINTS (MANDATORY)
app.register_blueprint(student_bp)
app.register_blueprint(attendance_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(fees_bp)
app.register_blueprint(dashboard_bp)  
app.register_blueprint(invoice_bp)
app.register_blueprint(exam_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(report_bp)
app.register_blueprint(report_pdf_bp)
app.register_blueprint(performance_bp)
app.register_blueprint(weekly_pdf_bp)
app.register_blueprint(monthly_pdf_bp)
app.register_blueprint(performance_graph_bp)
app.register_blueprint(parent_dashboard_bp)
app.register_blueprint(parent_auth_bp)
app.register_blueprint(whatsapp_send_bp)
app.register_blueprint(monthly_analytics_bp)
app.register_blueprint(admin_dashboard_bp)

# 🔍 DEBUG: show all routes
print(app.url_map)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)