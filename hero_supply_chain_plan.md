# Hero MotoCorp Supply Chain Management System
## Complete Development Plan & Database Schema

## 1. Project Overview

### 1.1 System Architecture
```
Frontend (Python GUI/CLI) ↔ Business Logic Layer ↔ MySQL Database
                          ↓
              Analytics & Reporting Module
                          ↓
              External APIs (Future: Maps, IoT)
```

### 1.2 Technology Stack
- **Backend**: Python 3.9+
- **Database**: MySQL 8.0
- **Libraries**: 
  - `mysql-connector-python` (Database connectivity)
  - `pandas` (Data analysis)
  - `matplotlib/plotly` (Visualization)
  - `tkinter` (GUI - Optional)
  - `flask` (Web interface - Optional)
  - `schedule` (Automated tasks)

## 2. Complete Database Schema

### 2.1 Master Data Tables

```sql
-- 1. Suppliers Master
CREATE TABLE suppliers (
    supplier_id INT PRIMARY KEY AUTO_INCREMENT,
    supplier_code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    contact_person VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'India',
    pin_code VARCHAR(10),
    rating DECIMAL(3,2) DEFAULT 0.00,
    lead_time_days INT DEFAULT 0,
    payment_terms VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Product Models Master
CREATE TABLE product_models (
    model_id INT PRIMARY KEY AUTO_INCREMENT,
    model_code VARCHAR(50) UNIQUE NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    engine_capacity VARCHAR(20),
    fuel_type ENUM('Petrol', 'Electric', 'Hybrid'),
    target_price DECIMAL(10,2),
    launch_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Parts Master
CREATE TABLE parts (
    part_id INT PRIMARY KEY AUTO_INCREMENT,
    part_code VARCHAR(50) UNIQUE NOT NULL,
    part_name VARCHAR(255) NOT NULL,
    category ENUM('Engine', 'Chassis', 'Electrical', 'Body', 'Tire', 'Accessory', 'Raw Material'),
    subcategory VARCHAR(100),
    unit_of_measure VARCHAR(20) DEFAULT 'PCS',
    unit_price DECIMAL(10,2),
    weight_kg DECIMAL(8,3),
    dimensions VARCHAR(100),
    quality_grade VARCHAR(20),
    shelf_life_days INT,
    is_critical BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 4. Supplier-Parts Mapping
CREATE TABLE supplier_parts (
    supplier_part_id INT PRIMARY KEY AUTO_INCREMENT,
    supplier_id INT,
    part_id INT,
    supplier_part_code VARCHAR(50),
    unit_price DECIMAL(10,2),
    minimum_order_qty INT DEFAULT 1,
    lead_time_days INT DEFAULT 0,
    quality_rating DECIMAL(3,2) DEFAULT 0.00,
    is_preferred BOOLEAN DEFAULT FALSE,
    contract_start_date DATE,
    contract_end_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (part_id) REFERENCES parts(part_id),
    UNIQUE KEY unique_supplier_part (supplier_id, part_id)
);

-- 5. Manufacturing Plants
CREATE TABLE plants (
    plant_id INT PRIMARY KEY AUTO_INCREMENT,
    plant_code VARCHAR(20) UNIQUE NOT NULL,
    plant_name VARCHAR(255) NOT NULL,
    location VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    capacity_per_day INT,
    operating_shifts INT DEFAULT 1,
    shift_hours INT DEFAULT 8,
    manager_name VARCHAR(100),
    contact_phone VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 6. Dealers Master
CREATE TABLE dealers (
    dealer_id INT PRIMARY KEY AUTO_INCREMENT,
    dealer_code VARCHAR(20) UNIQUE NOT NULL,
    dealer_name VARCHAR(255) NOT NULL,
    owner_name VARCHAR(100),
    phone VARCHAR(20),
    email VARCHAR(100),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pin_code VARCHAR(10),
    territory VARCHAR(100),
    showroom_size_sqft INT,
    service_capacity INT,
    credit_limit DECIMAL(15,2),
    security_deposit DECIMAL(15,2),
    onboarding_date DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Bill of Materials (BOM)
CREATE TABLE bom (
    bom_id INT PRIMARY KEY AUTO_INCREMENT,
    model_id INT,
    part_id INT,
    quantity_required DECIMAL(8,3) NOT NULL,
    stage ENUM('Engine Assembly', 'Chassis Building', 'Painting', 'Final Assembly') NOT NULL,
    is_critical BOOLEAN DEFAULT FALSE,
    wastage_percentage DECIMAL(5,2) DEFAULT 0.00,
    effective_from DATE,
    effective_to DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES product_models(model_id),
    FOREIGN KEY (part_id) REFERENCES parts(part_id),
    INDEX idx_bom_model (model_id),
    INDEX idx_bom_stage (stage)
);
```

### 2.2 Inventory Management Tables

```sql
-- 8. Inventory Master
CREATE TABLE inventory (
    inventory_id INT PRIMARY KEY AUTO_INCREMENT,
    part_id INT,
    plant_id INT,
    location_type ENUM('Raw Material', 'WIP', 'Finished Goods', 'Transit') NOT NULL,
    current_stock DECIMAL(12,3) DEFAULT 0,
    reserved_stock DECIMAL(12,3) DEFAULT 0,
    available_stock DECIMAL(12,3) GENERATED ALWAYS AS (current_stock - reserved_stock) STORED,
    reorder_level DECIMAL(12,3),
    maximum_level DECIMAL(12,3),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (part_id) REFERENCES parts(part_id),
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id),
    UNIQUE KEY unique_inventory (part_id, plant_id, location_type)
);

-- 9. Stock Movements
CREATE TABLE stock_movements (
    movement_id INT PRIMARY KEY AUTO_INCREMENT,
    part_id INT,
    plant_id INT,
    movement_type ENUM('Inbound', 'Outbound', 'Transfer', 'Adjustment', 'Consumption'),
    reference_type ENUM('Purchase Order', 'Production Order', 'Sales Order', 'Transfer', 'Manual'),
    reference_id INT,
    quantity DECIMAL(12,3),
    unit_cost DECIMAL(10,2),
    from_location VARCHAR(100),
    to_location VARCHAR(100),
    movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT,
    created_by VARCHAR(100),
    FOREIGN KEY (part_id) REFERENCES parts(part_id),
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id),
    INDEX idx_movement_date (movement_date),
    INDEX idx_movement_type (movement_type)
);
```

### 2.3 Procurement Module Tables

```sql
-- 10. Purchase Orders
CREATE TABLE purchase_orders (
    po_id INT PRIMARY KEY AUTO_INCREMENT,
    po_number VARCHAR(50) UNIQUE NOT NULL,
    supplier_id INT,
    plant_id INT,
    po_date DATE NOT NULL,
    required_date DATE,
    status ENUM('Draft', 'Sent', 'Acknowledged', 'Partial Received', 'Completed', 'Cancelled') DEFAULT 'Draft',
    total_amount DECIMAL(15,2) DEFAULT 0,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    freight_charges DECIMAL(10,2) DEFAULT 0,
    payment_terms VARCHAR(100),
    delivery_address TEXT,
    remarks TEXT,
    created_by VARCHAR(100),
    approved_by VARCHAR(100),
    approved_date TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id),
    INDEX idx_po_date (po_date),
    INDEX idx_po_status (status)
);

-- 11. Purchase Order Line Items
CREATE TABLE po_line_items (
    po_line_id INT PRIMARY KEY AUTO_INCREMENT,
    po_id INT,
    part_id INT,
    ordered_quantity DECIMAL(12,3),
    unit_price DECIMAL(10,2),
    line_amount DECIMAL(15,2) GENERATED ALWAYS AS (ordered_quantity * unit_price) STORED,
    received_quantity DECIMAL(12,3) DEFAULT 0,
    pending_quantity DECIMAL(12,3) GENERATED ALWAYS AS (ordered_quantity - received_quantity) STORED,
    expected_delivery_date DATE,
    line_status ENUM('Pending', 'Partial', 'Completed') DEFAULT 'Pending',
    quality_approved BOOLEAN DEFAULT FALSE,
    remarks TEXT,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
    FOREIGN KEY (part_id) REFERENCES parts(part_id),
    INDEX idx_po_line_part (part_id),
    INDEX idx_po_line_status (line_status)
);

-- 12. Goods Receipt Notes
CREATE TABLE goods_receipts (
    grn_id INT PRIMARY KEY AUTO_INCREMENT,
    grn_number VARCHAR(50) UNIQUE NOT NULL,
    po_id INT,
    supplier_id INT,
    plant_id INT,
    receipt_date DATE NOT NULL,
    invoice_number VARCHAR(100),
    invoice_date DATE,
    vehicle_number VARCHAR(20),
    driver_name VARCHAR(100),
    total_quantity DECIMAL(12,3),
    quality_status ENUM('Pending', 'Approved', 'Rejected', 'Hold') DEFAULT 'Pending',
    remarks TEXT,
    received_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id),
    FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id)
);

-- 13. GRN Line Items
CREATE TABLE grn_line_items (
    grn_line_id INT PRIMARY KEY AUTO_INCREMENT,
    grn_id INT,
    po_line_id INT,
    part_id INT,
    received_quantity DECIMAL(12,3),
    accepted_quantity DECIMAL(12,3),
    rejected_quantity DECIMAL(12,3),
    unit_price DECIMAL(10,2),
    quality_remarks TEXT,
    FOREIGN KEY (grn_id) REFERENCES goods_receipts(grn_id) ON DELETE CASCADE,
    FOREIGN KEY (po_line_id) REFERENCES po_line_items(po_line_id),
    FOREIGN KEY (part_id) REFERENCES parts(part_id)
);
```

### 2.4 Production Module Tables

```sql
-- 14. Production Orders
CREATE TABLE production_orders (
    production_order_id INT PRIMARY KEY AUTO_INCREMENT,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    model_id INT,
    plant_id INT,
    planned_quantity INT,
    actual_quantity INT DEFAULT 0,
    priority ENUM('Low', 'Medium', 'High', 'Critical') DEFAULT 'Medium',
    planned_start_date DATE,
    planned_end_date DATE,
    actual_start_date DATE NULL,
    actual_end_date DATE NULL,
    status ENUM('Planned', 'Released', 'In Progress', 'Completed', 'Cancelled') DEFAULT 'Planned',
    shift ENUM('Shift 1', 'Shift 2', 'Shift 3') DEFAULT 'Shift 1',
    supervisor VARCHAR(100),
    remarks TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES product_models(model_id),
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id),
    INDEX idx_production_status (status),
    INDEX idx_production_date (planned_start_date)
);

-- 15. Production Stages
CREATE TABLE production_stages (
    stage_id INT PRIMARY KEY AUTO_INCREMENT,
    production_order_id INT,
    stage_name ENUM('Engine Assembly', 'Chassis Building', 'Painting', 'Final Assembly', 'Quality Check') NOT NULL,
    stage_sequence INT,
    planned_start_date DATE,
    planned_end_date DATE,
    actual_start_date DATE NULL,
    actual_end_date DATE NULL,
    status ENUM('Not Started', 'In Progress', 'Completed', 'On Hold') DEFAULT 'Not Started',
    quantity_completed INT DEFAULT 0,
    quality_passed INT DEFAULT 0,
    quality_failed INT DEFAULT 0,
    machine_id VARCHAR(50),
    operator_name VARCHAR(100),
    remarks TEXT,
    FOREIGN KEY (production_order_id) REFERENCES production_orders(production_order_id) ON DELETE CASCADE,
    INDEX idx_stage_status (status),
    INDEX idx_stage_sequence (stage_sequence)
);

-- 16. Production Material Consumption
CREATE TABLE production_consumption (
    consumption_id INT PRIMARY KEY AUTO_INCREMENT,
    production_order_id INT,
    stage_id INT,
    part_id INT,
    planned_quantity DECIMAL(12,3),
    actual_quantity DECIMAL(12,3),
    wastage_quantity DECIMAL(12,3) DEFAULT 0,
    consumption_date DATE,
    batch_number VARCHAR(50),
    remarks TEXT,
    FOREIGN KEY (production_order_id) REFERENCES production_orders(production_order_id),
    FOREIGN KEY (stage_id) REFERENCES production_stages(stage_id),
    FOREIGN KEY (part_id) REFERENCES parts(part_id),
    INDEX idx_consumption_date (consumption_date)
);

-- 17. Quality Control
CREATE TABLE quality_checks (
    qc_id INT PRIMARY KEY AUTO_INCREMENT,
    reference_type ENUM('Production Order', 'Goods Receipt', 'Final Product'),
    reference_id INT,
    part_id INT NULL,
    production_order_id INT NULL,
    check_date DATE,
    inspector_name VARCHAR(100),
    total_checked INT,
    passed_quantity INT,
    failed_quantity INT,
    defect_types TEXT,
    corrective_action TEXT,
    status ENUM('Pass', 'Fail', 'Conditional Pass') DEFAULT 'Pass',
    remarks TEXT,
    FOREIGN KEY (part_id) REFERENCES parts(part_id),
    FOREIGN KEY (production_order_id) REFERENCES production_orders(production_order_id),
    INDEX idx_qc_date (check_date),
    INDEX idx_qc_status (status)
);
```

### 2.5 Logistics & Distribution Tables

```sql
-- 18. Shipments
CREATE TABLE shipments (
    shipment_id INT PRIMARY KEY AUTO_INCREMENT,
    shipment_number VARCHAR(50) UNIQUE NOT NULL,
    shipment_type ENUM('Inbound', 'Outbound', 'Inter-plant') NOT NULL,
    from_location_id INT,
    to_location_id INT,
    transporter_name VARCHAR(255),
    vehicle_number VARCHAR(20),
    driver_name VARCHAR(100),
    driver_phone VARCHAR(20),
    planned_dispatch_date DATE,
    actual_dispatch_date DATE NULL,
    planned_delivery_date DATE,
    actual_delivery_date DATE NULL,
    status ENUM('Planned', 'In Transit', 'Delivered', 'Cancelled') DEFAULT 'Planned',
    freight_charges DECIMAL(10,2),
    distance_km DECIMAL(8,2),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_shipment_status (status),
    INDEX idx_dispatch_date (actual_dispatch_date)
);

-- 19. Shipment Line Items
CREATE TABLE shipment_items (
    shipment_item_id INT PRIMARY KEY AUTO_INCREMENT,
    shipment_id INT,
    reference_type ENUM('Purchase Order', 'Production Order', 'Sales Order'),
    reference_id INT,
    part_id INT NULL,
    model_id INT NULL,
    quantity DECIMAL(12,3),
    unit_weight_kg DECIMAL(8,3),
    total_weight_kg DECIMAL(12,3) GENERATED ALWAYS AS (quantity * unit_weight_kg) STORED,
    packaging_type VARCHAR(100),
    remarks TEXT,
    FOREIGN KEY (shipment_id) REFERENCES shipments(shipment_id) ON DELETE CASCADE,
    FOREIGN KEY (part_id) REFERENCES parts(part_id),
    FOREIGN KEY (model_id) REFERENCES product_models(model_id)
);

-- 20. Dealer Orders
CREATE TABLE dealer_orders (
    dealer_order_id INT PRIMARY KEY AUTO_INCREMENT,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    dealer_id INT,
    order_date DATE NOT NULL,
    required_date DATE,
    status ENUM('Pending', 'Confirmed', 'Allocated', 'Shipped', 'Delivered', 'Cancelled') DEFAULT 'Pending',
    total_quantity INT,
    total_amount DECIMAL(15,2),
    payment_terms VARCHAR(100),
    delivery_address TEXT,
    priority ENUM('Low', 'Medium', 'High') DEFAULT 'Medium',
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id),
    INDEX idx_dealer_order_date (order_date),
    INDEX idx_dealer_order_status (status)
);

-- 21. Dealer Order Items
CREATE TABLE dealer_order_items (
    dealer_order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    dealer_order_id INT,
    model_id INT,
    color_variant VARCHAR(50),
    ordered_quantity INT,
    allocated_quantity INT DEFAULT 0,
    shipped_quantity INT DEFAULT 0,
    unit_price DECIMAL(10,2),
    line_amount DECIMAL(15,2) GENERATED ALWAYS AS (ordered_quantity * unit_price) STORED,
    FOREIGN KEY (dealer_order_id) REFERENCES dealer_orders(dealer_order_id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES product_models(model_id)
);

-- 22. Dealer Inventory
CREATE TABLE dealer_inventory (
    dealer_inventory_id INT PRIMARY KEY AUTO_INCREMENT,
    dealer_id INT,
    model_id INT,
    color_variant VARCHAR(50),
    current_stock INT DEFAULT 0,
    sold_this_month INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (dealer_id) REFERENCES dealers(dealer_id),
    FOREIGN KEY (model_id) REFERENCES product_models(model_id),
    UNIQUE KEY unique_dealer_model (dealer_id, model_id, color_variant)
);
```

### 2.6 Analytics & Configuration Tables

```sql
-- 23. Demand Forecast
CREATE TABLE demand_forecast (
    forecast_id INT PRIMARY KEY AUTO_INCREMENT,
    model_id INT,
    plant_id INT,
    forecast_month DATE,
    forecasted_quantity INT,
    actual_quantity INT DEFAULT 0,
    variance INT GENERATED ALWAYS AS (actual_quantity - forecasted_quantity) STORED,
    forecast_method VARCHAR(50),
    accuracy_percentage DECIMAL(5,2),
    created_date DATE,
    updated_date DATE,
    FOREIGN KEY (model_id) REFERENCES product_models(model_id),
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id),
    UNIQUE KEY unique_forecast (model_id, plant_id, forecast_month)
);

-- 24. System Configurations
CREATE TABLE system_config (
    config_id INT PRIMARY KEY AUTO_INCREMENT,
    config_key VARCHAR(100) UNIQUE NOT NULL,
    config_value TEXT,
    description TEXT,
    data_type ENUM('string', 'integer', 'decimal', 'boolean', 'date') DEFAULT 'string',
    is_active BOOLEAN DEFAULT TRUE,
    updated_by VARCHAR(100),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 25. User Management
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    email VARCHAR(100),
    role ENUM('Admin', 'Manager', 'Operator', 'Viewer') DEFAULT 'Operator',
    plant_id INT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (plant_id) REFERENCES plants(plant_id)
);

-- 26. Audit Log
CREATE TABLE audit_log (
    log_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    table_name VARCHAR(100),
    record_id INT,
    action ENUM('INSERT', 'UPDATE', 'DELETE'),
    old_values JSON NULL,
    new_values JSON NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    INDEX idx_audit_timestamp (timestamp),
    INDEX idx_audit_table (table_name)
);
```

## 3. Python Application Structure

### 3.1 Project Directory Structure
```
hero_supply_chain/
├── main.py                 # Application entry point
├── config/
│   ├── __init__.py
│   ├── database.py         # Database configuration
│   └── settings.py         # Application settings
├── models/
│   ├── __init__.py
│   ├── base_model.py       # Base model class
│   ├── supplier.py
│   ├── part.py
│   ├── inventory.py
│   ├── production.py
│   └── dealer.py
├── modules/
│   ├── __init__.py
│   ├── procurement.py      # Procurement module
│   ├── production.py       # Production module
│   ├── inventory.py        # Inventory module
│   ├── logistics.py        # Logistics module
│   └── analytics.py        # Analytics module
├── utils/
│   ├── __init__.py
│   ├── database_helper.py  # Database utilities
│   ├── validators.py       # Data validation
│   └── formatters.py       # Output formatting
├── gui/
│   ├── __init__.py
│   ├── main_window.py      # Main GUI window
│   └── dialogs/            # Various dialog boxes
├── reports/
│   ├── __init__.py
│   └── generators.py       # Report generators
└── tests/
    ├── __init__.py
    └── test_modules.py     # Unit tests
```

### 3.2 Core Classes Design

```python
# Example: Base Model Class
class BaseModel:
    def __init__(self, db_connection):
        self.db = db_connection
        self.table_name = None
        self.primary_key = 'id'
    
    def find(self, id):
        # Generic find method
        pass
    
    def save(self):
        # Generic save method
        pass
    
    def delete(self, id):
        # Generic delete method
        pass

# Example: Supplier Model
class Supplier(BaseModel):
    def __init__(self, db_connection):
        super().__init__(db_connection)
        self.table_name = 'suppliers'
        self.primary_key = 'supplier_id'
    
    def get_supplier_performance(self, supplier_id, date_from, date_to):
        # Calculate supplier performance metrics
        pass
    
    def get_parts_by_supplier(self, supplier_id):
        # Get all parts supplied by a supplier
        pass
```

## 4. Detailed Implementation Phases (20 Phases over 24 Weeks)

### **PHASE 1: Environment Setup & Database Foundation (Week 1)**
**Deliverables:**
- MySQL server installation and configuration
- Database creation with proper character sets and collations
- Initial security configuration
- Backup and recovery strategy setup
- Development environment setup (Python, IDEs, version control)

**Tasks:**
- Install MySQL 8.0 on development/production servers
- Create database users with appropriate privileges
- Set up Git repository and branching strategy
- Configure development environments for team members
- Create project directory structure
- Set up virtual environments for Python dependencies

**Success Criteria:**
- Database server accessible and configured
- All developers can connect to database
- Project repository created and accessible
- Development environment standardized across team

---

### **PHASE 2: Core Database Schema Creation (Week 1-2)**
**Deliverables:**
- All 26 database tables created
- Proper indexes and constraints implemented
- Initial data seeding scripts
- Database documentation

**Tasks:**
- Create master data tables (suppliers, parts, products, plants, dealers)
- Implement foreign key relationships
- Add indexes for performance optimization
- Create stored procedures for common operations
- Develop data seeding scripts with sample data
- Generate database schema documentation

**Success Criteria:**
- All tables created without errors
- Foreign key relationships working correctly
- Sample data loaded successfully
- Performance benchmarks met for basic queries

---

### **PHASE 3: Core Infrastructure & Utilities (Week 2)**
**Deliverables:**
- Database connection management
- Base model classes
- Validation framework
- Logging system
- Configuration management

**Tasks:**
```python
# Key components to develop:
- DatabaseConnection class with connection pooling
- BaseModel class with CRUD operations
- ValidationHelper for data validation
- Logger configuration for application logging
- ConfigManager for application settings
- ErrorHandler for exception management
```

**Success Criteria:**
- Database connections stable under load
- Base CRUD operations working for all tables
- Validation rules enforced
- Comprehensive logging implemented

---

### **PHASE 4: User Management & Authentication (Week 3)**
**Deliverables:**
- User registration and login system
- Role-based access control
- Session management
- Password security implementation

**Tasks:**
- Implement user authentication with password hashing
- Create role-based permission system
- Develop session management
- Build user management interface
- Implement password reset functionality
- Create audit logging for user actions

**Success Criteria:**
- Secure user authentication working
- Role-based access properly restricting features
- Session management preventing unauthorized access
- Audit trail capturing user activities

---

### **PHASE 5: Supplier Master Data Management (Week 3-4)**
**Deliverables:**
- Supplier CRUD operations
- Supplier performance tracking
- Supplier-parts relationship management
- Supplier onboarding workflow

**Tasks:**
- Create Supplier model and controller
- Implement supplier registration form
- Build supplier search and filtering
- Develop supplier performance calculation
- Create supplier-parts mapping interface
- Implement supplier rating system

**Success Criteria:**
- Suppliers can be added, updated, deleted
- Supplier performance metrics calculated correctly
- Supplier-parts relationships managed properly
- Search and filtering working efficiently

---

### **PHASE 6: Parts & Product Master Management (Week 4)**
**Deliverables:**
- Parts catalog management
- Product models and variants
- Bill of Materials (BOM) management
- Parts categorization system

**Tasks:**
- Create Parts model with full specifications
- Implement product models management
- Build BOM creation and management interface
- Develop parts categorization system
- Create parts search with filters
- Implement parts import from Excel

**Success Criteria:**
- Parts catalog fully functional
- BOM creation and modification working
- Parts search and filtering efficient
- Excel import/export operational

---

### **PHASE 7: Plant & Dealer Master Management (Week 4-5)**
**Deliverables:**
- Plant management system
- Dealer network management
- Capacity planning for plants
- Territory management for dealers

**Tasks:**
- Create Plant model with capacity information
- Implement dealer registration and management
- Build plant capacity planning tools
- Develop dealer territory assignment
- Create plant performance tracking
- Implement dealer credit limit management

**Success Criteria:**
- Plant information managed effectively
- Dealer network properly organized
- Capacity planning tools functional
- Territory assignments working correctly

---

### **PHASE 8: Basic Inventory Framework (Week 5)**
**Deliverables:**
- Inventory tracking foundation
- Stock movement recording
- Basic stock queries
- Location-wise inventory

**Tasks:**
- Create Inventory model for all locations
- Implement stock movement recording
- Build basic inventory queries
- Develop stock level monitoring
- Create inventory adjustment functionality
- Implement basic reporting for stock levels

**Success Criteria:**
- Inventory levels tracked accurately
- Stock movements recorded properly
- Basic inventory reports generated
- Stock adjustments working correctly

---

### **PHASE 9: Purchase Order Creation & Management (Week 6)**
**Deliverables:**
- Purchase order creation system
- PO approval workflow
- Supplier selection logic
- PO status tracking

**Tasks:**
- Create PurchaseOrder model and interface
- Implement PO creation with line items
- Build approval workflow
- Develop supplier selection based on performance
- Create PO status tracking
- Implement PO modification capabilities

**Success Criteria:**
- Purchase orders created successfully
- Approval workflow functioning
- Supplier selection logic working
- Status tracking accurate

---

### **PHASE 10: Goods Receipt & Quality Control (Week 6-7)**
**Deliverables:**
- Goods Receipt Note (GRN) processing
- Quality inspection workflow
- Supplier performance updates
- Inventory updates from receipts

**Tasks:**
- Create GoodsReceipt model and processing
- Implement quality inspection workflow
- Build supplier performance calculation
- Develop automatic inventory updates
- Create receipt discrepancy handling
- Implement quality rejection process

**Success Criteria:**
- GRN processing working smoothly
- Quality checks properly recorded
- Inventory updated automatically
- Supplier performance calculated correctly

---

### **PHASE 11: Auto-Reorder & Procurement Intelligence (Week 7)**
**Deliverables:**
- Automatic reorder point monitoring
- Smart reorder quantity calculation
- Supplier selection optimization
- Procurement alerts system

**Tasks:**
- Implement reorder level monitoring
- Create smart reorder quantity calculations
- Build supplier selection optimization
- Develop procurement alert system
- Create emergency procurement workflow
- Implement lead time optimization

**Success Criteria:**
- Reorder points monitored automatically
- Optimal quantities calculated correctly
- Best suppliers selected automatically
- Timely alerts generated for procurement team

---

### **PHASE 12: Production Planning & Scheduling (Week 8)**
**Deliverables:**
- Production order creation
- Capacity-based scheduling
- Material requirement planning
- Production priority management

**Tasks:**
- Create ProductionOrder model and interface
- Implement capacity-based scheduling
- Build material requirement calculation
- Develop production priority system
- Create production calendar management
- Implement shift planning

**Success Criteria:**
- Production orders scheduled efficiently
- Material requirements calculated accurately
- Capacity constraints respected
- Priority system working effectively

---

### **PHASE 13: Production Execution & Tracking (Week 8-9)**
**Deliverables:**
- Work-in-progress tracking
- Production stage monitoring
- Material consumption recording
- Real-time production status

**Tasks:**
- Implement WIP tracking across stages
- Create production stage monitoring
- Build material consumption recording
- Develop real-time status updates
- Create production efficiency tracking
- Implement bottleneck identification

**Success Criteria:**
- WIP accurately tracked through all stages
- Material consumption properly recorded
- Real-time status updates working
- Production efficiency calculated correctly

---

### **PHASE 14: Quality Control & Compliance (Week 9)**
**Deliverables:**
- Quality checkpoint system
- Defect tracking and analysis
- Quality metrics calculation
- Compliance reporting

**Tasks:**
- Create quality checkpoint workflow
- Implement defect recording and categorization
- Build quality metrics dashboard
- Develop compliance reporting
- Create corrective action tracking
- Implement quality trend analysis

**Success Criteria:**
- Quality checkpoints enforced
- Defects properly categorized and tracked
- Quality metrics accurate
- Compliance reports generated correctly

---

### **PHASE 15: Advanced Inventory Management (Week 10)**
**Deliverables:**
- Advanced inventory analytics
- ABC analysis implementation
- Inventory optimization
- Multi-location transfers

**Tasks:**
- Implement ABC analysis for parts
- Create inventory optimization algorithms
- Build inter-plant transfer system
- Develop inventory aging analysis
- Create inventory valuation methods
- Implement cycle counting system

**Success Criteria:**
- ABC analysis providing actionable insights
- Inventory levels optimized
- Inter-plant transfers working smoothly
- Inventory valuation accurate

---

### **PHASE 16: Shipment Planning & Logistics (Week 11)**
**Deliverables:**
- Shipment creation and planning
- Route optimization
- Carrier management
- Logistics cost tracking

**Tasks:**
- Create Shipment model and planning interface
- Implement basic route optimization
- Build carrier performance tracking
- Develop logistics cost allocation
- Create shipment consolidation logic
- Implement delivery scheduling

**Success Criteria:**
- Shipments planned and tracked effectively
- Routes optimized for cost and time
- Carrier performance monitored
- Logistics costs tracked accurately

---

### **PHASE 17: Dealer Order Management (Week 11-12)**
**Deliverables:**
- Dealer order processing system
- Order allocation optimization
- Dealer inventory tracking
- Credit limit management

**Tasks:**
- Create dealer order processing workflow
- Implement order allocation based on availability
- Build dealer inventory tracking
- Develop credit limit enforcement
- Create dealer performance analytics
- Implement order priority management

**Success Criteria:**
- Dealer orders processed efficiently
- Allocation optimization working
- Dealer inventories tracked accurately
- Credit limits properly enforced

---

### **PHASE 18: Distribution & Delivery Tracking (Week 12)**
**Deliverables:**
- Real-time shipment tracking
- Delivery confirmation system
- Exception handling
- Customer satisfaction tracking

**Tasks:**
- Implement shipment status tracking
- Create delivery confirmation workflow
- Build exception alert system
- Develop customer satisfaction surveys
- Create delivery performance metrics
- Implement proof of delivery system

**Success Criteria:**
- Shipment status updated in real-time
- Deliveries confirmed properly
- Exceptions handled promptly
- Performance metrics accurate

---

### **PHASE 19: Analytics Dashboard & Basic Reporting (Week 13)**
**Deliverables:**
- Executive dashboard
- Operational reports
- Performance KPIs
- Trend analysis

**Tasks:**
- Create executive summary dashboard
- Build operational performance reports
- Implement KPI calculations
- Develop trend analysis charts
- Create drill-down capabilities
- Implement scheduled report generation

**Success Criteria:**
- Dashboard providing clear insights
- Reports generated accurately
- KPIs calculated correctly
- Trend analysis helpful for decision-making

---

### **PHASE 20: Advanced Analytics & Forecasting (Week 13-14)**
**Deliverables:**
- Demand forecasting system
- Predictive analytics
- What-if scenario analysis
- Advanced performance metrics

**Tasks:**
- Implement demand forecasting algorithms
- Create predictive maintenance alerts
- Build scenario planning tools
- Develop advanced performance metrics
- Create machine learning integration framework
- Implement statistical analysis tools

**Success Criteria:**
- Demand forecasts reasonably accurate
- Predictive insights actionable
- Scenario analysis functional
- Advanced metrics providing value

---

### **PHASE 21: System Integration & API Development (Week 15)**
**Deliverables:**
- REST API for external integrations
- Data import/export capabilities
- Third-party system connectors
- Mobile app backend support

**Tasks:**
- Create RESTful API endpoints
- Implement data import/export utilities
- Build connector framework for ERP systems
- Develop mobile app backend
- Create API documentation
- Implement API security and rate limiting

**Success Criteria:**
- APIs working reliably
- Data exchange with external systems
- Mobile backend functional
- Integration framework scalable

---

### **PHASE 22: User Interface Enhancement (Week 16)**
**Deliverables:**
- Enhanced GUI/Web interface
- Mobile-responsive design
- User experience improvements
- Accessibility features

**Tasks:**
- Enhance user interface design
- Implement mobile-responsive layouts
- Improve user experience flows
- Add accessibility features
- Create user help system
- Implement keyboard shortcuts

**Success Criteria:**
- Interface intuitive and user-friendly
- Mobile responsiveness working
- Accessibility standards met
- User productivity improved

---

### **PHASE 23: Comprehensive Testing (Week 17-18)**
**Deliverables:**
- Complete test suite
- Performance testing results
- Security testing completion
- Bug fixes and optimizations

**Tasks:**
- Create comprehensive unit tests
- Perform integration testing
- Execute performance testing
- Conduct security testing
- Perform user acceptance testing
- Fix identified bugs and issues

**Success Criteria:**
- All critical functions tested
- Performance benchmarks met
- Security vulnerabilities addressed
- User acceptance criteria satisfied

---

### **PHASE 24: Production Deployment & Go-Live (Week 19-20)**
**Deliverables:**
- Production environment setup
- Data migration completion
- User training materials
- Go-live support

**Tasks:**
- Set up production environment
- Migrate data from existing systems
- Conduct user training sessions
- Create user documentation
- Implement monitoring and alerting
- Provide go-live support

**Success Criteria:**
- Production environment stable
- Data migration successful
- Users trained and confident
- System monitoring operational

---

### **PHASE 25: Post-Deployment Support & Optimization (Week 21-24)**
**Deliverables:**
- System monitoring and maintenance
- Performance optimization
- User feedback incorporation
- Enhancement planning

**Tasks:**
- Monitor system performance
- Optimize based on usage patterns
- Collect and analyze user feedback
- Plan future enhancements
- Create maintenance procedures
- Document lessons learned

**Success Criteria:**
- System running smoothly in production
- Performance optimized based on real usage
- User satisfaction high
- Future roadmap established

## 5. Key Features Implementation

### 5.1 Auto-Reorder System
```python
def check_reorder_levels():
    """
    Automatically check inventory levels and create purchase orders
    """
    # Check parts below reorder level
    # Calculate required quantity based on demand forecast
    # Create purchase orders for preferred suppliers
    # Send notifications to procurement team
```

### 5.2 Production Planning
```python
def create_production_schedule():
    """
    Create optimized production schedule based on:
    - Dealer orders
    - Demand forecast
    - Available inventory
    - Plant capacity
    """
```

### 5.3 Real-time Tracking
```python
def update_shipment_status():
    """
    Update shipment status and notify stakeholders
    """
    # GPS tracking integration (future)
    # Automatic ETA calculation
    # Exception alerts for delays
```

## 6. Performance Optimization

### 6.1 Database Indexing Strategy
- Primary keys: Auto-indexed
- Foreign keys: Indexed for joins
- Frequently queried columns: Custom indexes
- Composite indexes for multi-column queries

### 6.2 Query Optimization
- Use prepared statements
- Implement connection pooling
- Cache frequently accessed data
- Paginate large result sets

### 6.3 Data Archiving
- Archive old transactions quarterly
- Maintain summary tables for analytics
- Implement data retention policies

## 7. Security Considerations

### 7.1 User Access Control
- Role-based access control (RBAC)
- Plant-specific data access
- Audit logging for all operations
- Session management

### 7.2 Data Protection
- Input validation and sanitization
- SQL injection prevention
- Encrypted password storage
- Secure configuration management

## 8. Integration Possibilities

### 8.1 Current Integrations
- Email notifications
- SMS alerts for critical issues
- Excel import/export functionality

### 8.2 Future Integrations
- IoT sensors for machine monitoring
- GPS tracking for logistics
- ERP system integration
- Mobile app for field operations
- AI-based demand forecasting

This comprehensive plan provides a solid foundation for Hero MotoCorp's supply chain management system with scalability and future enhancements in mind.