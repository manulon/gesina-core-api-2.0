create schema gesina;

create table if not exists gesina."user"
(
	id serial constraint user_pk primary key,
	name text not null,
	lastname text not null,
	email text not null,
	password text not null,
	session_id text null
);

alter table gesina."user" owner to "user";

create table if not exists gesina.geometry
(
	id serial constraint geometry_pk primary key,
	name text not null,
	description text,
	created_at timestamp default now() not null,
	user_id integer not null constraint geometry_user_id_fk references gesina."user"
);

alter table gesina.geometry owner to "user";

create unique index if not exists geometry_id_uindex
	on gesina.geometry (id);

create unique index if not exists geometry_name_uindex
	on gesina.geometry (name);

create unique index if not exists user_id_uindex
	on gesina."user" (id);

create table if not exists gesina.execution_plan
(
	id serial constraint execution_plan_pk primary key,
	plan_name varchar not null,
	geometry_id integer not null constraint execution_plan_geometry_id_fk references gesina.geometry,
	user_id integer not null constraint execution_plan_user_id_fk references gesina."user",
	start_datetime timestamp not null,
	end_datetime timestamp not null,
	created_at timestamp not null,
	status text not null
);

alter table gesina.execution_plan owner to "user";

create unique index if not exists execution_plan_id_uindex on gesina.execution_plan (id);

