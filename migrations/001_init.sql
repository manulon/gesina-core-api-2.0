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
	session_id text null,
	admin_role bool not null,
	active bool not null
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
	status text not null,
    scheduled_task_id integer
);

create table if not exists execution_plan_output
(
    river text not null,
    reach text not null,
    river_stat text not null,
    execution_plan_id integer not null constraint execution_plan_output_execution_plan_fk references "execution_plan",
    stage_series_id integer default null,
    flow_series_id integer default null,
    primary key (river, reach, river_stat, execution_plan_id)
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
    user_id integer not null constraint scheduled_task_user_id_fk references "user",
    observation_days integer not null,
    forecast_days integer not null,
    start_condition_type text not null,
    restart_file text,
    calibration_id integer not null,
    calibration_id_for_simulations integer not null
);


create table if not exists "initial_flow"
(
	id serial constraint initial_flow_pk primary key,
    scheduled_task_id integer not null constraint initial_flows_scheduled_task_id_fk references "scheduled_task",
    river text not null,
    reach text not null,
    river_stat text not null,
    flow text not null
);

create table if not exists "border_condition"
(
	id serial constraint border_condition_pk primary key,
    scheduled_task_id integer not null constraint border_condition_scheduled_task_id_fk references "scheduled_task",
    river text not null,
    reach text not null,
    river_stat text not null,
    interval text not null,
    type text not null,
    series_id integer not null
);

create table if not exists "user_notification"
(
    id serial constraint notification_pk primary key,
    execution_plan_id integer not null constraint notification_execution_id_fk references "execution_plan" on delete CASCADE,
    user_id integer not null constraint notification_user_id_fk references "user" on delete CASCADE,
    seen boolean not null default False
);


create table if not exists "plan_series"
(
    id serial constraint plan_series_pk primary key,
    river text not null,
    reach text not null,
    river_stat text not null,
    stage_series_id integer default null,
    flow_series_id integer default null,
    scheduled_task_id integer not null constraint plan_series_scheduled_task_id_fk references "scheduled_task"
);
