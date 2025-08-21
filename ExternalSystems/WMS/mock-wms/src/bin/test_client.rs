use serde::{Deserialize, Serialize};
use std::env;
use std::io::{Read, Write};
use std::net::TcpStream;
use std::time::Duration;

#[derive(Serialize, Deserialize, Debug)]
struct DispatchItem {
    item_id: u32,
    quantity: u32,
}

#[derive(Serialize, Deserialize, Debug)]
struct DispatchRequest {
    order_id: u32,
    items: Vec<DispatchItem>,
}

fn main() {
    // Get command line arguments
    let args: Vec<String> = env::args().collect();
    if args.len() < 2 {
        println!("Usage: {} <order_id> [item_id:quantity ...]", args[0]);
        println!("Example: {} 1001 1:2 2:1", args[0]);
        return;
    }

    // Parse order ID
    let order_id = match args[1].parse::<u32>() {
        Ok(id) => id,
        Err(_) => {
            println!("Invalid order ID: {}", args[1]);
            return;
        }
    };

    // Parse items
    let mut items = Vec::new();
    for arg in &args[2..] {
        let parts: Vec<&str> = arg.split(':').collect();
        if parts.len() != 2 {
            println!(
                "Invalid item format: {}, expected format: item_id:quantity",
                arg
            );
            continue;
        }

        let item_id = match parts[0].parse::<u32>() {
            Ok(id) => id,
            Err(_) => {
                println!("Invalid item ID: {}", parts[0]);
                continue;
            }
        };

        let quantity = match parts[1].parse::<u32>() {
            Ok(q) => q,
            Err(_) => {
                println!("Invalid quantity: {}", parts[1]);
                continue;
            }
        };

        items.push((item_id, quantity));
    }

    if items.is_empty() {
        println!("No valid items provided");
        return;
    }

    // Build request using serde structs
    let mut dispatch_items = Vec::new();
    for (item_id, quantity) in items.iter() {
        dispatch_items.push(DispatchItem {
            item_id: *item_id,
            quantity: *quantity,
        });
    }

    let request = DispatchRequest {
        order_id,
        items: dispatch_items,
    };

    // Serialize to JSON
    let json = serde_json::to_string(&request).unwrap();
    println!("Sending request: {}", json);

    // Connect to the server
    let hostname = env::var("WMS_HOST").unwrap_or_else(|_| "localhost".to_string());
    let port = env::var("WMS_PORT").unwrap_or_else(|_| "5000".to_string());
    let addr = format!("{}:{}", hostname, port);

    match TcpStream::connect(&addr) {
        Ok(mut stream) => {
            println!("Connected to {}", addr);

            // Set timeouts
            stream
                .set_read_timeout(Some(Duration::from_secs(5)))
                .unwrap();
            stream
                .set_write_timeout(Some(Duration::from_secs(5)))
                .unwrap();

            // Send the request with a newline at the end to complete the message
            let json_with_newline = format!("{}\n", json);
            match stream.write_all(json_with_newline.as_bytes()) {
                Ok(_) => {
                    println!("Request sent successfully");
                    stream
                        .flush()
                        .unwrap_or_else(|e| println!("Failed to flush: {}", e));
                }
                Err(e) => {
                    println!("Failed to send request: {}", e);
                    return;
                }
            }

            // Read the response
            let mut buffer = [0; 1024];
            match stream.read(&mut buffer) {
                Ok(n) => {
                    if n == 0 {
                        println!("Server closed the connection without sending a response");
                    } else {
                        let response = String::from_utf8_lossy(&buffer[0..n]);
                        println!("Received response: {}", response);
                    }
                }
                Err(e) => {
                    println!("Failed to receive response: {}", e);
                }
            }
        }
        Err(e) => {
            println!("Failed to connect to {}: {}", addr, e);
        }
    }
}
