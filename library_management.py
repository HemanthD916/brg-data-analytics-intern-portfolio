"""
Library Management System - Python OOP Demonstration
Demonstrating inheritance, polymorphism, and data management skills
"""

import json
import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum

class ItemStatus(Enum):
    AVAILABLE = "Available"
    CHECKED_OUT = "Checked Out"
    RESERVED = "Reserved"
    DAMAGED = "Damaged"
    LOST = "Lost"

class NotificationType(Enum):
    OVERDUE = "Overdue"
    RESERVATION = "Reservation Ready"
    FINE = "Fine Applied"
    GENERAL = "General"

@dataclass
class Notification:
    notification_id: int
    user_id: int
    message: str
    notification_type: NotificationType
    timestamp: datetime.datetime
    is_read: bool = False

class Person(ABC):
    """Abstract base class for all library persons"""
    def __init__(self, person_id: int, name: str, email: str):
        self.person_id = person_id
        self.name = name
        self.email = email
        self.join_date = datetime.datetime.now()
        
    @abstractmethod
    def display_info(self) -> str:
        pass

class Patron(Person):
    """Library patron/user class"""
    def __init__(self, patron_id: int, name: str, email: str, membership_level: str = "Standard"):
        super().__init__(patron_id, name, email)
        self.membership_level = membership_level
        self.checked_out_items = []
        self.reserved_items = []
        self.fines = 0.0
        self.borrowing_history = []
        self.notifications = []
        
    def display_info(self) -> str:
        return f"Patron: {self.name} (ID: {self.person_id}) - Membership: {self.membership_level}"
    
    def checkout_item(self, item) -> bool:
        if len(self.checked_out_items) < self.get_max_checkouts():
            self.checked_out_items.append(item)
            self.borrowing_history.append({
                'item_id': item.item_id,
                'title': item.title,
                'checkout_date': datetime.datetime.now(),
                'due_date': datetime.datetime.now() + datetime.timedelta(days=item.checkout_period)
            })
            return True
        return False
    
    def get_max_checkouts(self) -> int:
        limits = {
            "Standard": 5,
            "Premium": 10,
            "Student": 3,
            "Faculty": 15
        }
        return limits.get(self.membership_level, 5)
    
    def add_notification(self, message: str, notification_type: NotificationType):
        notification = Notification(
            notification_id=len(self.notifications) + 1,
            user_id=self.person_id,
            message=message,
            notification_type=notification_type,
            timestamp=datetime.datetime.now()
        )
        self.notifications.append(notification)
        return notification

class Librarian(Person):
    """Library staff member class"""
    def __init__(self, staff_id: int, name: str, email: str, department: str):
        super().__init__(staff_id, name, email)
        self.department = department
        self.employee_id = f"LIB{staff_id:04d}"
        self.permissions = ["check_in", "check_out", "manage_catalog", "process_fines"]
        
    def display_info(self) -> str:
        return f"Librarian: {self.name} - Department: {self.department} (ID: {self.employee_id})"
    
    def process_checkout(self, patron: Patron, item) -> bool:
        if patron.checkout_item(item):
            item.checkout(patron.person_id)
            return True
        return False
    
    def process_checkin(self, item, condition: str = "Good") -> float:
        fine = item.checkin(condition)
        return fine
    
    def add_item_to_catalog(self, catalog, item) -> bool:
        return catalog.add_item(item)
    
    def generate_report(self, catalog, report_type: str = "inventory") -> Dict:
        if report_type == "inventory":
            return catalog.get_inventory_report()
        elif report_type == "popular_items":
            return catalog.get_popular_items_report()
        elif report_type == "overdue_items":
            return catalog.get_overdue_items_report()
        return {}

class LibraryItem(ABC):
    """Abstract base class for all library items"""
    def __init__(self, item_id: int, title: str, category: str):
        self.item_id = item_id
        self.title = title
        self.category = category
        self.status = ItemStatus.AVAILABLE
        self.checkout_count = 0
        self.checkout_history = []
        self.current_patron = None
        self.due_date = None
        self.reservation_queue = []
        self.added_date = datetime.datetime.now()
        
    @abstractmethod
    def get_checkout_period(self) -> int:
        """Return checkout period in days"""
        pass
    
    @abstractmethod
    def calculate_fine(self, days_overdue: int) -> float:
        """Calculate fine for overdue item"""
        pass
    
    @property
    def checkout_period(self) -> int:
        return self.get_checkout_period()
    
    def checkout(self, patron_id: int) -> bool:
        if self.status == ItemStatus.AVAILABLE:
            self.status = ItemStatus.CHECKED_OUT
            self.current_patron = patron_id
            self.checkout_count += 1
            self.due_date = datetime.datetime.now() + datetime.timedelta(days=self.checkout_period)
            self.checkout_history.append({
                'patron_id': patron_id,
                'checkout_date': datetime.datetime.now(),
                'due_date': self.due_date
            })
            return True
        return False
    
    def checkin(self, condition: str = "Good") -> float:
        self.status = ItemStatus.AVAILABLE
        fine = 0.0
        
        if self.due_date and datetime.datetime.now() > self.due_date:
            days_overdue = (datetime.datetime.now() - self.due_date).days
            fine = self.calculate_fine(days_overdue)
        
        self.current_patron = None
        self.due_date = None
        
        # Process next reservation if any
        if self.reservation_queue:
            next_patron = self.reservation_queue.pop(0)
            # In a real system, you would notify the patron
            print(f"Item {self.item_id} is now available for {next_patron}")
        
        return fine
    
    def reserve(self, patron_id: int) -> bool:
        if patron_id not in self.reservation_queue:
            self.reservation_queue.append(patron_id)
            return True
        return False
    
    def get_item_info(self) -> Dict:
        return {
            'item_id': self.item_id,
            'title': self.title,
            'category': self.category,
            'status': self.status.value,
            'checkout_count': self.checkout_count,
            'current_patron': self.current_patron,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'reservation_count': len(self.reservation_queue)
        }

class Book(LibraryItem):
    """Book item class"""
    def __init__(self, item_id: int, title: str, author: str, isbn: str, 
                 category: str = "General", edition: int = 1):
        super().__init__(item_id, title, category)
        self.author = author
        self.isbn = isbn
        self.edition = edition
        self.page_count = 0
        self.publisher = ""
        self.publication_year = datetime.datetime.now().year
        
    def get_checkout_period(self) -> int:
        return 21  # 3 weeks for books
    
    def calculate_fine(self, days_overdue: int) -> float:
        return days_overdue * 0.25  # $0.25 per day
    
    def get_book_info(self) -> Dict:
        info = self.get_item_info()
        info.update({
            'author': self.author,
            'isbn': self.isbn,
            'edition': self.edition,
            'type': 'Book'
        })
        return info

class DVD(LibraryItem):
    """DVD item class"""
    def __init__(self, item_id: int, title: str, director: str, 
                 category: str = "Entertainment", runtime: int = 0):
        super().__init__(item_id, title, category)
        self.director = director
        self.runtime = runtime  # in minutes
        self.format = "DVD"
        self.rating = "NR"
        self.release_year = datetime.datetime.now().year
        
    def get_checkout_period(self) -> int:
        return 7  # 1 week for DVDs
    
    def calculate_fine(self, days_overdue: int) -> float:
        return days_overdue * 1.00  # $1.00 per day
    
    def get_dvd_info(self) -> Dict:
        info = self.get_item_info()
        info.update({
            'director': self.director,
            'runtime': self.runtime,
            'format': self.format,
            'rating': self.rating,
            'type': 'DVD'
        })
        return info

class CD(Book):  # Inherits from Book since it shares many attributes
    """CD item class - demonstrates inheritance"""
    def __init__(self, item_id: int, title: str, artist: str, 
                 category: str = "Music", tracks: int = 0):
        # Call Book's init but override author with artist
        super().__init__(item_id, title, artist, "", category)
        self.artist = artist  # Override author
        self.tracks = tracks
        self.duration = 0  # in minutes
        self.format = "CD"
        
    def get_checkout_period(self) -> int:
        return 14  # 2 weeks for CDs
    
    def calculate_fine(self, days_overdue: int) -> float:
        return days_overdue * 0.50  # $0.50 per day
    
    def get_cd_info(self) -> Dict:
        info = self.get_item_info()
        info.update({
            'artist': self.artist,
            'tracks': self.tracks,
            'duration': self.duration,
            'format': self.format,
            'type': 'CD'
        })
        return info

class Catalog:
    """Main catalog management class"""
    def __init__(self):
        self.items = {}
        self.patrons = {}
        self.librarians = {}
        self.next_item_id = 1
        self.next_patron_id = 1
        self.next_staff_id = 1
        
    def add_item(self, item: LibraryItem) -> bool:
        if item.item_id not in self.items:
            self.items[item.item_id] = item
            return True
        return False
    
    def remove_item(self, item_id: int) -> bool:
        if item_id in self.items:
            del self.items[item_id]
            return True
        return False
    
    def search_items(self, search_term: str, search_by: str = "title") -> List[Dict]:
        results = []
        for item in self.items.values():
            if search_by == "title" and search_term.lower() in item.title.lower():
                results.append(item.get_item_info())
            elif search_by == "author" and hasattr(item, 'author'):
                if search_term.lower() in item.author.lower():
                    results.append(item.get_item_info())
            elif search_by == "category" and search_term.lower() in item.category.lower():
                results.append(item.get_item_info())
        return results
    
    def add_patron(self, name: str, email: str, membership_level: str = "Standard") -> Patron:
        patron = Patron(self.next_patron_id, name, email, membership_level)
        self.patrons[patron.person_id] = patron
        self.next_patron_id += 1
        return patron
    
    def add_librarian(self, name: str, email: str, department: str) -> Librarian:
        librarian = Librarian(self.next_staff_id, name, email, department)
        self.librarians[librarian.person_id] = librarian
        self.next_staff_id += 1
        return librarian
    
    def get_inventory_report(self) -> Dict:
        report = {
            'total_items': len(self.items),
            'available_items': sum(1 for item in self.items.values() 
                                 if item.status == ItemStatus.AVAILABLE),
            'checked_out_items': sum(1 for item in self.items.values() 
                                   if item.status == ItemStatus.CHECKED_OUT),
            'by_category': {},
            'by_type': {}
        }
        
        for item in self.items.values():
            # Count by category
            report['by_category'][item.category] = report['by_category'].get(item.category, 0) + 1
            
            # Count by type
            item_type = type(item).__name__
            report['by_type'][item_type] = report['by_type'].get(item_type, 0) + 1
        
        return report
    
    def get_popular_items_report(self, limit: int = 10) -> Dict:
        sorted_items = sorted(self.items.values(), 
                            key=lambda x: x.checkout_count, 
                            reverse=True)[:limit]
        
        return {
            'popular_items': [
                {
                    'title': item.title,
                    'checkout_count': item.checkout_count,
                    'type': type(item).__name__,
                    'category': item.category
                }
                for item in sorted_items
            ],
            'total_checkouts': sum(item.checkout_count for item in self.items.values())
        }
    
    def get_overdue_items_report(self) -> Dict:
        overdue_items = []
        total_fines = 0.0
        
        for item in self.items.values():
            if item.due_date and datetime.datetime.now() > item.due_date:
                days_overdue = (datetime.datetime.now() - item.due_date).days
                fine = item.calculate_fine(days_overdue)
                
                overdue_items.append({
                    'item_id': item.item_id,
                    'title': item.title,
                    'due_date': item.due_date.isoformat(),
                    'days_overdue': days_overdue,
                    'estimated_fine': fine,
                    'current_patron': item.current_patron
                })
                total_fines += fine
        
        return {
            'overdue_items': overdue_items,
            'total_items_overdue': len(overdue_items),
            'total_estimated_fines': total_fines
        }
    
    def save_to_file(self, filename: str = "library_data.json"):
        """Save catalog data to JSON file"""
        data = {
            'items': [],
            'patrons': [],
            'librarians': [],
            'next_ids': {
                'item': self.next_item_id,
                'patron': self.next_patron_id,
                'staff': self.next_staff_id
            }
        }
        
        for item in self.items.values():
            item_data = item.get_item_info()
            item_data['type'] = type(item).__name__
            
            # Add type-specific data
            if isinstance(item, Book):
                item_data.update({
                    'author': item.author,
                    'isbn': item.isbn,
                    'edition': item.edition
                })
            elif isinstance(item, DVD):
                item_data.update({
                    'director': item.director,
                    'runtime': item.runtime
                })
            elif isinstance(item, CD):
                item_data.update({
                    'artist': item.artist,
                    'tracks': item.tracks
                })
            
            data['items'].append(item_data)
        
        for patron in self.patrons.values():
            data['patrons'].append({
                'patron_id': patron.person_id,
                'name': patron.name,
                'email': patron.email,
                'membership_level': patron.membership_level,
                'fines': patron.fines
            })
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"Data saved to {filename}")
        return True
    
    def load_from_file(self, filename: str = "library_data.json"):
        """Load catalog data from JSON file"""
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Clear current data
            self.items.clear()
            self.patrons.clear()
            
            # Load items
            for item_data in data.get('items', []):
                item_type = item_data.pop('type', 'Book')
                
                if item_type == 'Book':
                    item = Book(
                        item_id=item_data['item_id'],
                        title=item_data['title'],
                        author=item_data.get('author', ''),
                        isbn=item_data.get('isbn', ''),
                        category=item_data.get('category', 'General')
                    )
                elif item_type == 'DVD':
                    item = DVD(
                        item_id=item_data['item_id'],
                        title=item_data['title'],
                        director=item_data.get('director', ''),
                        category=item_data.get('category', 'Entertainment'),
                        runtime=item_data.get('runtime', 0)
                    )
                elif item_type == 'CD':
                    item = CD(
                        item_id=item_data['item_id'],
                        title=item_data['title'],
                        artist=item_data.get('artist', ''),
                        category=item_data.get('category', 'Music'),
                        tracks=item_data.get('tracks', 0)
                    )
                else:
                    continue
                
                # Restore item state
                item.status = ItemStatus(item_data.get('status', 'Available'))
                item.checkout_count = item_data.get('checkout_count', 0)
                self.items[item.item_id] = item
            
            # Load IDs
            next_ids = data.get('next_ids', {})
            self.next_item_id = next_ids.get('item', 1)
            self.next_patron_id = next_ids.get('patron', 1)
            self.next_staff_id = next_ids.get('staff', 1)
            
            print(f"Data loaded from {filename}")
            return True
            
        except FileNotFoundError:
            print(f"File {filename} not found. Starting with empty catalog.")
            return False
        except Exception as e:
            print(f"Error loading data: {e}")
            return False

# Demonstration function
def demonstrate_library_system():
    """Demonstrate the library management system functionality"""
    print("=" * 60)
    print("LIBRARY MANAGEMENT SYSTEM DEMONSTRATION")
    print("=" * 60)
    
    # Create catalog
    catalog = Catalog()
    
    # Add some items demonstrating inheritance
    book1 = Book(1, "Python Data Science Handbook", "Jake VanderPlas", "9781491912058", "Technology")
    book1.page_count = 500
    book1.publisher = "O'Reilly"
    book1.publication_year = 2016
    
    dvd1 = DVD(2, "The Social Network", "David Fincher", "Biography", 120)
    dvd1.rating = "PG-13"
    dvd1.release_year = 2010
    
    cd1 = CD(3, "Random Access Memories", "Daft Punk", "Electronic", 13)
    cd1.duration = 74
    
    # Add items to catalog
    catalog.add_item(book1)
    catalog.add_item(dvd1)
    catalog.add_item(cd1)
    
    # Create patrons
    patron1 = catalog.add_patron("John Smith", "john@example.com", "Premium")
    patron2 = catalog.add_patron("Jane Doe", "jane@example.com", "Student")
    
    # Create librarian
    librarian = catalog.add_librarian("Sarah Johnson", "sarah@library.com", "Circulation")
    
    # Demonstrate checkout process
    print("\n1. CHECKOUT PROCESS:")
    print("-" * 40)
    
    # Librarian processes checkout
    if librarian.process_checkout(patron1, book1):
        print(f"✓ {patron1.name} checked out '{book1.title}'")
    else:
        print(f"✗ Could not check out '{book1.title}'")
    
    # Demonstrate item information
    print(f"\n2. ITEM INFORMATION:")
    print("-" * 40)
    print(f"Book: {book1.get_book_info()}")
    print(f"DVD: {dvd1.get_dvd_info()}")
    print(f"CD: {cd1.get_cd_info()}")
    
    # Demonstrate search functionality
    print(f"\n3. SEARCH FUNCTIONALITY:")
    print("-" * 40)
    tech_items = catalog.search_items("Technology", "category")
    print(f"Technology items: {len(tech_items)} found")
    
    # Demonstrate reporting
    print(f"\n4. ANALYTICS & REPORTING:")
    print("-" * 40)
    
    inventory_report = catalog.get_inventory_report()
    print(f"Total items in catalog: {inventory_report['total_items']}")
    print(f"Available items: {inventory_report['available_items']}")
    print(f"Checked out items: {inventory_report['checked_out_items']}")
    
    print(f"\nItems by category:")
    for category, count in inventory_report['by_category'].items():
        print(f"  {category}: {count}")
    
    print(f"\nItems by type (demonstrating polymorphism):")
    for item_type, count in inventory_report['by_type'].items():
        print(f"  {item_type}: {count}")
    
    # Demonstrate polymorphism
    print(f"\n5. POLYMORPHISM DEMONSTRATION:")
    print("-" * 40)
    
    items = [book1, dvd1, cd1]
    for item in items:
        print(f"{type(item).__name__} '{item.title}':")
        print(f"  Checkout period: {item.get_checkout_period()} days")
        print(f"  Overdue fine (5 days): ${item.calculate_fine(5):.2f}")
        print(f"  Status: {item.status.value}")
    
    # Check in book and calculate fine
    print(f"\n6. CHECKIN & FINE CALCULATION:")
    print("-" * 40)
    
    # Simulate overdue by setting due date in the past
    book1.due_date = datetime.datetime.now() - datetime.timedelta(days=10)
    fine = librarian.process_checkin(book1, "Good")
    print(f"Fine for overdue book: ${fine:.2f}")
    
    # Generate popular items report
    popular_report = catalog.get_popular_items_report()
    print(f"\n7. POPULAR ITEMS REPORT:")
    print("-" * 40)
    print(f"Total checkouts: {popular_report['total_checkouts']}")
    
    # Save data to file
    print(f"\n8. DATA PERSISTENCE:")
    print("-" * 40)
    catalog.save_to_file("library_demo.json")
    print("✓ Data saved to 'library_demo.json'")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)

# Run demonstration if script is executed directly
if __name__ == "__main__":
    demonstrate_library_system()
    
    # Additional interactive demonstration
    print("\n\nInteractive Demonstration:")
    print("-" * 40)
    
    # Create a fresh catalog for interaction
    interactive_catalog = Catalog()
    
    # Add some sample data
    interactive_catalog.add_item(Book(100, "Clean Code", "Robert Martin", "9780132350884", "Programming"))
    interactive_catalog.add_item(DVD(101, "The Imitation Game", "Morten Tyldum", "Biography", 114))
    
    # Create a patron
    patron = interactive_catalog.add_patron("Alex Johnson", "alex@example.com", "Standard")
    
    # Display available items
    print("\nAvailable items in catalog:")
    for item_id, item in interactive_catalog.items.items():
        if item.status == ItemStatus.AVAILABLE:
            print(f"  {item_id}: {item.title} ({type(item).__name__})")
    
    # Simple command-line interface
    while True:
        print("\nOptions:")
        print("  1. View all items")
        print("  2. Search items")
        print("  3. View inventory report")
        print("  4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            print("\nAll Items in Catalog:")
            for item in interactive_catalog.items.values():
                info = item.get_item_info()
                print(f"  {info['item_id']}: {info['title']} - {info['status']}")
        
        elif choice == "2":
            term = input("Enter search term: ").strip()
            results = interactive_catalog.search_items(term)
            if results:
                print(f"\nFound {len(results)} items:")
                for result in results:
                    print(f"  {result['title']} ({result['category']}) - {result['status']}")
            else:
                print("No items found.")
        
        elif choice == "3":
            report = interactive_catalog.get_inventory_report()
            print(f"\nInventory Report:")
            print(f"  Total items: {report['total_items']}")
            print(f"  Available: {report['available_items']}")
            print(f"  Checked out: {report['checked_out_items']}")
        
        elif choice == "4":
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")
