FROM rust:1.74-slim as builder

WORKDIR /app

# Copy Cargo.toml and Cargo.lock
COPY Cargo.toml ./

# Create a dummy main.rs to build dependencies
RUN mkdir -p src && echo 'fn main() { println!("Dummy!"); }' > src/main.rs

# Build dependencies
RUN cargo build --release

# Remove the dummy source code
RUN rm -rf src

# Copy the actual source code
COPY src ./src

# Build the application with the actual source code
RUN touch src/main.rs && cargo build --release

# Final image
FROM debian:bullseye-slim

# Install required libraries
RUN apt-get update && apt-get install -y libssl-dev ca-certificates && rm -rf /var/lib/apt/lists/*

# Copy the binary from the builder
COPY --from=builder /app/target/release/mock-wms /usr/local/bin/

# Expose TCP and HTTP ports
EXPOSE 5000
EXPOSE 5001

# Environment variables
ENV RUST_LOG=info
ENV WMS_PORT=5000

# Run the binary
CMD ["mock-wms"]
