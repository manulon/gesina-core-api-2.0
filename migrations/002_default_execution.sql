INSERT INTO gesina."user" (first_name, last_name, email, "password") VALUES
	 ('Admin', 'Ina', 'admin@ina.com.ar', '123456');

INSERT INTO gesina.geometry ("name", description, created_at, user_id) VALUES
	 ('Modelo1-Atucha', 'Ejemplo dado por el INA','2021-12-21 20:08:36.377642', 1);

INSERT INTO gesina.execution_plan (plan_name,geometry_id, user_id, start_datetime, end_datetime, created_at, status) VALUES
	 ('ejemplo-ina', 1, 1, '2021-12-21 20:08:39.133122', '2021-12-21 20:08:39.133122', '2021-12-21 20:08:39.133122', 'PENDING');