-- Create CMS database and user
CREATE DATABASE cms_db;
CREATE USER cms_user WITH ENCRYPTED PASSWORD 'cms_password';
GRANT ALL PRIVILEGES ON DATABASE cms_db TO cms_user;

-- Create ROS database and user
CREATE DATABASE ros_db;
CREATE USER ros_user WITH ENCRYPTED PASSWORD 'ros_password';
GRANT ALL PRIVILEGES ON DATABASE ros_db TO ros_user;

-- Create WMS database and user
CREATE DATABASE wms_db;
CREATE USER wms_user WITH ENCRYPTED PASSWORD 'wms_password';
GRANT ALL PRIVILEGES ON DATABASE wms_db TO wms_user;
