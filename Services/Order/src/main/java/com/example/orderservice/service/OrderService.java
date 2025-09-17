package com.example.orderservice.service;

import com.example.orderservice.model.Order;
import com.example.orderservice.repository.OrderRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class OrderService {

    @Autowired
    private OrderRepository orderRepository;

    // Create order
    public Order create(Order order) {
        return orderRepository.save(order);
    }

    // Get order by ID
    public Order getById(Long id) {
        return orderRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Order not found with id: " + id));
    }

    // Get all orders
    public List<Order> getAll() {
        return orderRepository.findAll();
    }

    // Update order
    public Order update(Long id, Order orderDetails) {
        Order existingOrder = getById(id);

        // Update only mutable fields
        existingOrder.setDestinationAddress(orderDetails.getDestinationAddress());
        existingOrder.setWeight(orderDetails.getWeight());
        existingOrder.setDeliveryStatus(orderDetails.getDeliveryStatus());
        existingOrder.setStatusMessage(orderDetails.getStatusMessage());
        existingOrder.setPhoneNo(orderDetails.getPhoneNo());
        existingOrder.setTrackingNo(orderDetails.getTrackingNo());

        return orderRepository.save(existingOrder);
    }

    // Delete order
    public void delete(Long id) {
        Order order = getById(id);
        orderRepository.delete(order);
    }
}
