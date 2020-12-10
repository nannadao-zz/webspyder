from sqlalchemy import create_engine, Column, Integer, String, Date
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine("DATABASE_URI", echo=True)
Session = sessionmaker(bind=engine)

class Report(Base):
  __tablename__ = 'prices'
  data_id = Column('data_id', Integer, primary_key=True)
  created_date = Column('created_date', Date, server_default=func.now())
  hotel_name = Column('hotel_name', String)
  room_name = Column('room_name', String)
  room_price = Column('room_price', Integer)

  def add(self):
    session = Session()
    session.add(self)
    session.commit()
    session.close()

if __name__ == "__main__":
  Base.metadata.create_all(bind=engine)