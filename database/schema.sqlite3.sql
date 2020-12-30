BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "game" (
	"code"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("code")
);
CREATE TABLE IF NOT EXISTS "round" (
	"number"	INTEGER NOT NULL,
	"game_code"	TEXT NOT NULL,
	PRIMARY KEY("game_code","number"),
	FOREIGN KEY("game_code") REFERENCES "game"("code") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "game_user" (
	"game_code"	TEXT NOT NULL,
	"user_uuid"	TEXT NOT NULL,
	"name"	TEXT NOT NULL,
	PRIMARY KEY("game_code","user_uuid"),
	UNIQUE("game_code","name"),
	FOREIGN KEY("user_uuid") REFERENCES "user"("uuid") ON DELETE RESTRICT,
	FOREIGN KEY("game_code") REFERENCES "game"("code") ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS "user" (
	"uuid"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("uuid")
);
CREATE TABLE IF NOT EXISTS "round_prompt" (
	"game_code"	TEXT NOT NULL,
	"round_number"	INTEGER NOT NULL,
	"user_uuid"	TEXT NOT NULL,
	"prompt_number"	INTEGER NOT NULL,
	"prompt"	TEXT NOT NULL,
	PRIMARY KEY("game_code","round_number","user_uuid","prompt_number"),
	UNIQUE("game_code","round_number","prompt"),
	FOREIGN KEY("round_number") REFERENCES "round_prompt"("number") ON DELETE CASCADE,
	FOREIGN KEY("user_uuid") REFERENCES "user"("uuid") ON DELETE RESTRICT,
	FOREIGN KEY("game_code") REFERENCES "game"("code") ON DELETE CASCADE
);
COMMIT;
