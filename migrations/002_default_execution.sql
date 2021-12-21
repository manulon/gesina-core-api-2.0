INSERT INTO gesina."user" (id, "name", lastname,email, "password") VALUES
	 (1, 'Admin','Ina','admin@ina.com.ar','123456');

INSERT INTO gesina.geometry (id, "name", description, created_at, user_id) VALUES
	 (1, 'Modelo1-Atucha','Ejemplo dado por el INA','2021-12-21 20:08:36.377642',1);

INSERT INTO gesina.execution_plan (id, plan_name,geometry_id, user_id, start_datetime, end_datetime, created_at, status) VALUES
	 (1, 'ejemplo-ina',1,1,'2021-12-21 20:08:39.133122','2021-12-21 20:08:39.133122','2021-12-21 20:08:39.133122','PENDING');