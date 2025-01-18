from app import db


class EmailRecipient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=True)
    active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return super().__repr__() + f" {self.name}"
