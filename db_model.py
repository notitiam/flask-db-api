from peewee import *

dbhandle = SqliteDatabase('./CardPunch.db')
class BaseModel(Model):
    class Meta:
        database = dbhandle

class Employee(BaseModel):
    EmpID = CharField(max_length=25)
    CardID = CharField(max_length=20)
    Date = DateField()
    EmpName = CharField(max_length=100)
    Category = CharField(max_length=100)
    

dbhandle.connect()
dbhandle.create_tables([Employee])
