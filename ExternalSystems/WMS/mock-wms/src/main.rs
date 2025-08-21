use anyhow::Result;
use log::{info, error, warn};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::io::{AsyncReadExt, AsyncWriteExt};
use tokio::net::{TcpListener, TcpStream};
use tokio::sync::Mutex;
use std::collections::HashMap;
use chrono::{DateTime, Utc};
use std::env;

// Data structures matching the implementation guide
#[derive(Debug, Serialize, Deserialize)]
struct DispatchRequest {
    order_id: u32,
    items: Vec<DispatchItem>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct DispatchItem {
    item_id: u32,
    quantity: u32,
}

#[derive(Debug, Serialize, Deserialize)]
struct WmsResponse {
    status: String,
    message: String,
}

// In-memory storage for inventory and dispatches
#[derive(Debug, Clone, Serialize, Deserialize)]
struct InventoryItem {
    item_id: u32,
    item_name: String,
    quantity: u32,
    warehouse_location: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
struct Dispatch {
    dispatch_id: u32,
    order_id: u32,
    items: Vec<DispatchItem>,
    status: String,
    created_at: DateTime<Utc>,
}

// Database structure
struct Database {
    inventory: HashMap<u32, InventoryItem>,
    dispatches: Vec<Dispatch>,
    next_dispatch_id: u32,
}

impl Database {
    fn new() -> Self {
        // Initialize with some sample inventory
        let mut inventory = HashMap::new();
        inventory.insert(1, InventoryItem {
            item_id: 1,
            item_name: "Widget A".to_string(),
            quantity: 100,
            warehouse_location: "A1".to_string(),
        });
        
        inventory.insert(2, InventoryItem {
            item_id: 2,
            item_name: "Widget B".to_string(),
            quantity: 200,
            warehouse_location: "B2".to_string(),
        });
        
        inventory.insert(3, InventoryItem {
            item_id: 3,
            item_name: "Widget C".to_string(),
            quantity: 50,
            warehouse_location: "C3".to_string(),
        });

        Self {
            inventory,
            dispatches: Vec::new(),
            next_dispatch_id: 1,
        }
    }

    fn get_inventory(&self, item_id: u32) -> Option<&InventoryItem> {
        self.inventory.get(&item_id)
    }

    fn create_dispatch(&mut self, dispatch_req: DispatchRequest) -> Dispatch {
        let dispatch = Dispatch {
            dispatch_id: self.next_dispatch_id,
            order_id: dispatch_req.order_id,
            items: dispatch_req.items,
            status: "PENDING".to_string(),
            created_at: Utc::now(),
        };
        
        self.dispatches.push(dispatch.clone());
        self.next_dispatch_id += 1;
        dispatch
    }

    fn update_inventory_for_dispatch(&mut self, dispatch_id: u32) -> Result<(), String> {
        if let Some(dispatch_index) = self.dispatches.iter().position(|d| d.dispatch_id == dispatch_id) {
            let dispatch = &mut self.dispatches[dispatch_index];
            
            // Check if we have enough inventory
            for item in &dispatch.items {
                if let Some(inventory_item) = self.inventory.get_mut(&item.item_id) {
                    if inventory_item.quantity < item.quantity {
                        return Err(format!("Insufficient inventory for item {}", item.item_id));
                    }
                } else {
                    return Err(format!("Item {} not found in inventory", item.item_id));
                }
            }
            
            // Update inventory
            for item in &dispatch.items {
                if let Some(inventory_item) = self.inventory.get_mut(&item.item_id) {
                    inventory_item.quantity -= item.quantity;
                }
            }
            
            dispatch.status = "PROCESSING".to_string();
            Ok(())
        } else {
            Err(format!("Dispatch {} not found", dispatch_id))
        }
    }
}

async fn handle_connection(mut socket: TcpStream, db: Arc<Mutex<Database>>) {
    let addr = socket.peer_addr().unwrap();
    info!("New connection from: {}", addr);

    let mut buffer = [0; 1024];
    
    // Read incoming data
    match socket.read(&mut buffer).await {
        Ok(n) => {
            if n == 0 {
                warn!("Connection closed by client: {}", addr);
                return;
            }
            
            info!("Received {} bytes from {}", n, addr);
            let data = &buffer[0..n];
            
            // Get data as string for logging and checking if it's HTTP
            let data_str = String::from_utf8_lossy(data);
            info!("Received raw data: {}", data_str);
            
            // Check if this is an HTTP request (starts with GET, POST, etc.)
            if data_str.starts_with("GET ") || data_str.starts_with("POST ") || 
               data_str.starts_with("PUT ") || data_str.starts_with("DELETE ") {
                info!("Detected HTTP request, sending 404 response");
                let http_response = "HTTP/1.1 404 Not Found\r\nContent-Type: application/json\r\n\r\n{\"error\":\"This is a TCP JSON API endpoint. HTTP requests should go to port 5001.\"}";
                if let Err(e) = socket.write_all(http_response.as_bytes()).await {
                    error!("Failed to send HTTP response: {}", e);
                }
                return;
            }
            
            // Try to parse as JSON
            match serde_json::from_slice::<DispatchRequest>(data) {
                Ok(dispatch_req) => {
                    info!("Parsed dispatch request: {:?}", dispatch_req);
                    
                    // Process the dispatch request
                    let mut db = db.lock().await;
                    let dispatch = db.create_dispatch(dispatch_req);
                    
                    // Simulate processing
                    match db.update_inventory_for_dispatch(dispatch.dispatch_id) {
                        Ok(_) => {
                            info!("Dispatch {} processed successfully", dispatch.dispatch_id);
                            
                            // Send acknowledgment
                            let response = WmsResponse {
                                status: "WMS_OK".to_string(),
                                message: "Dispatch received".to_string(),
                            };
                            
                            let response_json = serde_json::to_string(&response).unwrap();
                            if let Err(e) = socket.write_all(response_json.as_bytes()).await {
                                error!("Failed to send response: {}", e);
                            }
                        }
                        Err(e) => {
                            error!("Failed to process dispatch: {}", e);
                            
                            // Send error response
                            let response = WmsResponse {
                                status: "WMS_ERROR".to_string(),
                                message: format!("Error: {}", e),
                            };
                            
                            let response_json = serde_json::to_string(&response).unwrap();
                            if let Err(e) = socket.write_all(response_json.as_bytes()).await {
                                error!("Failed to send response: {}", e);
                            }
                        }
                    }
                }
                Err(e) => {
                    error!("Failed to parse JSON: {}", e);
                    
                    // Send error response
                    let response = WmsResponse {
                        status: "WMS_ERROR".to_string(),
                        message: "Invalid JSON format".to_string(),
                    };
                    
                    let response_json = serde_json::to_string(&response).unwrap();
                    if let Err(e) = socket.write_all(response_json.as_bytes()).await {
                        error!("Failed to send response: {}", e);
                    }
                }
            }
        }
        Err(e) => {
            error!("Failed to read from socket: {}", e);
        }
    }
}

// REST API handler (separate from TCP server)
mod http_api {
    use super::*;
    use axum::{
        routing::get,
        extract::{State, Path},
        http::StatusCode,
        Json, Router,
    };

    pub async fn start_api_server(db: Arc<Mutex<Database>>) -> Result<()> {
        let app = Router::new()
            .route("/inventory/:item_id", get(get_inventory_item))
            .route("/inventory", get(get_all_inventory))
            .route("/dispatches", get(get_all_dispatches))
            .with_state(db);

        let addr = "0.0.0.0:5001";
        info!("HTTP API server listening on {}", addr);
        let listener = tokio::net::TcpListener::bind(addr).await?;
        axum::serve(listener, app).await?;
        Ok(())
    }

    async fn get_inventory_item(
        State(db): State<Arc<Mutex<Database>>>,
        Path(item_id): Path<u32>,
    ) -> Result<Json<InventoryItem>, StatusCode> {
        let db = db.lock().await;
        match db.get_inventory(item_id) {
            Some(item) => Ok(Json(item.clone())),
            None => Err(StatusCode::NOT_FOUND),
        }
    }

    async fn get_all_inventory(
        State(db): State<Arc<Mutex<Database>>>,
    ) -> Json<Vec<InventoryItem>> {
        let db = db.lock().await;
        let items: Vec<InventoryItem> = db.inventory.values().cloned().collect();
        Json(items)
    }

    async fn get_all_dispatches(
        State(db): State<Arc<Mutex<Database>>>,
    ) -> Json<Vec<Dispatch>> {
        let db = db.lock().await;
        Json(db.dispatches.clone())
    }
}

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging
    env_logger::init_from_env(env_logger::Env::default().default_filter_or("info"));

    // Create shared database
    let db = Arc::new(Mutex::new(Database::new()));
    let api_db = db.clone();

    // Start API server in a separate task
    tokio::spawn(async move {
        if let Err(e) = http_api::start_api_server(api_db).await {
            error!("API server error: {}", e);
        }
    });

    // TCP port from environment or default
    let port = env::var("WMS_PORT").unwrap_or_else(|_| "5000".to_string());
    let addr = format!("0.0.0.0:{}", port);
    
    // Start TCP server
    let listener = TcpListener::bind(&addr).await?;
    info!("WMS TCP server listening on {}", addr);

    // Accept connections
    loop {
        match listener.accept().await {
            Ok((socket, _)) => {
                let db_clone = db.clone();
                tokio::spawn(async move {
                    handle_connection(socket, db_clone).await;
                });
            }
            Err(e) => {
                error!("Failed to accept connection: {}", e);
            }
        }
    }
}
