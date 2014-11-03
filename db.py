#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy import Enum, Unicode, Boolean, SmallInteger, Date
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.hybrid import hybrid_property

import sqlalchemy.types as types

Gender = Enum(u"男", u"女", name="gender_type")

Base = declarative_base()


class BaseMixin(object):

    __prefix__ = 'neu_'
    __protected_attributes__ = set([
        "created_at", "updated_at"])
    # @declared_attr
    # def __tablename__(cls):
    #     return 'neu_' + cls.__name__.lower()

    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)

class AccountMixin(object):
    # 是否验证过
    verified = Column(Boolean)
    # 是否通过验证
    passok = Column(Boolean)

class Staff(BaseMixin, Base):
    __tablename__ = "staff"
    id = Column(String(8), primary_key=True)
    name = Column(Unicode(20))
    gender = Column(Gender)

    department_id = Column(Integer, ForeignKey('department.id'))
    department = relationship("Department", backref="staffs")

    memo = Column(String(255))

class Department(Base, BaseMixin):
    __tablename__ = "department"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(50), unique=True)

    memo = Column(String(255))


class Student(Base, BaseMixin):
    __tablename__ = "student"
    id = Column(Integer, primary_key=True)
    # 学号
    no = Column(String(10), unique=True)
    name = Column(Unicode(20))
    gender = Column(Gender)

    # 这里有数据不一致的情况会出现，暂时不考虑，允许错误数据
    college_id = Column(Integer, ForeignKey('college.id'))
    college = relationship("College")

    major_id = Column(Integer, ForeignKey('major.id'))
    major = relationship("Major")

    class_id = Column(Integer, ForeignKey('class.id'))
    klass = relationship("Class")

    memo = Column(String(255))


class College(Base, BaseMixin):
    __tablename__ = "college"
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(20), unique=True)
    english_name = Column(String(200), unique=True)
    code = Column(String(10))   # english letter code eg. ise
    alias1 = Column(Unicode(10), unique=True)
    alias2 = Column(Unicode(10), unique=True)

    department_id = Column(Integer, ForeignKey('department.id'))
    department = relationship("Department")

    memo = Column(String(255))

class Major(Base, BaseMixin):
    __tablename__ = "major"
    id = Column(Integer, primary_key=True)

    no = Column(String(10), unique=True)

    name = Column(Unicode(20))
    alias1 = Column(Unicode(10), unique=True)
    alias2 = Column(Unicode(10), unique=True)

    college_id = Column(Integer, ForeignKey('college.id'))
    college = relationship("College", backref="majors")
    # alter table college add column memo varchar(255);
    # alter table college drop column meno;
    memo = Column(String(255))

class Class(Base, BaseMixin):
    __tablename__ = "class"
    id = Column(Integer, primary_key=True)

    no = Column(String(10), unique=True)
    name = Column(Unicode(40))

    alias1 = Column(Unicode(10), unique=True)
    alias2 = Column(Unicode(10), unique=True)
    # come year
    grade = Column(SmallInteger)

    major_id = Column(Integer, ForeignKey('major.id'))
    major = relationship("Major", backref="classes")

    memo = Column(String(255))

    @hybrid_property
    def college(self):
        return self.major.college

class Course(object):
    pass


# accounts
class LibraryAccount(Base, BaseMixin, AccountMixin):
    __tablename__ = "library_account"
    id = Column(Integer, primary_key=True)
    barcode = Column(String(10), unique=True)
    # 明文密码
    password = Column(String(160))
    expired_at = Column(Date)

    # 8 位一卡通
    ecard = Column(String(8), unique=True, nullable=True)

    # one-to-one
    student_id =Column(Integer, ForeignKey(Student.id))
    student = relationship('Student', uselist=False, backref="library_account")



# require psycopg2
# so use pg8000 as pure python
# engine = create_engine('postgresql+pg8000://wangmm:123456@192.168.1.100:5432/wangmm', echo=True)
engine = create_engine('postgresql+pg8000://wangmm:123456@192.168.1.100:5432/wangmm', echo=False)
# engine = create_engine('sqlite:///orm_in_detail.sqlite')

Session = sessionmaker()
Session.configure(bind=engine)
Base.metadata.create_all(engine)


def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        return instance


'''
SQL
select s.name, s.no, s.gender, c.name, m.name from student s, class c, major m where s.class_id = c.id and c.major_id = m.id order by s.no desc;


'''
