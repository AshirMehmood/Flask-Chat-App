project flow

1. schema

schema
    
    user: name, password, picture, rooms, messages(with room info and metadata to which they were sent)
    room: name, unique id url, users, admin(user), all messages

    SQLAlchemy setup:
        it includes two parts
        1. sqlalchemy namespace-core api
        2. sqlalchemy.orm namespace-ORM
        
        
2. db.py(sqlalchemy)

'''
The Engine, when first returned by create_engine(), has not actually tried to connect to the database yet;
that happens only the first time it is asked to perform a task against the database. This is a software design pattern known as lazy initialization.
'''

from sqlalchemy import create_engine, text

engine = create_engine("sqlite+pysqlite:///:memory", echo=True)

with engine.connect() as conn:
    conn.execute(text("query"))
    conn.execute(
        "insert into some_table (x, y) values (:x, :y)",
        [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
    )
    conn.commit()

# There is also another style of committing data, which is that we can declare our “connect” block to be a transaction block up front. For this mode of operation, we use the Engine.begin() method to acquire the connection, rather than the Engine.connect() method. This method will both manage the scope of the Connection and also enclose everything inside of a transaction with COMMIT at the end, assuming a successful block, or ROLLBACK in case of exception raise. This style is known as begin once: 
    
with engine.begin() as conn:
    conn.execute(text("query"))
    conn.execute(
        "insert into some_table (x, y) values (:x, :y)",
        [{"x": 1, "y": 1}, {"x": 2, "y": 4}],
    )
    
Fetching Rows

We’ll first illustrate the Result object more closely by making use of the rows we’ve inserted previously, running a textual SELECT statement on the table we’ve created:

>>> with engine.connect() as conn:
        ...result = conn.execute(text("SELECT x, y FROM some_table"))
        ...     for row in result:
        ...         print(f"x: {row.x}  y: {row.y}")
BEGIN (implicit)
SELECT x, y FROM some_table
[...] ()
x: 1  y: 1
x: 2  y: 4
x: 6  y: 8
x: 9  y: 10
ROLLBACK

Above, the “SELECT” string we executed selected all rows from our table. The object returned is called Result and represents an iterable object of result rows.

Result has lots of methods for fetching and transforming rows, such as the Result.all() method illustrated previously, which returns a list of all Row objects. It also implements the Python iterator interface so that we can iterate over the collection of Row objects directly.

The Row objects themselves are intended to act like Python named tuples. Below we illustrate a variety of ways to access rows.

    Tuple Assignment - This is the most Python-idiomatic style, which is to assign variables to each row positionally as they are received:

    result = conn.execute(text("select x, y from some_table"))

    for x, y in result:
        ...

Integer Index - Tuples are Python sequences, so regular integer access is available too:

result = conn.execute(text("select x, y from some_table"))

for row in result:
    x = row[0]

Attribute Name - As these are Python named tuples, the tuples have dynamic attribute names matching the names of each column. These names are normally the names that the SQL statement assigns to the columns in each row. While they are usually fairly predictable and can also be controlled by labels, in less defined cases they may be subject to database-specific behaviors:

result = conn.execute(text("select x, y from some_table"))

for row in result:
    y = row.y

    # illustrate use with Python f-strings
    print(f"Row: {row.x} {y}")

Mapping Access - To receive rows as Python mapping objects, which is essentially a read-only version of Python’s interface to the common dict object, the Result may be transformed into a MappingResult object using the Result.mappings() modifier; this is a result object that yields dictionary-like RowMapping objects rather than Row objects:

result = conn.execute(text("select x, y from some_table"))

for dict_row in result.mappings():
    x = dict_row["x"]
    y = dict_row["y"]

# using ORM

from sqlalchemy.orm import Session

stmt = text("SELECT x, y FROM some_table WHERE y > :y ORDER BY x, y")
with Session(engine) as session:
    result = session.execute(stmt, {"y": 6})
    for row in result:
        print(f"x: {row.x}  y: {row.y}")


engine = create_engine('sqlite:///:memory:', echo=True)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)
    nickname = Column(String)
    
    def __repr__(self):
        return f"<User(name={self.name}, fullname={self.fullname}>"
        
Base.metadata.create_all(bind=engine)

This creates a SQLite database in memory, defines a User table with columns for id, name, fullname, and nickname, and uses SQLAlchemy’s declarative_base() system to map it to a Python User class.


https://stackoverflow.com/questions/34154660/correct-way-to-declare-an-image-field-sqlalchemy

You should never save large blobs of binary data (images etc.) to a database. Databases are not designed to work as file storage, so you will only destroy your database performance if you do that.

Like you already speculated, the better way is to save the files to disc and just store the image file name to database (image url). The added benefit is that when your application grows larger, you can just store images to some disc server or cloud or whatever and all you web hosts can access the files from there.

If you want, you can figure out some good folder structure for your images, for example one folder for profile pics etc. But with modern filesystems it does not actually matter at all. After all, you don't probably need to manage those files by hand, so finding specific files from disks is not crucial.

EDIT: I forgot to mention that at some point you might want to server your static content (images, css, js files) from other server than the dynamic flask app. If you design your system right from the beginning with that idea in mind, the scaling will 

# Declaring Image Entities

from sqlalchemy import Column, ForeignKey, Integer, Unicode
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_imageattach.entity import Image, image_attachment


Base = declarative_base()


class User(Base):
    """User model."""

    id = Column(Integer, primary_key=True)
    name = Column(Unicode, nullable=False)
    picture = image_attachment('UserPicture')
    __tablename__ = 'user'


class UserPicture(Base, Image):
    """User picture model."""

    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    user = relationship('User')
    __tablename__ = 'user_picture'

3. auth.py (auths)


4. server.py (routes/socketIO events)

Clients may request an acknowledgement callback that confirms receipt of a message they sent. Any values returned from the handler function will be passed to the client as arguments in the callback function:

@socketio.on('my event')
def handle_my_custom_event(json):
    print('received json: ' + str(json))
    # display this message to all users in a room, save in db
    return 'one', 2


Broadcasting¶

Another very useful feature of SocketIO is the broadcasting of messages. Flask-SocketIO supports this feature with the broadcast=True optional argument to send() and emit():

@socketio.on('my event')
def handle_my_custom_event(data):
    emit('my response', data, broadcast=True)

When a message is sent with the broadcast option enabled, all clients connected to the namespace receive it, including the sender. When namespaces are not used, the clients connected to the global namespace receive the message. Note that callbacks are not invoked for broadcast messages.



In all the examples shown until this point the server responds to an event sent by the client. But for some applications, the server needs to be the originator of a message. This can be useful to send notifications to clients of events that originated in the server, for example in a background thread. The socketio.send() and socketio.emit() methods can be used to broadcast to all connected clients:

def some_function():
    socketio.emit('some event', {'data': 42})



