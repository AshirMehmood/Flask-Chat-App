DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS room;

CREATE TABLE user(
    id integer primary key autoincrement,
    username text unique not null,
    password text not null,
    email text not null
    
);

CREATE TABLE room(
    room_id integer primary key autoincrement,
    room_name text unique
);
