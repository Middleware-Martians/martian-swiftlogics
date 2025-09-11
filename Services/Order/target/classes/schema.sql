CREATE TABLE IF NOT EXISTS orders (
                                      order_id SERIAL PRIMARY KEY,
                                      destination_address VARCHAR(255) NOT NULL,
    weight DOUBLE PRECISION NOT NULL,
    delivery_status VARCHAR(50) NOT NULL,
    status_message TEXT
    );
