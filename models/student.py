from database.db import db

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), unique=True)
    batch = db.Column(db.String(50))
    fees_paid = db.Column(db.Float, default=0)

    def __repr__(self):
        return f"<Student {self.name}>"