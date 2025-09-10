import React, { useState, useEffect } from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";

interface OrderDetails {
  id: string;
  trackingNumber: string;
  status: "pending" | "processing" | "in_transit" | "delivered" | "failed";
  recipientName: string;
  recipientPhone: string;
  deliveryAddress: string;
  city: string;
  postalCode: string;
  packageDescription: string;
  packageWeight: number;
  packageValue: number;
  priority: string;
  submittedDate: string;
  estimatedDelivery: string;
  actualDelivery?: string;
  deliveryInstructions: string;
  trackingHistory: TrackingEvent[];
}

interface TrackingEvent {
  timestamp: string;
  status: string;
  location: string;
  description: string;
}

export default function OrderTracking() {
  const { orderId } = useParams<{ orderId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const [order, setOrder] = useState<OrderDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Success message from order submission
  const successMessage = location.state?.message;

  useEffect(() => {
    // Mock API call - replace with real API
    setTimeout(() => {
      if (orderId) {
        // Mock order data
        const mockOrder: OrderDetails = {
          id: orderId,
          trackingNumber: "SW12345678",
          status: "in_transit",
          recipientName: "John Doe",
          recipientPhone: "+94 77 123 4567",
          deliveryAddress: "123 Main Street, Apartment 4B",
          city: "Colombo",
          postalCode: "00100",
          packageDescription: "Electronics - Mobile phone accessories",
          packageWeight: 0.5,
          packageValue: 15000,
          priority: "express",
          submittedDate: "2025-09-08T10:30:00Z",
          estimatedDelivery: "2025-09-12T18:00:00Z",
          deliveryInstructions: "Please call before delivery. Leave with security if not available.",
          trackingHistory: [
            {
              timestamp: "2025-09-08T10:30:00Z",
              status: "Order Received",
              location: "Online Portal",
              description: "Order submitted and confirmed"
            },
            {
              timestamp: "2025-09-08T14:20:00Z",
              status: "Processing",
              location: "Warehouse - Colombo",
              description: "Package prepared and labeled"
            },
            {
              timestamp: "2025-09-09T08:15:00Z",
              status: "Out for Pickup",
              location: "Warehouse - Colombo", 
              description: "Package assigned to driver"
            },
            {
              timestamp: "2025-09-09T11:45:00Z",
              status: "In Transit",
              location: "Distribution Center - Mount Lavinia",
              description: "Package in transit to destination area"
            },
            {
              timestamp: "2025-09-10T09:30:00Z",
              status: "Out for Delivery",
              location: "Local Hub - Colombo 03",
              description: "Package loaded for final delivery"
            }
          ]
        };
        setOrder(mockOrder);
      } else {
        setError("Order ID not found");
      }
      setLoading(false);
    }, 1000);
  }, [orderId]);

  const getStatusColor = (status: string) => {
    const statusLower = status.toLowerCase();
    if (statusLower.includes("delivered")) return "text-green-600";
    if (statusLower.includes("transit") || statusLower.includes("delivery")) return "text-blue-600";
    if (statusLower.includes("processing") || statusLower.includes("pickup")) return "text-yellow-600";
    if (statusLower.includes("failed") || statusLower.includes("error")) return "text-red-600";
    return "text-gray-600";
  };

  const getStatusIcon = (status: string) => {
    const statusLower = status.toLowerCase();
    if (statusLower.includes("delivered")) {
      return (
        <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
          <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
          </svg>
        </div>
      );
    }
    if (statusLower.includes("transit") || statusLower.includes("delivery")) {
      return (
        <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
          </svg>
        </div>
      );
    }
    return (
      <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
        <svg className="w-5 h-5 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <svg className="w-8 h-8 animate-spin mx-auto mb-4" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" className="opacity-30"/>
            <path d="M4 12a8 8 0 018-8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" className="opacity-80"/>
          </svg>
          <p className="text-gray-600">Loading order details...</p>
        </div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error || "Order not found"}</p>
          <button
            onClick={() => navigate("/dashboard")}
            className="text-indigo-600 hover:text-indigo-800"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <button 
                onClick={() => navigate("/dashboard")}
                className="text-indigo-600 hover:text-indigo-800 mr-4"
              >
                ← Back to Dashboard
              </button>
              <h1 className="text-xl font-semibold text-gray-900">Order Tracking</h1>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Success Message */}
        {successMessage && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <div className="flex">
              <svg className="w-5 h-5 text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
              <p className="ml-3 text-sm text-green-700">{successMessage}</p>
            </div>
          </div>
        )}

        {/* Order Overview */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="p-6">
            <div className="flex justify-between items-start mb-4">
              <div>
                <h2 className="text-lg font-semibold text-gray-900">Order #{order.id}</h2>
                <p className="text-sm text-gray-600">Tracking Number: {order.trackingNumber}</p>
              </div>
              <span className={`inline-flex px-3 py-1 text-sm font-semibold rounded-full ${
                order.status === "delivered" ? "bg-green-100 text-green-800" :
                order.status === "in_transit" ? "bg-blue-100 text-blue-800" :
                order.status === "processing" ? "bg-yellow-100 text-yellow-800" :
                "bg-gray-100 text-gray-800"
              }`}>
                {order.status.replace("_", " ").toUpperCase()}
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Delivery Information</h3>
                <p className="text-sm text-gray-600">
                  <strong>Recipient:</strong> {order.recipientName}<br/>
                  <strong>Phone:</strong> {order.recipientPhone}<br/>
                  <strong>Address:</strong> {order.deliveryAddress}, {order.city} {order.postalCode}
                </p>
              </div>
              
              <div>
                <h3 className="font-medium text-gray-900 mb-2">Package Details</h3>
                <p className="text-sm text-gray-600">
                  <strong>Description:</strong> {order.packageDescription}<br/>
                  <strong>Weight:</strong> {order.packageWeight}kg<br/>
                  <strong>Value:</strong> LKR {order.packageValue.toLocaleString()}<br/>
                  <strong>Priority:</strong> {order.priority.toUpperCase()}
                </p>
              </div>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <p className="text-sm text-gray-600">
                    <strong>Submitted:</strong> {new Date(order.submittedDate).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">
                    <strong>Estimated Delivery:</strong> {new Date(order.estimatedDelivery).toLocaleString()}
                  </p>
                </div>
              </div>
              
              {order.deliveryInstructions && (
                <div className="mt-4">
                  <p className="text-sm text-gray-600">
                    <strong>Delivery Instructions:</strong> {order.deliveryInstructions}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Tracking Timeline */}
        <div className="bg-white rounded-lg shadow">
          <div className="p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-6">Tracking History</h3>
            <div className="space-y-6">
              {order.trackingHistory.map((event, index) => (
                <div key={index} className="flex">
                  <div className="flex-shrink-0">
                    {getStatusIcon(event.status)}
                  </div>
                  <div className="ml-4 flex-grow">
                    <div className="flex justify-between items-start">
                      <div>
                        <p className={`font-medium ${getStatusColor(event.status)}`}>
                          {event.status}
                        </p>
                        <p className="text-sm text-gray-600 mt-1">{event.description}</p>
                        <p className="text-xs text-gray-500 mt-1">{event.location}</p>
                      </div>
                      <p className="text-xs text-gray-500">
                        {new Date(event.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Real-time Updates Notice */}
        <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex">
            <svg className="w-5 h-5 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="ml-3 text-sm text-blue-700">
              This page automatically updates with real-time tracking information. You'll receive notifications for any status changes.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
