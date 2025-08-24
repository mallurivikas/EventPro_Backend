#!/usr/bin/env python3
"""
Automatic Ticket Booking Simulation Script for EventPro
This script simulates real-time ticket purchases with random user data
"""

import json
import random
import time
import requests
from datetime import datetime, timedelta
from faker import Faker
import csv
import os

# Initialize Faker for generating random user data
fake = Faker()

class TicketBookingSimulator:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.bookings = []
        self.total_revenue = 0
        
    def generate_random_attendee(self):
        """Generate random attendee data"""
        return {
            "name": fake.name(),
            "email": fake.email(),
            "phone": fake.phone_number(),
            "age": random.randint(18, 65),
            "city": fake.city(),
            "purchase_time": datetime.now().isoformat(),
            "payment_method": random.choice(["Credit Card", "Debit Card", "UPI", "Net Banking"]),
            "referral_source": random.choice(["Social Media", "Email", "Website", "Word of Mouth", "Advertisement"])
        }
    
    def book_ticket(self, event_id, ticket_price=250000, currency="INR"):
        """Simulate a single ticket booking"""
        attendee = self.generate_random_attendee()
        
        booking = {
            "id": len(self.bookings) + 1,
            "event_id": event_id,
            "attendee": attendee,
            "ticket_price": ticket_price,
            "currency": currency,
            "booking_time": datetime.now(),
            "status": "confirmed"
        }
        
        self.bookings.append(booking)
        self.total_revenue += ticket_price
        
        print(f"✅ Ticket booked for {attendee['name']} ({attendee['email']}) - {currency} {ticket_price:,}")
        return booking
    
    def simulate_booking_burst(self, event_id, num_bookings=10, delay_range=(1, 5)):
        """Simulate a burst of ticket bookings"""
        print(f"\n🚀 Starting booking simulation for Event {event_id}...")
        print(f"📊 Simulating {num_bookings} ticket purchases...")
        
        for i in range(num_bookings):
            # Random delay between bookings
            delay = random.uniform(delay_range[0], delay_range[1])
            time.sleep(delay)
            
            # Random ticket price variation (±20%)
            base_price = 250000
            variation = random.uniform(0.8, 1.2)
            ticket_price = int(base_price * variation)
            
            booking = self.book_ticket(event_id, ticket_price)
            
            # Show progress
            progress = (i + 1) / num_bookings * 100
            print(f"Progress: {progress:.1f}% | Total Revenue: INR {self.total_revenue:,}")
    
    def export_to_csv(self, filename=None):
        """Export booking data to CSV"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ticket_bookings_{timestamp}.csv"
        
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'booking_id', 'event_id', 'attendee_name', 'attendee_email', 
                'attendee_phone', 'attendee_age', 'attendee_city', 
                'ticket_price', 'currency', 'booking_time', 'payment_method', 
                'referral_source', 'status'
            ]
            
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            for booking in self.bookings:
                writer.writerow({
                    'booking_id': booking['id'],
                    'event_id': booking['event_id'],
                    'attendee_name': booking['attendee']['name'],
                    'attendee_email': booking['attendee']['email'],
                    'attendee_phone': booking['attendee']['phone'],
                    'attendee_age': booking['attendee']['age'],
                    'attendee_city': booking['attendee']['city'],
                    'ticket_price': booking['ticket_price'],
                    'currency': booking['currency'],
                    'booking_time': booking['booking_time'].strftime("%Y-%m-%d %H:%M:%S"),
                    'payment_method': booking['attendee']['payment_method'],
                    'referral_source': booking['attendee']['referral_source'],
                    'status': booking['status']
                })
        
        print(f"\n📊 Booking data exported to: {filepath}")
        return filepath
    
    def get_booking_stats(self):
        """Get booking statistics"""
        if not self.bookings:
            return {"message": "No bookings yet"}
        
        cities = [booking['attendee']['city'] for booking in self.bookings]
        payment_methods = [booking['attendee']['payment_method'] for booking in self.bookings]
        referral_sources = [booking['attendee']['referral_source'] for booking in self.bookings]
        
        return {
            "total_bookings": len(self.bookings),
            "total_revenue": self.total_revenue,
            "average_ticket_price": self.total_revenue / len(self.bookings),
            "top_cities": {city: cities.count(city) for city in set(cities)},
            "payment_method_breakdown": {method: payment_methods.count(method) for method in set(payment_methods)},
            "referral_source_breakdown": {source: referral_sources.count(source) for source in set(referral_sources)},
            "booking_timeframe": {
                "first_booking": min(booking['booking_time'] for booking in self.bookings),
                "last_booking": max(booking['booking_time'] for booking in self.bookings)
            }
        }
    
    def continuous_simulation(self, event_id, duration_minutes=30, bookings_per_minute=2):
        """Run continuous booking simulation"""
        print(f"\n🔄 Starting continuous simulation for {duration_minutes} minutes...")
        print(f"📈 Target: {bookings_per_minute} bookings per minute")
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            # Book multiple tickets in this cycle
            for _ in range(bookings_per_minute):
                base_price = random.choice([200000, 250000, 300000, 350000])  # Different ticket tiers
                variation = random.uniform(0.9, 1.1)
                ticket_price = int(base_price * variation)
                
                self.book_ticket(event_id, ticket_price)
                
                # Small delay between individual bookings
                time.sleep(random.uniform(0.5, 2))
            
            # Wait for next minute cycle
            time.sleep(random.uniform(20, 40))
            
            # Show current stats
            stats = self.get_booking_stats()
            print(f"\n📊 Current Stats: {stats['total_bookings']} bookings | INR {stats['total_revenue']:,} revenue")

def main():
    print("🎫 EventPro Ticket Booking Simulator")
    print("=" * 50)
    
    # Initialize simulator
    simulator = TicketBookingSimulator()
    
    try:
        while True:
            print("\nChoose simulation mode:")
            print("1. Quick burst (10 bookings)")
            print("2. Medium burst (25 bookings)")
            print("3. Large burst (50 bookings)")
            print("4. Continuous simulation (30 minutes)")
            print("5. Custom simulation")
            print("6. Export current data to CSV")
            print("7. Show booking statistics")
            print("8. Exit")
            
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == "1":
                event_id = input("Enter Event ID (default: 1): ").strip() or "1"
                simulator.simulate_booking_burst(event_id, 10, (0.5, 2))
                
            elif choice == "2":
                event_id = input("Enter Event ID (default: 1): ").strip() or "1"
                simulator.simulate_booking_burst(event_id, 25, (0.3, 1.5))
                
            elif choice == "3":
                event_id = input("Enter Event ID (default: 1): ").strip() or "1"
                simulator.simulate_booking_burst(event_id, 50, (0.2, 1))
                
            elif choice == "4":
                event_id = input("Enter Event ID (default: 1): ").strip() or "1"
                duration = int(input("Enter duration in minutes (default: 30): ").strip() or "30")
                rate = int(input("Enter bookings per minute (default: 2): ").strip() or "2")
                simulator.continuous_simulation(event_id, duration, rate)
                
            elif choice == "5":
                event_id = input("Enter Event ID (default: 1): ").strip() or "1"
                num_bookings = int(input("Enter number of bookings: "))
                min_delay = float(input("Enter minimum delay between bookings (seconds): "))
                max_delay = float(input("Enter maximum delay between bookings (seconds): "))
                simulator.simulate_booking_burst(event_id, num_bookings, (min_delay, max_delay))
                
            elif choice == "6":
                filename = input("Enter filename (leave blank for auto-generated): ").strip()
                simulator.export_to_csv(filename if filename else None)
                
            elif choice == "7":
                stats = simulator.get_booking_stats()
                print("\n📊 Booking Statistics:")
                print(json.dumps(stats, indent=2, default=str))
                
            elif choice == "8":
                # Auto-export before exit
                if simulator.bookings:
                    print("\n💾 Auto-exporting data before exit...")
                    simulator.export_to_csv()
                print("👋 Thanks for using EventPro Ticket Booking Simulator!")
                break
                
            else:
                print("❌ Invalid choice. Please try again.")
                
    except KeyboardInterrupt:
        print("\n\n⏹️ Simulation stopped by user.")
        if simulator.bookings:
            print("💾 Auto-exporting data...")
            simulator.export_to_csv()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if simulator.bookings:
            print("💾 Auto-exporting data...")
            simulator.export_to_csv()

if __name__ == "__main__":
    main()