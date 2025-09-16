package com.martian.driverMS.service;

import com.martian.driverMS.model.Driver;
import com.martian.driverMS.repository.DriverRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class DriverService {

    private final DriverRepository repository;

    public DriverService(DriverRepository repository) {
        this.repository = repository;
    }

    public List<Driver> getAllDrivers() {
        return repository.findAll();
    }

    public Driver getDriverById(Long id) {
        return repository.findById(id).orElse(null);
    }

    public Driver saveDriver(Driver driver) {
        return repository.save(driver);
    }

    public Driver updateDriver(Long id, Driver driverDetails) {
        return repository.findById(id).map(driver -> {
            driver.setName(driverDetails.getName());
            driver.setLicenseNumber(driverDetails.getLicenseNumber());
            driver.setPhoneNumber(driverDetails.getPhoneNumber());
            if (driverDetails.getAvailabilityStatus() != null) {
                driver.setAvailabilityStatus(driverDetails.getAvailabilityStatus());
            }
            if (driverDetails.getDeliveryStatus() != null) {
                driver.setDeliveryStatus(driverDetails.getDeliveryStatus());
            }
            if (driverDetails.getCurrentLocation() != null) {
                driver.setCurrentLocation(driverDetails.getCurrentLocation());
            }
            if (driverDetails.getVehicleType() != null) {
                driver.setVehicleType(driverDetails.getVehicleType());
            }
            if (driverDetails.getVehicleNumber() != null) {
                driver.setVehicleNumber(driverDetails.getVehicleNumber());
            }
            return repository.save(driver);
        }).orElse(null);
    }

    public String deleteDriver(Long id) {
        repository.deleteById(id);
        return "Driver deleted successfully!";
    }
    
    // New methods for status management
    public Driver updateAvailabilityStatus(Long id, Driver.AvailabilityStatus status) {
        return repository.findById(id).map(driver -> {
            driver.setAvailabilityStatus(status);
            return repository.save(driver);
        }).orElse(null);
    }
    
    public Driver updateDeliveryStatus(Long id, Driver.DeliveryStatus status) {
        return repository.findById(id).map(driver -> {
            driver.setDeliveryStatus(status);
            return repository.save(driver);
        }).orElse(null);
    }
    
    public Driver updateLocation(Long id, String location) {
        return repository.findById(id).map(driver -> {
            driver.setCurrentLocation(location);
            return repository.save(driver);
        }).orElse(null);
    }
    
    public List<Driver> getDriversByAvailabilityStatus(Driver.AvailabilityStatus status) {
        return repository.findByAvailabilityStatus(status);
    }
    
    public List<Driver> getDriversByDeliveryStatus(Driver.DeliveryStatus status) {
        return repository.findByDeliveryStatus(status);
    }
}
