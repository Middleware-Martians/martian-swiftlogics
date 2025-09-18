package com.martian.driverMS.controller;

import com.martian.driverMS.model.Driver;
import com.martian.driverMS.service.DriverService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/drivers")
@CrossOrigin(origins = "*")
public class DriverController {

    @Autowired
    private DriverService driverService;

    // Get all drivers
    @GetMapping
    public ResponseEntity<List<Driver>> getAllDrivers() {
        return ResponseEntity.ok(driverService.getAllDrivers());
    }

    // Get driver by ID
    @GetMapping("/{id}")
    public ResponseEntity<Driver> getDriverById(@PathVariable Long id) {
        Driver driver = driverService.getDriverById(id);
        if (driver != null) {
            return ResponseEntity.ok(driver);
        }
        return ResponseEntity.notFound().build();
    }

    // Add new driver
    @PostMapping
    public ResponseEntity<Driver> addDriver(@RequestBody Driver driver) {
        try {
            Driver savedDriver = driverService.saveDriver(driver);
            return ResponseEntity.ok(savedDriver);
        } catch (Exception e) {
            return ResponseEntity.badRequest().build();
        }
    }

    // Update driver
    @PutMapping("/{id}")
    public ResponseEntity<Driver> updateDriver(@PathVariable Long id, @RequestBody Driver driverDetails) {
        Driver updatedDriver = driverService.updateDriver(id, driverDetails);
        if (updatedDriver != null) {
            return ResponseEntity.ok(updatedDriver);
        }
        return ResponseEntity.notFound().build();
    }

    // Delete driver
    @DeleteMapping("/{id}")
    public ResponseEntity<String> deleteDriver(@PathVariable Long id) {
        String result = driverService.deleteDriver(id);
        return ResponseEntity.ok(result);
    }

    // Health check
    @GetMapping("/health")
    public ResponseEntity<String> healthCheck() {
        return ResponseEntity.ok("Driver service is running!");
    }

    // Update driver availability status
    @PutMapping("/{id}/availability")
    public ResponseEntity<Driver> updateAvailabilityStatus(@PathVariable Long id, 
                                                          @RequestParam String status) {
        try {
            Driver.AvailabilityStatus availabilityStatus = Driver.AvailabilityStatus.valueOf(status.toUpperCase());
            Driver updatedDriver = driverService.updateAvailabilityStatus(id, availabilityStatus);
            if (updatedDriver != null) {
                return ResponseEntity.ok(updatedDriver);
            }
            return ResponseEntity.notFound().build();
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    // Update driver delivery status
    @PutMapping("/{id}/delivery-status")
    public ResponseEntity<Driver> updateDeliveryStatus(@PathVariable Long id, 
                                                      @RequestParam String status) {
        try {
            Driver.DeliveryStatus deliveryStatus = Driver.DeliveryStatus.valueOf(status.toUpperCase());
            Driver updatedDriver = driverService.updateDeliveryStatus(id, deliveryStatus);
            if (updatedDriver != null) {
                return ResponseEntity.ok(updatedDriver);
            }
            return ResponseEntity.notFound().build();
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    // Get drivers by availability status
    @GetMapping("/availability/{status}")
    public ResponseEntity<List<Driver>> getDriversByAvailability(@PathVariable String status) {
        try {
            Driver.AvailabilityStatus availabilityStatus = Driver.AvailabilityStatus.valueOf(status.toUpperCase());
            List<Driver> drivers = driverService.getDriversByAvailabilityStatus(availabilityStatus);
            return ResponseEntity.ok(drivers);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    // Get drivers by delivery status
    @GetMapping("/delivery-status/{status}")
    public ResponseEntity<List<Driver>> getDriversByDeliveryStatus(@PathVariable String status) {
        try {
            Driver.DeliveryStatus deliveryStatus = Driver.DeliveryStatus.valueOf(status.toUpperCase());
            List<Driver> drivers = driverService.getDriversByDeliveryStatus(deliveryStatus);
            return ResponseEntity.ok(drivers);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().build();
        }
    }

    // Update driver location
    @PutMapping("/{id}/location")
    public ResponseEntity<Driver> updateLocation(@PathVariable Long id, 
                                                @RequestParam String location) {
        Driver updatedDriver = driverService.updateLocation(id, location);
        if (updatedDriver != null) {
            return ResponseEntity.ok(updatedDriver);
        }
        return ResponseEntity.notFound().build();
    }
}
