create table game
(
    code  TEXT not null
        primary key
        unique,
    state TEXT default 'WAITING_ROOM' not null
);

create table round
(
    number    INTEGER not null,
    game_code TEXT    not null
        references game
            on delete cascade,
    current   INTEGER not null,
    id        INTEGER not null
        constraint round_pk
            primary key autoincrement,
    unique (game_code, number)
);

create unique index round_id_uindex
    on round (id);

create table user
(
    uuid TEXT not null
        primary key
        unique
);

create table player
(
    game_code   TEXT    not null
        references game
            on delete cascade,
    user_uuid   TEXT    not null
        references user
            on delete restrict,
    client_hash INTEGER not null,
    admin       INTEGER default 0 not null,
    name        TEXT    not null,
    id          INTEGER not null
        constraint player_pk
            primary key autoincrement,
    unique (game_code, user_uuid),
    unique (game_code, name)
);

create table drawing
(
    drawing   text,
    sequence  int,
    id        INTEGER not null
        constraint drawing_pk
            primary key autoincrement,
    player_id int     not null
        references player,
    round_id  int     not null
        references round
);

create unique index drawing_id_uindex
    on drawing (id);

create unique index player_id_uindex
    on player (id);

create table prompt
(
    prompt_number       INTEGER not null,
    prompt              TEXT    not null,
    id                  INTEGER not null
        constraint prompt_pk
            primary key autoincrement,
    drawing_id          int
        references drawing,
    assigned_drawing_id int
        references drawing,
    round_id            int     not null
        references round,
    player_id           int     not null
        references player
);

create unique index prompt_id_uindex
    on prompt (id);

CREATE VIEW game_current_round as
select game_code, id as round_id, number as round_number
from round
where current = true;


