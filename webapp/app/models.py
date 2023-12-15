from app.extension import db, bcrpyt
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(50), nullable = False)
    last_name = db.Column(db.String(50), nullable = False)
    email = db.Column(db.String(100), unique= True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    account_created = db.Column(db.DateTime, default=datetime.utcnow)
    account_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate = datetime.utcnow)

    @property
    def password(self):
        raise AttributeError("Password is not readable attribute")

    @password.setter
    def password(self, password):
        self.password_hash = bcrpyt.generate_password_hash(password).decode('utf-8')

    def verify_password(self, password):
        return bcrpyt.check_password_hash(self.password_hash, password)
    
class Assignment(db.Model):
        id = db.Column(db.String(100), primary_key = True)
        name = db.Column(db.String(50), nullable=False)
        points = db.Column(db.Integer, nullable= False)
        number_of_attempts = db.Column(db.Integer, nullable = False)
        deadline = db.Column(db.DateTime, nullable = False)
        assignment_created = db.Column(db.DateTime,nullable = False ,default = datetime.utcnow)
        assignment_updated = db.Column(db.DateTime,nullable =True, default = datetime.utcnow, onupdate = datetime.utcnow)

        created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
        creator = db.relationship('User', backref='assignments')

        def serialize(self):
            """Return object data in serializable format"""
            return {
                'id':self.id,
                'name':self.name,
                'points':self.points,
                'number_of_attempts':self.number_of_attempts,
                'deadline':self.deadline.isoformat(),
                'assignment_created': self.assignment_created.isoformat(),
                'assignment_updated': self.assignment_updated.isoformat() if self.assignment_created else None
            }
        
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.String, db.ForeignKey('assignment.id'), nullable=False)
    submission_url = db.Column(db.String(200), nullable=False)
    Submission_date = db.Column(db.DateTime, default=datetime.utcnow)
    assignment_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def serialize(self):
         """Return object data in easily serializable format"""
         return {
              'id' : self.id,
              "assignment_id": self.assignment_id,
              "submission_url": self.submission_url,
              "submission_date": self.submission_date.isoformat(),
              "assigment_updated": self.assignment_updated.isoformat() if self.assignment_updated else None
         }

    


