package com.martian.clientms.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;
import java.sql.Connection;

@Component
public class DatabaseConnectionChecker {

    private final DataSource dataSource;
    private final Logger logger = LoggerFactory.getLogger(DatabaseConnectionChecker.class);

    public DatabaseConnectionChecker(DataSource dataSource) {
        this.dataSource = dataSource;
    }

    @EventListener(ApplicationReadyEvent.class)
    public void checkConnection() {
        try (Connection conn = dataSource.getConnection()) {
            if (conn != null && !conn.isClosed()) {
                String url = conn.getMetaData().getURL();
                logger.info("Successfully connected to the database: {}", url);
            } else {
                logger.error("Database connection is null or closed after startup");
            }
        } catch (Exception ex) {
            logger.error("Failed to connect to the database on startup: {}", ex.getMessage(), ex);
        }
    }
}

