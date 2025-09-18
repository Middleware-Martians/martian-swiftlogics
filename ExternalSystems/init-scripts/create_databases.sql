-- Create CMS database and user
CREATE DATABASE cms_db;
CREATE USER cms_user WITH ENCRYPTED PASSWORD 'cms_password';
GRANT ALL PRIVILEGES ON DATABASE cms_db TO cms_user;

-- Connect to cms_db to grant schema permissions
\c cms_db
GRANT ALL ON SCHEMA public TO cms_user;
GRANT CREATE ON SCHEMA public TO cms_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO cms_user;

-- Back to postgres database for other users
\c postgres

-- Create ROS database and user
CREATE DATABASE ros_db;
CREATE USER ros_user WITH ENCRYPTED PASSWORD 'ros_password';
GRANT ALL PRIVILEGES ON DATABASE ros_db TO ros_user;

-- Connect to ros_db to grant schema permissions
\c ros_db
GRANT ALL ON SCHEMA public TO ros_user;
GRANT CREATE ON SCHEMA public TO ros_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO ros_user;

-- Back to postgres database for WMS user
\c postgres

-- Create WMS database and user
CREATE DATABASE wms_db;
CREATE USER wms_user WITH ENCRYPTED PASSWORD 'wms_password';
GRANT ALL PRIVILEGES ON DATABASE wms_db TO wms_user;

-- Connect to wms_db to grant schema permissions
\c wms_db
GRANT ALL ON SCHEMA public TO wms_user;
GRANT CREATE ON SCHEMA public TO wms_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO wms_user;
