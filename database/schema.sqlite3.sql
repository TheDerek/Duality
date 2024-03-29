create table game
(
	code TEXT not null
		primary key
		unique,
	state TEXT default 'WAITING_ROOM' not null
);

create table round
(
	number INTEGER not null,
	game_code TEXT not null
		references game
			on delete cascade,
	current INTEGER not null,
	id INTEGER not null
		constraint round_pk
			primary key autoincrement,
	situation_index int,
	unique (game_code, number)
);

create unique index round_game_code_situation_index_uindex
	on round (game_code, situation_index);

create table user
(
	uuid TEXT not null
		primary key
		unique
);

create table player
(
	game_code TEXT not null
		references game
			on delete cascade,
	user_uuid TEXT not null
		references user
			on delete restrict,
	client_hash INTEGER not null,
	admin INTEGER default 0 not null,
	name TEXT not null,
	id INTEGER not null
		constraint player_pk
			primary key autoincrement,
	unique (game_code, user_uuid),
	unique (game_code, name)
);

create table drawing
(
	drawing text,
	sequence int,
	id INTEGER not null
		constraint drawing_pk
			primary key autoincrement,
	player_id int not null
		references player,
	round_id int not null
		references round,
	current int default 0 not null
);

create unique index drawing_id_uindex
	on drawing (id);

create unique index player_id_uindex
	on player (id);

create table prompt
(
	prompt_number INTEGER not null,
	prompt TEXT not null,
	id INTEGER not null
		constraint prompt_pk
			primary key autoincrement,
	drawing_id int
		references drawing,
	round_id int not null
		references round,
	player_id int not null
		references player
);

create table assigned_prompt
(
	id integer not null
		constraint assigned_prompts_pk
			primary key autoincrement,
	drawing_id int not null
		references drawing,
	prompt_id int
		references prompt,
	player_id int not null
		references player
);

create unique index assigned_prompts_id_uindex
	on assigned_prompt (id);

create unique index assigned_prompts_player_id_drawing_id_uindex
	on assigned_prompt (player_id, drawing_id);

create unique index prompt_id_uindex
	on prompt (id);

CREATE VIEW game_current_round as
	select game_code, id as round_id, number as round_number from round where current=true;

CREATE VIEW scores as
SELECT
    player.id as player_id,
    round.id as round_id,
    round.number as round_number,
    (
        SELECT COUNT(1)
        FROM assigned_prompt, prompt
        WHERE assigned_prompt.player_id = player.id
          AND assigned_prompt.prompt_id = prompt.id
          AND assigned_prompt.drawing_id = prompt.drawing_id
          AND prompt.round_id = round.id
    ) as score

FROM game, round, player
WHERE player.game_code = game.code
  AND round.game_code = game.code;

