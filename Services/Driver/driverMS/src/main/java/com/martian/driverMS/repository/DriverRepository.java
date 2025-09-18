package com.martian.driverMS.repository;

import com.martian.driverMS.model.Driver;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface DriverRepository extends JpaRepository<Driver, Long> {
    
    // Find drivers by availability status
    List<Driver> findByAvailabilityStatus(Driver.AvailabilityStatus availabilityStatus);
    
    // Find drivers by delivery status
    List<Driver> findByDeliveryStatus(Driver.DeliveryStatus deliveryStatus);
    
    // Find drivers by vehicle type
    List<Driver> findByVehicleType(String vehicleType);
    
    // Find drivers by current location
    List<Driver> findByCurrentLocation(String currentLocation);
    
    // Find available drivers (availability status = AVAILABLE)
    List<Driver> findByAvailabilityStatusAndDeliveryStatus(
        Driver.AvailabilityStatus availabilityStatus, 
        Driver.DeliveryStatus deliveryStatus
    );
}
