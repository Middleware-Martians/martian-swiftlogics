@echo off
echo Connecting to PostgreSQL database...
echo.
echo Available commands:
echo   \l                    - List all databases
echo   \c database_name      - Connect to a specific database
echo   \dt                   - List tables in current database
echo   \d table_name         - Describe table structure
echo   SELECT * FROM orders; - Show all orders
echo   \q                    - Quit
echo.
docker exec -it swiftlogistics_postgres psql -U admin_user -d cms_db