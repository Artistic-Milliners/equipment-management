# Graph Report - ems  (2026-10-01)

## Corpus Check
- Large corpus: 555 files · ~2,768,236 words. Semantic extraction will be expensive (many Claude tokens). Consider running on a subfolder.

## Summary
- 806 nodes · 1362 edges · 77 communities (42 shown, 35 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 218 edges (avg confidence: 0.91)
- Token cost: 512,721 input · 0 output

## Community Hubs (Navigation)
- Django Admin Forms
- Database Migrations
- Inventory Role Permissions
- Complaint Lifecycle Rules
- User Portal Templates
- JWT Auth API
- Ticket Status & Fixes
- Production Hardening
- Core Org Models
- Django Framework Imports
- Group Admin Commands
- App Config & Signals
- Temporary Issue Review
- Spares Stock Commands
- Excel Inventory Import
- Maintenance Complaint Views
- MachineIssue Model
- Spare Issuance UI
- Tracking & Review Views
- Docker & Bootstrap
- Spare Transaction Ledger
- Core Serializers & Filters
- Machine CRUD Views
- CSV Export
- Machine Spare Filtering
- Review Unique Constraint
- Manufacturer Tests
- Machine/Issue APIs
- Inventory System Summary
- 3-Column Ticket View
- Item Codes & Duplicates
- Modal & 500 Fixes
- Tiered Access Control
- UnitID Custom Field
- Unit Form & Command
- Work Sessions & Quick Review
- Closed Complaints Archive
- Inventory Improvements
- List Views
- Docker Setup Guide
- Frontend Dependencies
- Machine Issue Approval
- Machine Section API
- Machine Hours API
- Stock Receiving Docs
- Karachi Timezone Fix
- Complaint Slideshow JS
- Misc Command A
- Misc Command B
- Ticket Filter JS
- Docker Entrypoint
- Login Page
- Session Timer

## God Nodes (most connected - your core abstractions)
1. `Spares` - 43 edges
2. `MachineIssue` - 43 edges
3. `Machines` - 28 edges
4. `ComplainClosingView` - 25 edges
5. `SpareTransaction` - 23 edges
6. `Employee` - 22 edges
7. `Equipment` - 22 edges
8. `CustomUser` - 18 edges
9. `home.html (User dashboard)` - 16 edges
10. `ComplainReviewView` - 15 edges

## Surprising Connections (you probably didn't know these)
- `Closing Form Redirect Fix` --references--> `ComplainClosingView`  [EXTRACTED]
  docs/CLOSING_REDIRECT_FIX.md → User/views.py
- `File Upload Validation (core/validators.py) (CRITICAL-5)` --references--> `ComplainClosingView`  [EXTRACTED]
  docs/PRODUCTION_READINESS.md → User/views.py
- `Home Page Beautification` --references--> `home()`  [EXTRACTED]
  docs/SESSION_SUMMARY.md → User/views.py
- `/api/ticket-detail/<pk>/ endpoint` --references--> `TicketDetailAPIView`  [EXTRACTED]
  docs/NEW_COMPLAIN_VIEW_GUIDE.md → api/views.py
- `Manufacturer` --implements--> `Manufacturer Standardization`  [EXTRACTED]
  core/models.py → docs/INVENTORY_IMPROVEMENTS.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Complaint lifecycle UI flow (initiate -> track/feedback -> close -> archive)** — user_templates_user_initiate_complain, user_templates_user_complain_tracking, user_templates_user_complain_tracking_user_feedback_form, user_templates_user_complain_closing, user_templates_user_closedcomplainlist [INFERRED 0.85]
- **Machine management pages** — user_templates_user_add_machine, user_templates_user_machine_detail, user_templates_user_update_machine, user_templates_user_sidebar [INFERRED 0.85]
- **EMS Docker stack (db, web, nginx)** — docker_compose_db, docker_compose_web, docker_compose_nginx, docker_compose_prod_web, docker_compose_prod_nginx [EXTRACTED 1.00]
- **Complaint lifecycle UI flow (view -> quick review -> review form -> approval -> archive)** — maintenance_templates_maintenance_complain_view, maintenance_templates_maintenance_quick_review, maintenance_templates_maintenance_complain_form, maintenance_templates_maintenance_complain_detail, maintenance_templates_maintenance_closed_complaints [INFERRED 0.85]
- **Quick resolution + user acknowledgment + closing path** — maintenance_templates_maintenance_quick_review, user_views_user_close_complaint, user_views_complainclosingview, docs_closing_form_review_fix_minimal_review_autocreate, docs_acknowledgment_integration_status_progression [INFERRED 0.85]
- **Spare inventory system features** — docs_complete_inventory_system_summary_auto_item_codes, docs_complete_inventory_system_summary_transaction_ledger, docs_complete_inventory_system_summary_manufacturer_standardization, docs_complete_inventory_modals_machine_search, docs_check_inventory_setup_sparetransaction [INFERRED 0.85]
- **Inventory operations that write SpareTransaction audit records** — user_views_spare_add, user_views_spare_issue, user_views_spare_receive, user_views_spare_update, core_management_commands_import_spares_excel, core_models_sparetransaction [INFERRED 0.85]
- **Inventory role-based access control (groups, decorator, template filter, setup command)** — docs_inventory_controller_group, docs_engineering_group, docs_management_group, user_decorators_inventory_controller_restricted, user_templatetags_user_tags_is_inventory_controller, core_management_commands_setup_inventory_groups [INFERRED 0.85]
- **Engineer ticket review-to-documentation workflow** — docs_ticket_status_workflow, docs_ticket_status_awaiting_documentation, docs_ticket_status_under_observation, user_views_complainreviewview, user_views_complainclosingview, maintenance_templates_maintenance_complain_view [INFERRED 0.85]
- **Complaint closure enforcement (review required, smart redirects, user acknowledgment)** — docs_new_complaint_workflow_review_required_before_closing, docs_new_complaint_workflow_validate_status_transition, docs_workflow_summary_smart_redirects, docs_user_acknowledgment_todo_user_acknowledgment_system, docs_test_scenario_user_close_complaint, docs_new_complaint_workflow_quick_review [INFERRED 0.85]
- **Inventory stock movement audit trail** — docs_stock_receiving_and_ledger_receive_stock, docs_stock_receiving_and_ledger_transaction_ledger, docs_stock_receiving_and_ledger_transaction_types, docs_quick_csv_export_test_csv_export_feature, docs_modal_timing_fix_issueitem, docs_timezone_fix_applied_backend_pkt_conversion [INFERRED 0.85]
- **Group/permission-based access control layers** — docs_tiered_access_system_tiered_access_control, docs_setup_permissions_now_inventory_permission_tiers, docs_quick_access_restriction_setup_inventory_controller_restriction, docs_ticket_filtering_system_role_based_ticket_filtering, docs_new_complain_view_guide_role_based_action_buttons [INFERRED 0.75]

## Communities (77 total, 35 thin omitted)

### Community 0 - "Django Admin Forms"
Cohesion: 0.05
Nodes (36): ContractorCreationForm, ContratorCreation, CustomGroupAdmin, CustomUserAdmin, DepartmentCreation, DepartmentCreationForm, DesignationCreation, DesignationCreationForm (+28 more)

### Community 1 - "Database Migrations"
Cohesion: 0.05
Nodes (19): Migration, Migration, Migration, Migration, Migration, Migration, Migration, Migration (+11 more)

### Community 2 - "Inventory Role Permissions"
Cohesion: 0.06
Nodes (13): Engineering group, Inventory Controller Access Restriction Doc, Inventory Controller group, Inventory Permissions Setup Guide, Management group, Management Permissions Setup Doc, Engineering Management group, inventory_controller_restricted() (+5 more)

### Community 3 - "Complaint Lifecycle Rules"
Cohesion: 0.08
Nodes (15): IssueClosing, Closing Form Missing Review Fix, New Complaint Workflow Doc, Complaint Status Lifecycle (PENDING to CLOSED), Engineer Quick Review (Triage), validate_status_transition(), Test Scenario - Complete Workflow, Resolution Status Field in Review Form (+7 more)

### Community 4 - "User Portal Templates"
Cohesion: 0.07
Nodes (30): Department Change Troubleshooting Doc, Department CASCADE Delete Issue, Employee-User Account Link, fix_employee_links management command, Tracking Page Debug Output (ComplainTrackingView), Home Page Improvements Doc, Recent Activity Feed, Dashboard Statistics Cards (+22 more)

### Community 5 - "JWT Auth API"
Cohesion: 0.09
Nodes (9): UserLoginSerializer, generateToken(), jwt_required(), HomeAPIView, TicketDetailAPIView, UserLoginAPIView, UserTokenRefreshAPIView, Command (+1 more)

### Community 6 - "Ticket Status & Fixes"
Cohesion: 0.07
Nodes (27): validate_status_transition(), User Acknowledgment Integration, Ticket Status Progression (RESOLVED -> AWAITING_DOCUMENTATION -> CLOSED), API 500 Error Fix - Ticket Details, /api/ticket-detail/<pk>/ endpoint, Closing Form Redirect Fix, Complain View Empty List Fix, Documentation Button for Engineers Doc (+19 more)

### Community 7 - "Production Hardening"
Cohesion: 0.06
Nodes (11): Migration, Production Readiness Guide, Restrict ALLOWED_HOSTS (CRITICAL-3), Secure API Endpoints (CRITICAL-6), DEBUG Mode Disable (CRITICAL-2), File Upload Validation (core/validators.py) (CRITICAL-5), Hardcoded Secrets Vulnerability (CRITICAL-1), Operational Hardening (pooling, health checks, backups, monitoring) (+3 more)

### Community 8 - "Core Org Models"
Cohesion: 0.07
Nodes (13): Contractor, Contractor_Person, CustomUser, Department, Designation, Employee, Equipment, IssueList (+5 more)

### Community 9 - "Django Framework Imports"
Cohesion: 0.08
Nodes (5): CreateUnitView, DetailUserView, index(), spare_delete(), spare_view()

### Community 10 - "Group Admin Commands"
Cohesion: 0.11
Nodes (6): Command, Command, Command, assign_permission(), create_group(), create_permission()

### Community 11 - "App Config & Signals"
Cohesion: 0.10
Nodes (7): ApiConfig, CoreConfig, Contractor_Person, create_employee(), ticket(), MaintenanceConfig, UserConfig

### Community 12 - "Temporary Issue Review"
Cohesion: 0.15
Nodes (7): Employee, IssueList, TemporaryIssue, start_working(), temporary_issue_review_detail(), temporary_issue_review_list(), InitiateComplainView

### Community 13 - "Spares Stock Commands"
Cohesion: 0.13
Nodes (4): Command, Command, Command, Spares

### Community 15 - "Excel Inventory Import"
Cohesion: 0.20
Nodes (5): Excel Import System Guide, INVENTORY_IMPORT_TEMPLATE.xlsx, openpyxl, Excel Import Quick Start, Final Inventory System Complete Doc

### Community 16 - "Maintenance Complaint Views"
Cohesion: 0.19
Nodes (8): Equipment, ImageModel, complain_approve(), complain_delete(), complain_detail(), complain_edit(), get_machines(), side_bar()

### Community 17 - "MachineIssue Model"
Cohesion: 0.16
Nodes (3): MachineIssue, downtime_report(), user_close_complaint()

### Community 18 - "Spare Issuance UI"
Cohesion: 0.18
Nodes (13): Stock Status & Low-Stock Alerts, Issue Item Troubleshooting Guide, Cookie-based CSRF token (getCookie), Work Order lookup by ID or ticket_num, Item Issuance Improvements Doc, Issue Item Modal, Machine & Work Order Linking, Real-Time Stock Impact Warnings (+5 more)

### Community 19 - "Tracking & Review Views"
Cohesion: 0.17
Nodes (9): Proper Logging System (HIGH-1), Session Summary - EMS Improvements, MachineIssue date_time auto_now Fix, Engineer Workflow Enhancements (doc filters, duplicate review fix), Home Page Beautification, Ticket Tracking Page Fix, Missing select_related() on ComplainTrackingView, ComplainReviewView (+1 more)

### Community 20 - "Docker & Bootstrap"
Cohesion: 0.23
Nodes (6): db service (postgres:15-alpine), nginx reverse proxy service, prod nginx service (Dockerfile.nginx), prod web service (.env.prod, ENV_STATE=prod), web service (Django runserver), requirements.txt (Django 5.0.1, DRF, psycopg2, gunicorn, PyJWT)

### Community 21 - "Spare Transaction Ledger"
Cohesion: 0.20
Nodes (8): SpareTransactionInline, SpareTransaction, exportLedger() JS, Stock Receiving System, Transaction Export Fix, TRANSACTION_TYPE_CHOICES vs TRANSACTION_TYPES AttributeError, export_spare_transactions_csv(), spare_receive()

### Community 22 - "Core Serializers & Filters"
Cohesion: 0.27
Nodes (7): Department, DepartmentSerializer, EmployeeSerializer, IssueSerializer, meta, UserSerializer, filterTicketAPIView

### Community 23 - "Machine CRUD Views"
Cohesion: 0.18
Nodes (8): Machines, MachineSpares, delete_machine(), edit_machine(), machine_detail(), spare_add(), spare_update(), update_machine()

### Community 24 - "CSV Export"
Cohesion: 0.24
Nodes (10): CSV Export Feature Doc, exportInventory() JS, Full Inventory CSV Export, Karachi Local Time (UTC+5), Spare Transaction Types (RECEIPT/ISSUE/ADJUSTMENT/RETURN/DAMAGE), Transaction History CSV Export, CSV Export Fix Doc, Spares.location AttributeError (+2 more)

### Community 25 - "Machine Spare Filtering"
Cohesion: 0.24
Nodes (10): General Purpose Spare (no machine link), Machine Filter Feature Doc, filterItems() JS, Filter by Machine dropdown, updateFilterSummary() JS, Machine Search Feature Doc, Select All Visible / Clear Selection, filterMachines() JS (+2 more)

### Community 26 - "Review Unique Constraint"
Cohesion: 0.22
Nodes (4): Command, MachineIssueReview, core_machineissuereview_issue_id_key unique constraint, Migration Fix Steps Doc

### Community 28 - "Machine/Issue APIs"
Cohesion: 0.25
Nodes (4): MachineCodeSerializer, IssueListAPIView, MachineCodeAPIView, UserDetailAPIView

### Community 29 - "Inventory System Summary"
Cohesion: 0.28
Nodes (9): Check Inventory Setup, fix_spare_item_codes management command, SpareTransaction model, Complete Inventory Modals Summary, Machine Search Selector (Add/Edit/Issue modals), Complete Inventory Management System Summary, Auto-Generated Item Codes (ELE-0001 etc.), Manufacturer Standardization (+1 more)

### Community 30 - "3-Column Ticket View"
Cohesion: 0.25
Nodes (9): New 3-Column Complain View Guide, Client-Side Ticket Filtering, Role-Based Action Buttons, 3-Column Ticket Management View, /api/ticket-detail/<pk>/ endpoint, Ticket Filtering System by User Role, Role-Based Ticket Filtering (Approvers/Engineers/Users), setup_approval_groups management command (+1 more)

### Community 31 - "Item Codes & Duplicates"
Cohesion: 0.33
Nodes (9): Inventory Quick Reference Card, Category-Prefixed Item Code System (ELE/MEC/HYD/PNE/SAF/GEN), Stock Status Levels (In/Low/Out of Stock), Spares Form Update Summary, Live Duplicate Detection for Spares, Manufacturer Standardization (FK + part number), Today's Complete Summary - Inventory Management, Excel Bulk Import (import_spares_excel) (+1 more)

### Community 32 - "Modal & 500 Fixes"
Cohesion: 0.25
Nodes (7): Modal Timing Fix Doc, editItem() JS function, issueItem() JS function, Quick Fix: 500 Error When Issuing Items, fix_spare_item_codes management command, Unapplied Migrations Cause (core_sparetransaction missing), Transaction Types (RECEIPT/ISSUE/ADJUSTMENT/RETURN/DAMAGE)

### Community 33 - "Tiered Access Control"
Cohesion: 0.32
Nodes (8): Quick Access Restriction Setup, Inventory Controller Access Restriction, Setup Inventory Permissions Guide, Inventory Permission Tiers (Controller full, Engineering/Management view-only), setup_inventory_groups management command, Tiered Access Control System Doc, setup_tiered_permissions management command, Tiered Access Control (All Users/Engineering/Management)

### Community 35 - "Unit Form & Command"
Cohesion: 0.33
Nodes (4): Command, Unit, meta, UnitForm

### Community 36 - "Work Sessions & Quick Review"
Cohesion: 0.33
Nodes (4): Meta, QuickReviewComments, WorkSession, quick_review()

### Community 37 - "Closed Complaints Archive"
Cohesion: 0.29
Nodes (5): Closed Complaints Archive Guide, Engineer/Approver Role Access Control, Critical Date Time Field Fix, Closed Complaints Archive, closed_complaints_archive()

### Community 38 - "Inventory Improvements"
Cohesion: 0.29
Nodes (6): Edit Modal Update Doc, Edit Inventory Item Modal, Import Duplicate Handling (--skip-duplicates), Inventory Management System Improvements Doc, Spare Duplicate Detection (fuzzy matching), Manufacturer Standardization

### Community 39 - "List Views"
Cohesion: 0.29
Nodes (4): ApprovalListView, ClosedComplainListView, ListUnitView, ListUsers

### Community 41 - "Docker Setup Guide"
Cohesion: 0.53
Nodes (6): EMS Docker Setup Guide, db service (PostgreSQL 15), .env environment configuration, nginx service (reverse proxy), postgres_data volume, web service (Django + Gunicorn)

### Community 42 - "Frontend Dependencies"
Cohesion: 0.33
Nodes (5): dependencies, jquery, @selectize/selectize, jquery, @selectize/selectize

### Community 47 - "Stock Receiving Docs"
Cohesion: 0.40
Nodes (5): Quick CSV Export Test Guide, Inventory & Transaction CSV Export, Stock Receiving and Transaction Ledger Doc, Receive Stock Modal / spare_receive, Spare Transaction Ledger (audit trail)

### Community 48 - "Karachi Timezone Fix"
Cohesion: 0.50
Nodes (5): Timezone Fix Applied - Karachi Time, Backend UTC to Asia/Karachi Conversion (pytz), formatDateTimePKT() JS function, Timezone Fix - Karachi (initial frontend approach), Frontend Intl timeZone Asia/Karachi Formatting

### Community 50 - "Complaint Slideshow JS"
Cohesion: 0.60
Nodes (3): currentSlide(), plusSlides(), showSlides()

## Ambiguous Edges - Review These
- `setup_inventory_groups.py` → `setup_inventory_permissions.py`  [AMBIGUOUS]
  docs/MANAGEMENT_PERMISSIONS_SETUP.md · relation: semantically_similar_to
- `Inventory Permissions Setup Guide` → `Management Permissions Setup Doc`  [AMBIGUOUS]
  docs/MANAGEMENT_PERMISSIONS_SETUP.md · relation: conceptually_related_to
- `Proper Logging System (HIGH-1)` → `Session Summary - EMS Improvements`  [AMBIGUOUS]
  docs/PRODUCTION_READINESS.md · relation: conceptually_related_to
- `Inventory Permission Tiers (Controller full, Engineering/Management view-only)` → `Tiered Access Control (All Users/Engineering/Management)`  [AMBIGUOUS]
  docs/SETUP_PERMISSIONS_NOW.md · relation: conceptually_related_to
- `User Acknowledgment System Implementation Plan` → `Automatic Smart Redirects (closing <-> review)`  [AMBIGUOUS]
  docs/WORKFLOW_SUMMARY.md · relation: conceptually_related_to

## Knowledge Gaps
- **71 isolated node(s):** `meta`, `UserInline`, `Meta`, `Migration`, `Migration` (+66 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 306 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `setup_inventory_groups.py` and `setup_inventory_permissions.py`?**
  _Edge tagged AMBIGUOUS (relation: semantically_similar_to) - confidence is low._
- **What is the exact relationship between `Inventory Permissions Setup Guide` and `Management Permissions Setup Doc`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Proper Logging System (HIGH-1)` and `Session Summary - EMS Improvements`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Inventory Permission Tiers (Controller full, Engineering/Management view-only)` and `Tiered Access Control (All Users/Engineering/Management)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `User Acknowledgment System Implementation Plan` and `Automatic Smart Redirects (closing <-> review)`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Spares` connect `Spares Stock Commands` to `Django Admin Forms`, `Inventory Role Permissions`, `Complaint Lifecycle Rules`, `Django Framework Imports`, `Permission Setup Commands`, `Excel Inventory Import`, `Maintenance Complaint Views`, `Spare Issuance UI`, `Tracking & Review Views`, `Spare Transaction Ledger`, `Machine CRUD Views`, `CSV Export`, `Review Unique Constraint`, `Manufacturer Tests`, `Item Codes & Duplicates`, `Unit Form & Command`, `Work Sessions & Quick Review`, `Inventory Improvements`, `Model Save Overrides`, `Misc Command A`?**
  _High betweenness centrality (0.141) - this node is a cross-community bridge._
- **Why does `MachineIssue` connect `MachineIssue Model` to `Django Admin Forms`, `Complaint Lifecycle Rules`, `Work Sessions & Quick Review`, `JWT Auth API`, `Closed Complaints Archive`, `List Views`, `Model Save Overrides`, `Django Framework Imports`, `Group Admin Commands`, `App Config & Signals`, `Machine Issue Approval`, `Temporary Issue Review`, `Permission Setup Commands`, `Maintenance Complaint Views`, `Tracking & Review Views`, `User Portal Templates`, `Core Serializers & Filters`, `3-Column Ticket View`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._