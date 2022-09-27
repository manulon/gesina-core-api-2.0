INSERT INTO gesina."user" (first_name, last_name, email, "password") VALUES
	 ('Admin', 'Ina', 'admin@ina.com.ar', 'pbkdf2:sha256:260000$GHfgkUcvLSdnsckm$328bead9fe19b7978903164cbeb4fdf33c1a7e506544c221ac2270b80e8bcdcd');

INSERT INTO gesina.geometry ("name", description, created_at, user_id) VALUES
	 ('Modelo1-Atucha.g01', 'Ejemplo dado por el INA','2021-12-21 20:08:36.377642', 1);

INSERT INTO gesina.geometry ("name", description, created_at, user_id) VALUES
	 ('DeltaParana_2017.g01', 'Geometría Paraná','NOW()', 1);

INSERT INTO gesina.execution_plan (plan_name,geometry_id, user_id, start_datetime, end_datetime, created_at, status) VALUES
	 ('ejemplo-ina', 1, 1, '2021-12-21 20:08:39.133122', '2021-12-21 20:08:39.133122', '2021-12-21 20:08:39.133122', 'PENDING');


INSERT INTO gesina.scheduled_task (name, description, frequency, geometry_id, user_id, start_datetime, metadata,
    observation_days, forecast_days, start_condition_type) VALUES
	 ('Paraná', 'Corrida periódica del rio Paraná', 360, 2, 1, '2021-12-21 00:00:00.000000', null,
	 90, 4, 'restart_file');

INSERT INTO gesina.border_condition (
    scheduled_task_id, river, reach, river_stat, interval, type, series_id) values (
    1, 'Parana', 'ParanaAA', '224000', '1-DAY', 'STAGE_HYDROGRAPH', 1);

INSERT INTO gesina.border_condition (
    scheduled_task_id, river, reach, river_stat, interval, type, series_id) values (
    1, 'Lujan', '1', '30.664', '1-HOUR', 'FLOW_HYDROGRAPH', 1);

INSERT INTO gesina.border_condition (
    scheduled_task_id, river, reach, river_stat, interval, type, series_id) values (
    1, 'Ibicuy', 'Ibicuy', '67.930*', '1-HOUR', 'LATERAL_INFLOW_HYDROGRAPH', 1);

INSERT INTO gesina.border_condition (
    scheduled_task_id, river, reach, river_stat, interval, type, series_id) values (
    1, 'Lujan', 'Desembocadura', '0', '1-HOUR', 'STAGE_HYDROGRAPH', 1);

INSERT INTO gesina.border_condition (
    scheduled_task_id, river, reach, river_stat, interval, type, series_id) values (
    1, 'SanAntonio', 'Desembocadura', '0', '1-HOUR', 'STAGE_HYDROGRAPH', 1);

INSERT INTO gesina.border_condition (
    scheduled_task_id, river, reach, river_stat, interval, type, series_id) values (
    1, 'CanaldelEste', 'Desembocadura', '0', '1-HOUR', 'STAGE_HYDROGRAPH', 1);

INSERT INTO gesina.border_condition (
    scheduled_task_id, river, reach, river_stat, interval, type, series_id) values (
    1, 'Palmas', 'Desembocadura', '6246.783', '1-HOUR', 'STAGE_HYDROGRAPH', 1);

INSERT INTO gesina.border_condition (
    scheduled_task_id, river, reach, river_stat, interval, type, series_id) values (
    1, 'Mini', 'Desembocadura', '0', '1-HOUR', 'STAGE_HYDROGRAPH', 1);

INSERT INTO gesina.border_condition (
    scheduled_task_id, river, reach, river_stat, interval, type, series_id) values (
    1, 'LaBarquita', 'Desembocadura', '0', '1-HOUR', 'STAGE_HYDROGRAPH', 1);

INSERT INTO gesina.border_condition (
    scheduled_task_id, river, reach, river_stat, interval, type, series_id) values (
    1, 'BarcaGrande', 'Desembocadura', '0', '1-HOUR', 'STAGE_HYDROGRAPH', 1);

INSERT INTO gesina.border_condition (
    scheduled_task_id, river, reach, river_stat, interval, type, series_id) values (
    1, 'Guazu', 'Desembocadura', '8000', '1-HOUR', 'STAGE_HYDROGRAPH', 1);

INSERT INTO gesina.border_condition (
    scheduled_task_id, river, reach, river_stat, interval, type, series_id) values (
    1, 'Sauce', 'Desembocadura', '0', '1-HOUR', 'STAGE_HYDROGRAPH', 1);

INSERT INTO gesina.border_condition (
    scheduled_task_id, river, reach, river_stat, interval, type, series_id) values (
    1, 'Bravo', 'Desembocadura', '0', '1-HOUR', 'STAGE_HYDROGRAPH', 1);

INSERT INTO gesina.border_condition (
    scheduled_task_id, river, reach, river_stat, interval, type, series_id) values (
    1, 'Gutierrez', 'Desembocadura', '1960.748', '1-HOUR', 'STAGE_HYDROGRAPH', 1);

INSERT INTO gesina.border_condition (
    scheduled_task_id, river, reach, river_stat, interval, type, series_id) values (
    1, 'Gutierrez', 'Desembocadura', '1960.748', '1-HOUR', 'STAGE_HYDROGRAPH', 1);
