import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import hashlib
import json
import os
from database import (create_table, insert_item, update_item, delete_item, get_items,
                     create_billing_tables, search_item_by_name, create_bill, get_bills, 
                     get_bill_details, get_daily_sales)

# Authentication System
AUTH_FILE = "auth_config.json"

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def load_auth_config():
    """Load authentication configuration from file"""
    if os.path.exists(AUTH_FILE):
        try:
            with open(AUTH_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"enabled": False, "password_hash": None}
    return {"enabled": False, "password_hash": None}

def save_auth_config(config):
    """Save authentication configuration to file"""
    try:
        with open(AUTH_FILE, 'w') as f:
            json.dump(config, f)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Could not save authentication settings: {str(e)}")
        return False

def authenticate_user():
    """Show login dialog and authenticate user"""
    auth_config = load_auth_config()
    
    if not auth_config["enabled"]:
        return True  # No authentication required
    
    # Create login window
    login_window = tk.Toplevel()
    login_window.title("Lock Shop Authentication")
    login_window.geometry("350x300")
    login_window.transient()
    login_window.grab_set()
    login_window.resizable(False, False)
    
    # Center the window
    login_window.update_idletasks()
    x = (login_window.winfo_screenwidth() // 2) - (350 // 2)
    y = (login_window.winfo_screenheight() // 2) - (300 // 2)
    login_window.geometry(f"350x300+{x}+{y}")
    
    # Make window stay on top
    login_window.attributes('-topmost', True)
    
    # Variables
    authenticated = [False]  # Using list to modify from nested function
    
    # Header
    header_frame = tk.Frame(login_window)
    header_frame.pack(pady=20)
    
    tk.Label(header_frame, text="🔒 Lock Shop Security", 
             font=("Arial", 16, "bold"), fg="#2E7D32").pack()
    tk.Label(header_frame, text="Enter password to access the application", 
             font=("Arial", 10)).pack(pady=5)
    
    # Password entry
    entry_frame = tk.Frame(login_window)
    entry_frame.pack(pady=10)
    
    tk.Label(entry_frame, text="Password:", font=("Arial", 12, "bold")).pack()
    password_entry = tk.Entry(entry_frame, show="*", font=("Arial", 12), width=20)
    password_entry.pack(pady=5)
    password_entry.focus()
    
    # Show/Hide password option
    show_password_var = tk.BooleanVar()
    def toggle_password_visibility():
        if show_password_var.get():
            password_entry.config(show="")
        else:
            password_entry.config(show="*")
    
    tk.Checkbutton(entry_frame, text="Show password", 
                   variable=show_password_var, 
                   command=toggle_password_visibility).pack(pady=2)
    
    # Buttons
    button_frame = tk.Frame(login_window)
    button_frame.pack(pady=20)
    
    def login():
        password = password_entry.get()
        if not password:
            messagebox.showwarning("Input Error", "Please enter password")
            password_entry.focus()
            return
        
        password_hash = hash_password(password)
        if password_hash == auth_config["password_hash"]:
            authenticated[0] = True
            login_window.destroy()
        else:
            messagebox.showerror("Authentication Failed", "Incorrect password!")
            password_entry.delete(0, tk.END)
            password_entry.focus()
    
    def exit_app():
        login_window.destroy()
    
    tk.Button(button_frame, text="Login", command=login, 
              bg="#4CAF50", fg="white", width=10, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Exit", command=exit_app, 
              width=10).pack(side=tk.LEFT, padx=5)
    
    # Bind Enter key to login
    login_window.bind('<Return>', lambda e: login())
    
    # Handle window close
    login_window.protocol("WM_DELETE_WINDOW", exit_app)
    
    # Wait for window to close
    login_window.wait_window()
    
    return authenticated[0]

def show_security_settings():
    """Show security settings window"""
    auth_config = load_auth_config()
    
    security_window = tk.Toplevel(root)
    security_window.title("Security Settings")
    security_window.geometry("400x400")
    security_window.transient(root)
    security_window.grab_set()
    security_window.resizable(False, False)
    
    # Header
    header_frame = tk.Frame(security_window)
    header_frame.pack(pady=15)
    
    tk.Label(header_frame, text="🔐 Security Settings", 
             font=("Arial", 16, "bold"), fg="#2E7D32").pack()
    
    # Current status
    status_frame = tk.Frame(security_window)
    status_frame.pack(fill="x", padx=20, pady=10)
    
    status_text = "🔓 Password Protection: DISABLED" if not auth_config["enabled"] else "🔒 Password Protection: ENABLED"
    status_color = "#FF5722" if not auth_config["enabled"] else "#4CAF50"
    
    status_label = tk.Label(status_frame, text=status_text, 
                           font=("Arial", 12, "bold"), fg=status_color)
    status_label.pack()
    
    # Separator
    ttk.Separator(security_window, orient='horizontal').pack(fill='x', pady=10)
    
    # Security options
    options_frame = tk.Frame(security_window)
    options_frame.pack(expand=True, fill="both", padx=20)
    
    def add_password():
        """Add password protection"""
        if auth_config["enabled"]:
            messagebox.showinfo("Already Protected", "Password protection is already enabled.\nUse 'Change Password' to modify the current password.")
            return
        
        password_window = tk.Toplevel(security_window)
        password_window.title("Add Password Protection")
        password_window.geometry("350x350")
        password_window.transient(security_window)
        password_window.grab_set()
        password_window.resizable(False, False)
        
        tk.Label(password_window, text="Set New Password", 
                font=("Arial", 14, "bold")).pack(pady=15)
        
        # Password fields
        tk.Label(password_window, text="New Password:", font=("Arial", 10)).pack()
        new_password_entry = tk.Entry(password_window, show="*", font=("Arial", 12), width=25)
        new_password_entry.pack(pady=5)
        new_password_entry.focus()
        
        tk.Label(password_window, text="Confirm Password:", font=("Arial", 10)).pack(pady=(10, 0))
        confirm_password_entry = tk.Entry(password_window, show="*", font=("Arial", 12), width=25)
        confirm_password_entry.pack(pady=5)
        
        # Show password option
        show_pwd_var = tk.BooleanVar()
        def toggle_pwd_visibility():
            show_char = "" if show_pwd_var.get() else "*"
            new_password_entry.config(show=show_char)
            confirm_password_entry.config(show=show_char)
        
        tk.Checkbutton(password_window, text="Show passwords", 
                      variable=show_pwd_var, command=toggle_pwd_visibility).pack(pady=5)
        
        def save_password():
            new_pwd = new_password_entry.get()
            confirm_pwd = confirm_password_entry.get()
            
            if not new_pwd or not confirm_pwd:
                messagebox.showwarning("Input Error", "Please fill in both password fields")
                return
            
            if len(new_pwd) < 4:
                messagebox.showwarning("Password Too Short", "Password must be at least 4 characters long")
                return
            
            if new_pwd != confirm_pwd:
                messagebox.showerror("Password Mismatch", "Passwords do not match!")
                return
            
            # Save new password
            new_config = {
                "enabled": True,
                "password_hash": hash_password(new_pwd)
            }
            
            if save_auth_config(new_config):
                messagebox.showinfo("Success", "Password protection has been enabled!\nThe application will require this password on next startup.")
                password_window.destroy()
                security_window.destroy()
        
        # Buttons
        btn_frame = tk.Frame(password_window)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Save Password", command=save_password,
                  bg="#4CAF50", fg="white", width=12).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=password_window.destroy,
                  width=12).pack(side=tk.LEFT, padx=5)
        
        password_window.bind('<Return>', lambda e: save_password())
    
    def change_password():
        """Change existing password"""
        if not auth_config["enabled"]:
            messagebox.showinfo("No Password Set", "Password protection is not enabled.\nUse 'Add Password Protection' first.")
            return
        
        change_window = tk.Toplevel(security_window)
        change_window.title("Change Password")
        change_window.geometry("350x350")
        change_window.transient(security_window)
        change_window.grab_set()
        change_window.resizable(False, False)
        
        tk.Label(change_window, text="Change Password", 
                font=("Arial", 14, "bold")).pack(pady=15)
        
        # Current password
        tk.Label(change_window, text="Current Password:", font=("Arial", 10)).pack()
        current_password_entry = tk.Entry(change_window, show="*", font=("Arial", 12), width=25)
        current_password_entry.pack(pady=5)
        current_password_entry.focus()
        
        # New password fields
        tk.Label(change_window, text="New Password:", font=("Arial", 10)).pack(pady=(10, 0))
        new_password_entry = tk.Entry(change_window, show="*", font=("Arial", 12), width=25)
        new_password_entry.pack(pady=5)
        
        tk.Label(change_window, text="Confirm New Password:", font=("Arial", 10)).pack(pady=(5, 0))
        confirm_password_entry = tk.Entry(change_window, show="*", font=("Arial", 12), width=25)
        confirm_password_entry.pack(pady=5)
        
        # Show password option
        show_pwd_var = tk.BooleanVar()
        def toggle_pwd_visibility():
            show_char = "" if show_pwd_var.get() else "*"
            current_password_entry.config(show=show_char)
            new_password_entry.config(show=show_char)
            confirm_password_entry.config(show=show_char)

        tk.Checkbutton(change_window, text="Show passwords",
                       variable=show_pwd_var, command=toggle_pwd_visibility).pack(pady=5)
        
        def save_new_password():
            current_pwd = current_password_entry.get()
            new_pwd = new_password_entry.get()
            confirm_pwd = confirm_password_entry.get()
            
            if not all([current_pwd, new_pwd, confirm_pwd]):
                messagebox.showwarning("Input Error", "Please fill in all password fields")
                return
            
            # Verify current password
            if hash_password(current_pwd) != auth_config["password_hash"]:
                messagebox.showerror("Authentication Failed", "Current password is incorrect!")
                current_password_entry.delete(0, tk.END)
                current_password_entry.focus()
                return
            
            if len(new_pwd) < 4:
                messagebox.showwarning("Password Too Short", "New password must be at least 4 characters long")
                return
            
            if new_pwd != confirm_pwd:
                messagebox.showerror("Password Mismatch", "New passwords do not match!")
                return
            
            if current_pwd == new_pwd:
                messagebox.showwarning("Same Password", "New password must be different from current password")
                return
            
            # Save new password
            new_config = {
                "enabled": True,
                "password_hash": hash_password(new_pwd)
            }
            
            if save_auth_config(new_config):
                messagebox.showinfo("Success", "Password has been changed successfully!")
                change_window.destroy()
                security_window.destroy()
        
        # Buttons
        btn_frame = tk.Frame(change_window)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Change Password", command=save_new_password,
                  bg="#2196F3", fg="white", width=14).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=change_window.destroy,
                  width=12).pack(side=tk.LEFT, padx=5)
        
        change_window.bind('<Return>', lambda e: save_new_password())
    
    def remove_password():
        """Remove password protection"""
        if not auth_config["enabled"]:
            messagebox.showinfo("No Password Set", "Password protection is not currently enabled.")
            return
        
        # Confirm current password before removing
        remove_window = tk.Toplevel(security_window)
        remove_window.title("Remove Password Protection")
        remove_window.geometry("350x350")
        remove_window.transient(security_window)
        remove_window.grab_set()
        remove_window.resizable(False, False)
        
        tk.Label(remove_window, text="Remove Password Protection", 
                font=("Arial", 14, "bold")).pack(pady=15)
        
        tk.Label(remove_window, text="Enter current password to confirm removal:", 
                font=("Arial", 10)).pack(pady=5)
        
        tk.Label(remove_window, text="Current Password:", font=("Arial", 10)).pack()
        password_entry = tk.Entry(remove_window, show="*", font=("Arial", 12), width=25)
        password_entry.pack(pady=5)
        password_entry.focus()
        
        # Show password option
        show_pwd_var = tk.BooleanVar()
        def toggle_pwd_visibility():
            password_entry.config(show="" if show_pwd_var.get() else "*")
        
        tk.Checkbutton(remove_window, text="Show password", 
                      variable=show_pwd_var, command=toggle_pwd_visibility).pack(pady=5)
        
        def confirm_removal():
            current_pwd = password_entry.get()
            
            if not current_pwd:
                messagebox.showwarning("Input Error", "Please enter your current password")
                return
            
            if hash_password(current_pwd) != auth_config["password_hash"]:
                messagebox.showerror("Authentication Failed", "Incorrect password!")
                password_entry.delete(0, tk.END)
                password_entry.focus()
                return
            
            # Final confirmation
            if messagebox.askyesno("Confirm Removal", 
                                 "Are you sure you want to remove password protection?\n\n" +
                                 "The application will no longer require authentication on startup."):
                
                new_config = {
                    "enabled": False,
                    "password_hash": None
                }
                
                if save_auth_config(new_config):
                    messagebox.showinfo("Success", "Password protection has been removed!\nThe application will no longer require authentication.")
                    remove_window.destroy()
                    security_window.destroy()
        
        # Buttons
        btn_frame = tk.Frame(remove_window)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Remove Protection", command=confirm_removal,
                  bg="#f44336", fg="white", width=16).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=remove_window.destroy,
                  width=12).pack(side=tk.LEFT, padx=5)
        
        remove_window.bind('<Return>', lambda e: confirm_removal())
    
    # Security option buttons
    tk.Button(options_frame, text="🔒 Add Password Protection", command=add_password,
              bg="#4CAF50", fg="white", width=25, height=2, 
              font=("Arial", 11, "bold")).pack(pady=5)
    
    tk.Button(options_frame, text="🔄 Change Password", command=change_password,
              bg="#2196F3", fg="white", width=25, height=2,
              font=("Arial", 11, "bold")).pack(pady=5)
    
    tk.Button(options_frame, text="🔓 Remove Password Protection", command=remove_password,
              bg="#f44336", fg="white", width=25, height=2,
              font=("Arial", 11, "bold")).pack(pady=5)
    
    # Close button
    tk.Button(security_window, text="Close", command=security_window.destroy,
              width=12, font=("Arial", 10)).pack(pady=20)

# GUI Application
# Category-specific low stock thresholds
LOW_STOCK_THRESHOLDS = {
    "Door Locks": 5,        # Door locks are expensive, keep fewer in stock
    "Keys": 20,             # Keys are cheap and commonly needed
    "Car Remotes": 3,       # Car remotes are expensive and less frequently needed
    "Number Plates": 15,    # Moderate stock for number plates
    "Other": 10             # Default threshold for miscellaneous items
}

# Product categories for lock shop
CATEGORIES = ["Door Locks", "Keys", "Car Remotes", "Number Plates", "Other"]

def get_low_stock_threshold(category):
    """Get the low stock threshold for a specific category"""
    return LOW_STOCK_THRESHOLDS.get(category, 10)  # Default to 10 if category not found

def is_low_stock(quantity, category):
    """Check if an item is considered low stock based on its category"""
    threshold = get_low_stock_threshold(category)
    return quantity <= threshold

def load_items(search_term="", show_low_stock_only=False, category_filter="All"):
    for row in tree.get_children():
        tree.delete(row)
    
    items = get_items()
    
    # Filter by category if specified
    if category_filter != "All":
        items = [item for item in items if len(item) > 4 and item[4] == category_filter]
    
    # Filter for low stock items if requested
    if show_low_stock_only:
        filtered_items = []
        for item in items:
            category = item[4] if len(item) > 4 else "Other"
            if is_low_stock(item[2], category):
                filtered_items.append(item)
        items = filtered_items
    
    # Filter items based on search term
    if search_term:
        filtered_items = [item for item in items if search_term.lower() in item[1].lower()]
        items = filtered_items
    
    for row in items:
        # Handle both old data (without category) and new data (with category)
        if len(row) == 4:  # Old format: ID, Name, Qty, Price
            display_row = row + ("Other",)  # Add default category
            category = "Other"
        else:  # New format: ID, Name, Qty, Price, Category
            display_row = row
            category = row[4]
            
        item_id = tree.insert('', 'end', values=display_row)
        # Highlight low stock items in red based on category-specific threshold
        if is_low_stock(row[2], category):
            tree.item(item_id, tags=('low_stock',))

def clear_inputs():
    entry_name.delete(0, tk.END)
    entry_qty.delete(0, tk.END)
    entry_price.delete(0, tk.END)
    category_var.set("Door Locks")  # Reset to first category

def on_search(*args):
    search_term = search_var.get()
    load_items(search_term, low_stock_filter.get(), category_filter_var.get())

def clear_search():
    search_var.set("")
    low_stock_filter.set(False)
    category_filter_var.set("All")
    load_items()

def toggle_low_stock():
    load_items(search_var.get(), low_stock_filter.get(), category_filter_var.get())

def on_category_filter_change(*args):
    load_items(search_var.get(), low_stock_filter.get(), category_filter_var.get())

def check_low_stock_alert():
    """Check and show alert for low stock items with category-specific thresholds"""
    items = get_items()
    low_stock_items = []
    
    for item in items:
        category = item[4] if len(item) > 4 else "Other"
        if is_low_stock(item[2], category):
            low_stock_items.append((item, category, get_low_stock_threshold(category)))
    
    if low_stock_items:
        alert_message = f"Warning: {len(low_stock_items)} item(s) are running low on stock!\n\nLow Stock Items:\n"
        
        # Group by category for better readability
        category_items = {}
        for item_data, category, threshold in low_stock_items:
            if category not in category_items:
                category_items[category] = []
            category_items[category].append((item_data, threshold))
        
        for category in CATEGORIES:
            if category in category_items:
                alert_message += f"\n{category} (Threshold: ≤{get_low_stock_threshold(category)}):\n"
                for item_data, threshold in category_items[category]:
                    alert_message += f"  • {item_data[1]}: {item_data[2]} remaining\n"
        
        messagebox.showwarning("Low Stock Alert", alert_message)
    else:
        messagebox.showinfo("Stock Status", "All items are adequately stocked!")

def show_threshold_settings():
    """Show window to configure category-specific low stock thresholds"""
    threshold_window = tk.Toplevel(root)
    threshold_window.title("Low Stock Threshold Settings")
    threshold_window.geometry("400x300")
    threshold_window.transient(root)
    threshold_window.grab_set()
    
    tk.Label(threshold_window, text="Category-Specific Low Stock Thresholds", 
             font=("Arial", 12, "bold")).pack(pady=10)
    
    tk.Label(threshold_window, text="Items with quantities at or below these values will be marked as low stock:",
             font=("Arial", 9)).pack(pady=5)
    
    # Create frame for threshold entries
    threshold_frame = tk.Frame(threshold_window)
    threshold_frame.pack(expand=True, fill="both", padx=20, pady=10)
    
    threshold_vars = {}
    threshold_entries = {}
    
    for i, category in enumerate(CATEGORIES):
        # Category label
        tk.Label(threshold_frame, text=f"{category}:", font=("Arial", 10, "bold")).grid(
            row=i, column=0, sticky="w", padx=(0, 10), pady=5)
        
        # Current threshold value
        threshold_vars[category] = tk.StringVar(value=str(get_low_stock_threshold(category)))
        threshold_entry = tk.Entry(threshold_frame, textvariable=threshold_vars[category], width=10)
        threshold_entry.grid(row=i, column=1, padx=(0, 5), pady=5)
        threshold_entries[category] = threshold_entry
        
        # Units label
        tk.Label(threshold_frame, text="items", font=("Arial", 9)).grid(
            row=i, column=2, sticky="w", pady=5)
    
    def save_thresholds():
        """Save the new threshold values"""
        global LOW_STOCK_THRESHOLDS
        try:
            new_thresholds = {}
            for category in CATEGORIES:
                value = int(threshold_vars[category].get())
                if value < 0:
                    raise ValueError(f"Threshold for {category} cannot be negative")
                new_thresholds[category] = value
            
            # Update global thresholds
            LOW_STOCK_THRESHOLDS.update(new_thresholds)
            
            # Refresh the main display to reflect new thresholds
            load_items(search_var.get(), low_stock_filter.get(), category_filter_var.get())
            
            messagebox.showinfo("Settings Saved", "Low stock thresholds updated successfully!")
            threshold_window.destroy()
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid positive numbers for all thresholds.\nError: {str(e)}")
    
    def reset_to_defaults():
        """Reset thresholds to default values"""
        default_thresholds = {
            "Door Locks": 5,
            "Keys": 20,
            "Car Remotes": 3,
            "Number Plates": 15,
            "Other": 10
        }
        for category in CATEGORIES:
            threshold_vars[category].set(str(default_thresholds[category]))
    
    # Buttons
    button_frame = tk.Frame(threshold_window)
    button_frame.pack(fill="x", padx=20, pady=10)
    
    tk.Button(button_frame, text="Reset Defaults", command=reset_to_defaults,
              width=12).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Cancel", command=threshold_window.destroy,
              width=12).pack(side=tk.RIGHT, padx=5)
    tk.Button(button_frame, text="Save", command=save_thresholds,
              bg="#4CAF50", fg="white", width=12).pack(side=tk.RIGHT, padx=5)

def get_category_stats():
    """Show inventory statistics by category with threshold information"""
    items = get_items()
    category_stats = {}
    total_value = 0
    
    for item in items:
        category = item[4] if len(item) > 4 else "Other"
        qty = item[2]
        price = item[3]
        item_value = qty * price
        
        if category not in category_stats:
            category_stats[category] = {
                "count": 0, 
                "total_qty": 0, 
                "total_value": 0, 
                "low_stock_count": 0,
                "threshold": get_low_stock_threshold(category)
            }
        
        category_stats[category]["count"] += 1
        category_stats[category]["total_qty"] += qty
        category_stats[category]["total_value"] += item_value
        
        if is_low_stock(qty, category):
            category_stats[category]["low_stock_count"] += 1
            
        total_value += item_value
    
    # Create stats message
    stats_message = "INVENTORY STATISTICS BY CATEGORY\n" + "="*60 + "\n\n"
    
    for category in CATEGORIES:
        if category in category_stats:
            stats = category_stats[category]
            stats_message += f"{category}:\n"
            stats_message += f"  • Items: {stats['count']}\n"
            stats_message += f"  • Total Quantity: {stats['total_qty']}\n"
            stats_message += f"  • Total Value: PKR {stats['total_value']:.2f}\n"
            stats_message += f"  • Low Stock Threshold: ≤{stats['threshold']} items\n"
            if stats['low_stock_count'] > 0:
                stats_message += f"  • ⚠️  Low Stock Items: {stats['low_stock_count']}\n"
            else:
                stats_message += f"  • ✓ All items adequately stocked\n"
            stats_message += "\n"
        else:
            threshold = get_low_stock_threshold(category)
            stats_message += f"{category}:\n"
            stats_message += f"  • No items\n"
            stats_message += f"  • Low Stock Threshold: ≤{threshold} items\n\n"
    
    stats_message += f"TOTAL INVENTORY VALUE: PKR {total_value:.2f}"
    
    # Create popup window for stats
    stats_window = tk.Toplevel(root)
    stats_window.title("Inventory Statistics")
    stats_window.geometry("500x600")
    stats_window.transient(root)
    stats_window.grab_set()
    
    text_widget = tk.Text(stats_window, wrap=tk.WORD, padx=10, pady=10, font=("Courier", 10))
    text_widget.pack(expand=True, fill="both")
    text_widget.insert("1.0", stats_message)
    text_widget.config(state=tk.DISABLED)
    
    button_frame = tk.Frame(stats_window)
    button_frame.pack(pady=10)
    
    tk.Button(button_frame, text="Configure Thresholds", command=show_threshold_settings,
              bg="#FF9800", fg="white", width=18).pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame, text="Close", command=stats_window.destroy, width=12).pack(side=tk.LEFT, padx=5)

# Billing functions
def open_billing_window():
    """Open the billing/POS window"""
    billing_window = tk.Toplevel(root)
    billing_window.title("Create Bill - Lock Shop POS")
    billing_window.geometry("800x700")
    billing_window.transient(root)
    billing_window.grab_set()
    
    # Current bill items
    current_bill = []
    
    def search_and_add_item():
        item_name = search_item_entry.get().strip()
        if not item_name:
            messagebox.showwarning("Input Error", "Please enter item name to search")
            return
        
        # Search for items
        found_items = search_item_by_name(item_name)
        
        if not found_items:
            messagebox.showinfo("Not Found", f"No items found matching '{item_name}'")
            return
        
        if len(found_items) == 1:
            # Only one item found, proceed to quantity
            item = found_items[0]
            add_item_to_bill(item)
        else:
            # Multiple items found, show selection window
            show_item_selection(found_items)
    
    def show_item_selection(items):
        """Show window to select from multiple matching items"""
        selection_window = tk.Toplevel(billing_window)
        selection_window.title("Select Item")
        selection_window.geometry("600x400")
        selection_window.transient(billing_window)
        selection_window.grab_set()
        
        tk.Label(selection_window, text="Multiple items found. Select one:", 
                font=("Arial", 12, "bold")).pack(pady=10)
        
        # Create treeview for item selection
        columns = ("ID", "Name", "Available", "Price", "Category")
        selection_tree = ttk.Treeview(selection_window, columns=columns, show="headings", height=10)
        
        for col in columns:
            selection_tree.heading(col, text=col)
        
        selection_tree.column("ID", width=50)
        selection_tree.column("Name", width=200)
        selection_tree.column("Available", width=80)
        selection_tree.column("Price", width=80)
        selection_tree.column("Category", width=100)
        
        for item in items:
            selection_tree.insert('', 'end', values=item)
        
        selection_tree.pack(expand=True, fill="both", padx=10, pady=10)
        
        def select_item():
            selected = selection_tree.focus()
            if not selected:
                messagebox.showwarning("Selection Error", "Please select an item")
                return
            
            item_values = selection_tree.item(selected, 'values')
            item = (int(item_values[0]), item_values[1], int(item_values[2]), 
                   float(item_values[3]), item_values[4])
            selection_window.destroy()
            add_item_to_bill(item)
        
        btn_frame = tk.Frame(selection_window)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Select", command=select_item, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=selection_window.destroy).pack(side=tk.LEFT, padx=5)
    
    def add_item_to_bill(item):
        """Add selected item to bill after getting quantity"""
        item_id, item_name, available_qty, price, category = item
        
        # Get quantity from user
        qty_window = tk.Toplevel(billing_window)
        qty_window.title("Enter Quantity")
        qty_window.geometry("300x250")
        qty_window.transient(billing_window)
        qty_window.grab_set()
        
        tk.Label(qty_window, text=f"Item: {item_name}", font=("Arial", 10, "bold")).pack(pady=10)
        tk.Label(qty_window, text=f"Category: {category}", font=("Arial", 9)).pack()
        tk.Label(qty_window, text=f"Available: {available_qty}", font=("Arial", 9)).pack()
        tk.Label(qty_window, text=f"Price: PKR {price:.2f}", font=("Arial", 9)).pack()
        
        # Show low stock warning if applicable
        if is_low_stock(available_qty, category):
            threshold = get_low_stock_threshold(category)
            warning_label = tk.Label(qty_window, 
                text=f"⚠️ LOW STOCK: Only {available_qty} remaining (Threshold: {threshold})",
                font=("Arial", 8), fg="red")
            warning_label.pack(pady=5)
        
        tk.Label(qty_window, text="Enter Quantity:", font=("Arial", 10)).pack(pady=(20, 5))
        qty_entry = tk.Entry(qty_window, width=10, font=("Arial", 12))
        qty_entry.pack(pady=5)
        qty_entry.focus()
        
        def add_to_bill():
            try:
                quantity = int(qty_entry.get())
                if quantity <= 0:
                    messagebox.showerror("Invalid Quantity", "Quantity must be greater than 0")
                    return
                if quantity > available_qty:
                    messagebox.showerror("Insufficient Stock", f"Only {available_qty} available")
                    return
                
                # Add to current bill
                bill_item = {
                    'item_id': item_id,
                    'item_name': item_name,
                    'quantity': quantity,
                    'unit_price': price,
                    'total_price': quantity * price
                }
                current_bill.append(bill_item)
                update_bill_display()
                qty_window.destroy()
                search_item_entry.delete(0, tk.END)
                
            except ValueError:
                messagebox.showerror("Invalid Input", "Please enter a valid number")
        
        btn_frame = tk.Frame(qty_window)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="Add to Bill", command=add_to_bill, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=qty_window.destroy).pack(side=tk.LEFT, padx=5)
        
        # Bind Enter key to add to bill
        qty_window.bind('<Return>', lambda e: add_to_bill())
    
    def update_bill_display():
        """Update the bill items display"""
        for row in bill_tree.get_children():
            bill_tree.delete(row)
        
        total_amount = 0
        for item in current_bill:
            bill_tree.insert('', 'end', values=(
                item['item_name'], item['quantity'], f"PKR {item['unit_price']:.2f}", f"PKR {item['total_price']:.2f}"
            ))
            total_amount += item['total_price']
        
        total_label.config(text=f"Total Amount: PKR {total_amount:.2f}")
    
    def remove_bill_item():
        """Remove selected item from bill"""
        selected = bill_tree.focus()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select an item to remove")
            return
        
        item_index = bill_tree.index(selected)
        current_bill.pop(item_index)
        update_bill_display()
    
    def save_bill():
        """Save the bill to database"""
        if not current_bill:
            messagebox.showwarning("Empty Bill", "Please add items to the bill")
            return
        
        customer_name = customer_entry.get().strip()
        if not customer_name:
            messagebox.showwarning("Customer Required", "Please enter customer name")
            return
        
        try:
            bill_date = datetime.now().strftime("%Y-%m-%d")
            bill_id = create_bill(customer_name, bill_date, current_bill)
            
            messagebox.showinfo("Bill Saved", f"Bill #{bill_id} saved successfully!\nTotal: PKR {sum(item['total_price'] for item in current_bill):.2f}")
            
            # Clear the bill
            current_bill.clear()
            update_bill_display()
            customer_entry.delete(0, tk.END)
            
            # Refresh main inventory display
            load_items(search_var.get(), low_stock_filter.get(), category_filter_var.get())
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save bill: {str(e)}")
    
    # Billing window layout
    # Customer info
    customer_frame = tk.Frame(billing_window)
    customer_frame.pack(fill="x", padx=10, pady=10)
    
    tk.Label(customer_frame, text="Customer Name:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
    customer_entry = tk.Entry(customer_frame, font=("Arial", 12), width=30)
    customer_entry.pack(side=tk.LEFT, padx=10)
    
    date_label = tk.Label(customer_frame, text=f"Date: {datetime.now().strftime('%Y-%m-%d')}", 
                         font=("Arial", 12))
    date_label.pack(side=tk.RIGHT)
    
    # Item search
    search_frame = tk.Frame(billing_window)
    search_frame.pack(fill="x", padx=10, pady=10)
    
    tk.Label(search_frame, text="Search Item:", font=("Arial", 12, "bold")).pack(side=tk.LEFT)
    search_item_entry = tk.Entry(search_frame, font=("Arial", 12), width=30)
    search_item_entry.pack(side=tk.LEFT, padx=10)
    search_item_entry.bind('<Return>', lambda e: search_and_add_item())
    
    tk.Button(search_frame, text="Search & Add", command=search_and_add_item, 
             bg="#4CAF50", fg="white", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
    
    # Bill items display
    bill_frame = tk.Frame(billing_window)
    bill_frame.pack(expand=True, fill="both", padx=10, pady=10)
    
    tk.Label(bill_frame, text="Bill Items:", font=("Arial", 12, "bold")).pack(anchor="w")
    
    bill_columns = ("Item Name", "Quantity", "Unit Price", "Total")
    bill_tree = ttk.Treeview(bill_frame, columns=bill_columns, show="headings", height=10)
    
    for col in bill_columns:
        bill_tree.heading(col, text=col)
    
    bill_tree.column("Item Name", width=250)
    bill_tree.column("Quantity", width=100, anchor=tk.CENTER)
    bill_tree.column("Unit Price", width=100, anchor=tk.CENTER)
    bill_tree.column("Total", width=100, anchor=tk.CENTER)
    
    bill_scrollbar = ttk.Scrollbar(bill_frame, orient="vertical", command=bill_tree.yview)
    bill_tree.configure(yscrollcommand=bill_scrollbar.set)
    
    bill_tree.pack(side="left", expand=True, fill="both")
    bill_scrollbar.pack(side="right", fill="y")
    
    # Total and buttons
    bottom_frame = tk.Frame(billing_window)
    bottom_frame.pack(fill="x", padx=10, pady=10)
    
    total_label = tk.Label(bottom_frame, text="Total Amount: PKR 0.00", 
                          font=("Arial", 14, "bold"), fg="#2E7D32")
    total_label.pack(anchor="w")
    
    btn_frame = tk.Frame(bottom_frame)
    btn_frame.pack(fill="x", pady=10)
    
    tk.Button(btn_frame, text="Remove Item", command=remove_bill_item, 
             bg="#f44336", fg="white", width=12).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Clear Bill", command=lambda: (current_bill.clear(), update_bill_display()), 
             bg="#FF9800", fg="white", width=12).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Save Bill", command=save_bill, 
             bg="#4CAF50", fg="white", width=12, font=("Arial", 10, "bold")).pack(side=tk.RIGHT, padx=5)
    tk.Button(btn_frame, text="Cancel", command=billing_window.destroy, 
             width=12).pack(side=tk.RIGHT, padx=5)

def view_bills():
    """View all bills"""
    bills_window = tk.Toplevel(root)
    bills_window.title("View Bills - Sales Records")
    bills_window.geometry("800x600")
    bills_window.transient(root)
    bills_window.grab_set()
    
    # Bills list
    bills_frame = tk.Frame(bills_window)
    bills_frame.pack(expand=True, fill="both", padx=10, pady=10)
    
    tk.Label(bills_frame, text="Sales Records:", font=("Arial", 12, "bold")).pack(anchor="w")
    
    bills_columns = ("Bill ID", "Customer", "Date", "Amount", "Time")
    bills_tree = ttk.Treeview(bills_frame, columns=bills_columns, show="headings", height=15)
    
    for col in bills_columns:
        bills_tree.heading(col, text=col)
    
    bills_tree.column("Bill ID", width=80, anchor=tk.CENTER)
    bills_tree.column("Customer", width=200)
    bills_tree.column("Date", width=100, anchor=tk.CENTER)
    bills_tree.column("Amount", width=120, anchor=tk.CENTER)
    bills_tree.column("Time", width=150, anchor=tk.CENTER)
    
    bills_scrollbar = ttk.Scrollbar(bills_frame, orient="vertical", command=bills_tree.yview)
    bills_tree.configure(yscrollcommand=bills_scrollbar.set)
    
    bills_tree.pack(side="left", expand=True, fill="both")
    bills_scrollbar.pack(side="right", fill="y")
    
    def load_bills():
        for row in bills_tree.get_children():
            bills_tree.delete(row)
        
        bills = get_bills()
        total_sales = 0
        for bill in bills:
            bills_tree.insert('', 'end', values=(
                f"#{bill[0]}", bill[1], bill[2], f"PKR {bill[3]:.2f}", bill[4]
            ))
            total_sales += bill[3]
        
        total_sales_label.config(text=f"Total Sales: PKR {total_sales:.2f}")
    
    def view_bill_details():
        selected = bills_tree.focus()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a bill to view details")
            return
        
        bill_values = bills_tree.item(selected, 'values')
        bill_id = int(bill_values[0].replace('#', ''))
        
        # Get bill details
        bill, items = get_bill_details(bill_id)
        
        # Create details window
        details_window = tk.Toplevel(bills_window)
        details_window.title(f"Bill #{bill_id} Details")
        details_window.geometry("600x500")
        details_window.transient(bills_window)
        
        # Bill header
        header_text = f"Bill #{bill[0]}\n"
        header_text += f"Customer: {bill[1]}\n"
        header_text += f"Date: {bill[2]}\n"
        header_text += f"Time: {bill[4]}\n"
        header_text += "-" * 50 + "\n"
        
        text_widget = tk.Text(details_window, wrap=tk.WORD, font=("Courier", 10))
        text_widget.pack(expand=True, fill="both", padx=10, pady=10)
        text_widget.insert("1.0", header_text)
        
        # Bill items
        text_widget.insert(tk.END, f"{'Item':<30} {'Qty':<5} {'Price':<10} {'Total':<10}\n")
        text_widget.insert(tk.END, "-" * 65 + "\n")
        
        for item in items:
            text_widget.insert(tk.END, f"{item[0]:<30} {item[1]:<5} PKR {item[2]:<9.2f} PKR {item[3]:<9.2f}\n")
        
        text_widget.insert(tk.END, "-" * 65 + "\n")
        text_widget.insert(tk.END, f"{'TOTAL AMOUNT:':<50} PKR {bill[3]:.2f}\n")
        
        text_widget.config(state=tk.DISABLED)
        
        tk.Button(details_window, text="Close", command=details_window.destroy).pack(pady=10)
    
    # Buttons and stats
    bottom_frame = tk.Frame(bills_window)
    bottom_frame.pack(fill="x", padx=10, pady=10)
    
    total_sales_label = tk.Label(bottom_frame, text="Total Sales: PKR 0.00", 
                                font=("Arial", 12, "bold"), fg="#2E7D32")
    total_sales_label.pack(anchor="w")
    
    btn_frame = tk.Frame(bottom_frame)
    btn_frame.pack(fill="x", pady=10)
    
    tk.Button(btn_frame, text="View Details", command=view_bill_details, 
             bg="#2196F3", fg="white", width=12).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Refresh", command=load_bills, 
             bg="#4CAF50", fg="white", width=12).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame, text="Close", command=bills_window.destroy, 
             width=12).pack(side=tk.RIGHT, padx=5)
    
    load_bills()

def on_add():
    name = entry_name.get()
    qty = entry_qty.get()
    price = entry_price.get()
    category = category_var.get()
    
    if not name or not qty or not price:
        messagebox.showwarning("Input Error", "All fields are required")
        return
    try:
        insert_item(name, int(qty), float(price), category)
        load_items(search_var.get(), low_stock_filter.get(), category_filter_var.get())
        clear_inputs()
    except ValueError:
        messagebox.showerror("Input Error", "Quantity must be a number and Price must be a decimal number")
    except Exception as e:
        messagebox.showerror("Database Error", f"Could not add item. Error: {str(e)}")

def on_update():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Selection Error", "Select an item to update")
        return
    values = tree.item(selected, 'values')
    item_id = values[0]
    name = entry_name.get()
    qty = entry_qty.get()
    price = entry_price.get()
    category = category_var.get()
    
    if not name or not qty or not price:
        messagebox.showwarning("Input Error", "All fields are required")
        return
    
    try:
        update_item(item_id, name, int(qty), float(price), category)
        load_items(search_var.get(), low_stock_filter.get(), category_filter_var.get())
        clear_inputs()
    except ValueError:
        messagebox.showerror("Input Error", "Quantity must be a number and Price must be a decimal number")
    except Exception as e:
        messagebox.showerror("Database Error", f"Could not update item. Error: {str(e)}")

def on_delete():
    selected = tree.focus()
    if not selected:
        messagebox.showwarning("Selection Error", "Select an item to delete")
        return
    
    # Confirmation dialog
    if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this item?"):
        item_id = tree.item(selected, 'values')[0]
        delete_item(item_id)
        load_items(search_var.get(), low_stock_filter.get(), category_filter_var.get())
        clear_inputs()

def on_tree_select(event):
    selected = tree.focus()
    if not selected:
        return
    values = tree.item(selected, 'values')
    entry_name.delete(0, tk.END)
    entry_name.insert(0, values[1])
    entry_qty.delete(0, tk.END)
    entry_qty.insert(0, values[2])
    entry_price.delete(0, tk.END)
    entry_price.insert(0, values[3])
    # Set category if available
    if len(values) > 4:
        category_var.set(values[4])

# Main Application Startup with Authentication
def main():
    """Main function to start the application with authentication"""
    global root
    
    # Check authentication first
    if not authenticate_user():
        return  # User failed authentication or chose to exit
    
    # Create main application window
    root = tk.Tk()
    root.title("Lock Shop Inventory System")
    root.geometry("1400x600")
    
    # Search Section
    search_frame = tk.Frame(root)
    search_frame.pack(pady=10, padx=10, fill="x")
    
    tk.Label(search_frame, text="Search Items:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(0, 5))
    
    global search_var, search_entry, category_filter_var, category_filter_combo, low_stock_filter, low_stock_check
    
    search_var = tk.StringVar()
    search_var.trace("w", on_search)  # Real-time search as user types
    search_entry = tk.Entry(search_frame, textvariable=search_var, width=25)
    search_entry.pack(side=tk.LEFT, padx=(0, 5))
    
    tk.Button(search_frame, text="Clear Search", command=clear_search, width=12).pack(side=tk.LEFT, padx=5)
    
    # Category Filter
    tk.Label(search_frame, text="Category:", font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=(15, 5))
    category_filter_var = tk.StringVar(value="All")
    category_filter_combo = ttk.Combobox(search_frame, textvariable=category_filter_var, 
                                       values=["All"] + CATEGORIES, state="readonly", width=15)
    category_filter_combo.pack(side=tk.LEFT, padx=(0, 5))
    category_filter_var.trace("w", on_category_filter_change)
    
    # Low Stock Filter
    low_stock_filter = tk.BooleanVar()
    low_stock_check = tk.Checkbutton(search_frame, text="Low Stock Only", 
                                    variable=low_stock_filter, command=toggle_low_stock)
    low_stock_check.pack(side=tk.LEFT, padx=10)
    
    # Action buttons in search frame
    tk.Button(search_frame, text="🔐 Security", command=show_security_settings,
              width=12, bg="#9C27B0", fg="white", font=("Arial", 10, "bold")).pack(side=tk.RIGHT, padx=2)
    tk.Button(search_frame, text="Threshold Settings", command=show_threshold_settings,
              width=16, bg="#795548", fg="white").pack(side=tk.RIGHT, padx=2)
    tk.Button(search_frame, text="Low Stock Alert", command=check_low_stock_alert, 
              width=15, bg="#FF5722", fg="white").pack(side=tk.RIGHT, padx=2)
    tk.Button(search_frame, text="Statistics", command=get_category_stats, 
              width=12, bg="#607D8B", fg="white").pack(side=tk.RIGHT, padx=2)
    tk.Button(search_frame, text="View Bills", command=view_bills, 
              width=12, bg="#3F51B5", fg="white").pack(side=tk.RIGHT, padx=2)
    tk.Button(search_frame, text="Create Bill", command=open_billing_window, 
              width=12, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(side=tk.RIGHT, padx=2)
    
    # Separator
    separator = ttk.Separator(root, orient='horizontal')
    separator.pack(fill='x', pady=5)
    
    # Input fields
    frame = tk.Frame(root)
    frame.pack(pady=10)
    
    tk.Label(frame, text="Item Name", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5)
    tk.Label(frame, text="Quantity", font=("Arial", 9, "bold")).grid(row=0, column=1, padx=5)
    tk.Label(frame, text="Price (PKR)", font=("Arial", 9, "bold")).grid(row=0, column=2, padx=5)
    tk.Label(frame, text="Category", font=("Arial", 9, "bold")).grid(row=0, column=3, padx=5)
    
    global entry_name, entry_qty, entry_price, category_var, category_combo
    
    entry_name = tk.Entry(frame, width=20)
    entry_name.grid(row=1, column=0, padx=5, pady=5)
    entry_qty = tk.Entry(frame, width=12)
    entry_qty.grid(row=1, column=1, padx=5, pady=5)
    entry_price = tk.Entry(frame, width=12)
    entry_price.grid(row=1, column=2, padx=5, pady=5)
    
    # Category dropdown
    category_var = tk.StringVar(value="Door Locks")
    category_combo = ttk.Combobox(frame, textvariable=category_var, values=CATEGORIES, 
                                 state="readonly", width=15)
    category_combo.grid(row=1, column=3, padx=5, pady=5)
    
    # Buttons
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=10)
    
    tk.Button(btn_frame, text="Add Item", width=12, command=on_add, bg="#4CAF50", fg="white").grid(row=0, column=0, padx=5)
    tk.Button(btn_frame, text="Update Item", width=12, command=on_update, bg="#2196F3", fg="white").grid(row=0, column=1, padx=5)
    tk.Button(btn_frame, text="Delete Item", width=12, command=on_delete, bg="#f44336", fg="white").grid(row=0, column=2, padx=5)
    tk.Button(btn_frame, text="Clear Fields", width=12, command=clear_inputs, bg="#FF9800", fg="white").grid(row=0, column=3, padx=5)
    
    # Status Label
    status_frame = tk.Frame(root)
    status_frame.pack(fill="x", padx=10)
    
    global status_label
    status_label = tk.Label(status_frame, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
    status_label.pack(fill="x")
    
    # Treeview with scrollbar
    tree_frame = tk.Frame(root)
    tree_frame.pack(expand=True, fill="both", padx=10, pady=10)
    
    columns = ("ID", "Item Name", "Quantity", "Price", "Category")
    global tree
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    
    # Configure column widths and headings
    tree.heading("ID", text="ID")
    tree.heading("Item Name", text="Item Name")
    tree.heading("Quantity", text="Qty")
    tree.heading("Price", text="Price (PKR)")
    tree.heading("Category", text="Category")
    
    tree.column("ID", width=50, anchor=tk.CENTER)
    tree.column("Item Name", width=250, anchor=tk.W)
    tree.column("Quantity", width=80, anchor=tk.CENTER)
    tree.column("Price", width=100, anchor=tk.CENTER)
    tree.column("Category", width=120, anchor=tk.CENTER)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side="left", expand=True, fill="both")
    scrollbar.pack(side="right", fill="y")
    
    tree.bind("<<TreeviewSelect>>", on_tree_select)
    
    # Configure tags for low stock highlighting
    tree.tag_configure('low_stock', background='#ffebee', foreground='#c62828')
    
    # Update status label with item count and threshold info
    def update_status():
        item_count = len(tree.get_children())
        search_term = search_var.get()
        low_stock_only = low_stock_filter.get()
        category_filter = category_filter_var.get()
        
        status_parts = []
        
        if category_filter != "All":
            threshold = get_low_stock_threshold(category_filter)
            status_parts.append(f"{category_filter} (Low Stock: ≤{threshold})")
        
        if low_stock_only:
            status_parts.append("low stock items")
        
        if search_term:
            status_parts.append(f"matching '{search_term}'")
        
        if status_parts:
            status_text = f"Showing {item_count} {' '.join(status_parts)} items"
        else:
            status_text = f"Total items: {item_count}"
            
        # Add threshold info for current category filter
        if category_filter != "All":
            threshold = get_low_stock_threshold(category_filter)
            status_text += f" | {category_filter} Low Stock Threshold: ≤{threshold}"
        
        # Add authentication status
        auth_config = load_auth_config()
        auth_status = "🔒 Protected" if auth_config["enabled"] else "🔓 Unprotected"
        status_text += f" | Security: {auth_status}"
        
        status_label.config(text=status_text)
    
    # Override load_items to update status
    original_load_items = load_items
    def load_items_with_status(search_term="", show_low_stock_only=False, category_filter="All"):
        original_load_items(search_term, show_low_stock_only, category_filter)
        update_status()
    
    # Replace the global load_items function for this window
    globals()['load_items'] = load_items_with_status
    
    # Initialize database tables
    create_table()
    create_billing_tables()
    
    # Load initial data
    load_items()
    
    # Start the main loop
    root.mainloop()

# Run the application
if __name__ == "__main__":
    main()