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
    primary key (game_code, number)
);

create table user
(
    uuid TEXT not null
        primary key
        unique
);

create table drawing
(
    drawing      text,
    round_number int     not null
        constraint round_drawings_round_number_fk
            references round (number)
            on delete cascade,
    game_code    text    not null
        references game
            on delete cascade,
    user_uuid    text    not null
        references user,
    sequence     int,
    id           INTEGER not null
        constraint drawing_pk
            primary key autoincrement
);

create unique index drawing_id_uindex
    on drawing (id);

create unique index one_drawing_per_user_per_round
    on drawing (round_number, game_code, user_uuid);

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
    primary key (game_code, user_uuid),
    unique (game_code, name)
);

create table prompt
(
    game_code     TEXT    not null
        references game
            on delete cascade,
    round_number  INTEGER not null
        references round (number)
            on delete cascade,
    user_uuid     TEXT    not null
        references user
            on delete restrict,
    prompt_number INTEGER not null,
    prompt        TEXT    not null,
    id            INTEGER not null
        constraint prompt_pk
            primary key autoincrement,
    drawing_id    int
        references drawing,
    unique (game_code, round_number, user_uuid, prompt_number),
    unique (game_code, round_number, prompt)
);

create unique index prompt_id_uindex
    on prompt (id);


