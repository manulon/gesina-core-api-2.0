create schema gesina;
create schema scheduler;

SET search_path TO gesina;

create table if not exists "user"
(
	id serial constraint user_pk primary key,
	first_name text not null,
	last_name text not null,
	email text not null,
	password text not null,
	session_id text null
);

alter table "user" owner to "user";

create table if not exists geometry
(
	id serial constraint geometry_pk primary key,
	name text not null,
	description text,
	created_at timestamp default now() not null,
	user_id integer not null constraint geometry_user_id_fk references "user"
);

alter table geometry owner to "user";

create unique index if not exists geometry_id_uindex
	on geometry (id);

create unique index if not exists geometry_name_uindex
	on geometry (name);

create unique index if not exists user_id_uindex
	on "user" (id);

create table if not exists execution_plan
(
	id serial constraint execution_plan_pk primary key,
	plan_name varchar not null,
	geometry_id integer not null constraint execution_plan_geometry_id_fk references geometry,
	user_id integer not null constraint execution_plan_user_id_fk references "user",
	start_datetime timestamp not null,
	end_datetime timestamp not null,
	created_at timestamp not null,
	status text not null
);

alter table execution_plan owner to "user";

create unique index if not exists execution_plan_id_uindex on execution_plan (id);


create table if not exists "scheduled_task"
(
	id serial constraint scheduled_task_pk primary key,
	name text not null,
	description text not null,
	frequency integer not null,
	start_datetime timestamp not null,
	metadata jsonb null,
	created_at timestamp default now() not null,
    enabled bool default true not null,
    geometry_id integer not null constraint scheduled_task_geometry_id_fk references geometry,
    user_id integer not null constraint scheduled_task_user_id_fk references "user"
);
