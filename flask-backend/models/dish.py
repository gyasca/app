from extensions import db

# Dish model
class Dish(db.Model):
    __tablename__ = 'dishes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    avg_calories = db.Column(db.Float, nullable=False)
    ingredients = db.relationship('Ingredient', backref='dish', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Dish {self.name}>"