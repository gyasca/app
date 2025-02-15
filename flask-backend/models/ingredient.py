from extensions import db

# Ingredient model
class Ingredient(db.Model):
    __tablename__ = 'ingredients'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    calories = db.Column(db.Float, nullable=False)
    carb = db.Column(db.Float, nullable=False)
    protein = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    increment_type = db.Column(db.String(20), nullable=False)  # e.g., 'grams', 'pieces', etc.

    def __repr__(self):
        return f"<Ingredient {self.name}>"