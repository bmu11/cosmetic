from flask import Flask, render_template
from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

DATABASE_URL = 'sqlite:///cosmetic.db'
engine = create_engine(DATABASE_URL, echo=True)
metadata = MetaData()
products_table = Table(
    'all', metadata,
    autoload_with=engine
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@app.route('/')
def home():
    session = SessionLocal()
    categories = session.execute(select(products_table.c.type).distinct()).fetchall()
    session.close()
    return render_template('index.html', categories=[c[0] for c in categories])

@app.route('/category/<string:type>')
def category(type):
    session = SessionLocal()
    products = session.execute(select(products_table).where(products_table.c.type == type)).fetchall()
    session.close()
    return render_template('category.html', type=type, products=products)

if __name__ == '__main__':
    app.run(debug=True)
