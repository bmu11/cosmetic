from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select, distinct

DATABASE_URL = 'sqlite:///cosmetic.db'
engine = create_engine(DATABASE_URL, echo=True)
metadata = MetaData()
products_table = Table(
    'all', metadata,
    Column('id', Integer, primary_key=True),
    Column('photo', String),
    Column('title', String),
    Column('category', String),
    Column('massa', String),
    Column('country', String),
    Column('desc', String),
    Column('use', String),
    Column('struct', String),
    Column('color', String),
    Column('price', String),
    Column('brand', String),
    Column('type', String)
)

metadata.create_all(engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_all_products():
    session = SessionLocal()
    products = session.execute(select(products_table)).fetchall()
    session.close()
    return products

def insert_product(photo, title, category, massa, country, desc, use, struct, color, price, brand, type):
    session = SessionLocal()
    ins = products_table.insert().values(
        photo=photo if photo else "не найдено",
        title=title if title else "не найдено",
        category=category if category else "не найдено",
        massa=massa if massa else "не найдено",
        country=country if country else "не найдено",
        desc=desc if desc else "не найдено",
        use=use if use else "не найдено",
        struct=struct if struct else "не найдено",
        color=color if color else "не найдено",
        price=price if price else "не найдено",
        brand=brand if brand else "не найдено",
        type=type if type else "не найдено"
    )
    session.execute(ins)
    session.commit()
    session.close()

def delete_products_with_title_not_found():
    session = SessionLocal()
    session.execute(products_table.delete().where(products_table.c.title == "не найдено"))
    session.commit()
    session.close()
    print("строки с title 'не найдено' были удалены.")

def delete_products_with_desc_not_found():
    session = SessionLocal()
    session.execute(products_table.delete().where(products_table.c.desc == "не найдено"))
    session.execute(products_table.delete().where(products_table.c.desc == "описание не найдено"))
    session.commit()
    session.close()
    print("строки с desc 'не найдено' были удалены.")

def delete_duplicate_titles():
    session = SessionLocal()
    unique_titles = session.execute(select(distinct(products_table.c.title))).fetchall()

    for title_tuple in unique_titles:
        title = title_tuple[0]
        duplicates = session.execute(select(products_table).where(products_table.c.title == title)).fetchall()

        if len(duplicates) > 1:
            for duplicate in duplicates[1:]:
                session.execute(products_table.delete().where(products_table.c.id == duplicate.id))
                print(f"удалена запись с id: {duplicate.id} и title: {title}")

    session.commit()
    session.close()
    print("дубликаты записей были удалены.")
