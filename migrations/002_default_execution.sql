INSERT INTO gesina."user" (first_name, last_name, email, "password") VALUES
	 ('Admin', 'Ina', 'admin@ina.com.ar', 'pbkdf2:sha256:260000$ejlxRPQiZOMWt2o2$f856120dd2d2170c070b1648524000f6803ef28eb2ad9af96523ad900e454743');

INSERT INTO gesina.geometry ("name", description, created_at, user_id) VALUES
	 ('Modelo1-Atucha.g01', 'Ejemplo dado por el INA','2021-12-21 20:08:36.377642', 1);

INSERT INTO gesina.execution_plan (plan_name,geometry_id, user_id, start_datetime, end_datetime, created_at, status) VALUES
	 ('ejemplo-ina', 1, 1, '2021-12-21 20:08:39.133122', '2021-12-21 20:08:39.133122', '2021-12-21 20:08:39.133122', 'PENDING');


INSERT INTO gesina.scheduled_task (id, name, description, frequency, geometry_id, user_id, start_datetime, metadata) VALUES
	 (1, 'Paraná', 'Corrida periódica del rio Paraná', 360, 1, 1, '2021-12-21 00:00:00.000000', null);
