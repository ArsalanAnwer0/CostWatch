#!/bin/bash

# CostWatch Database Initialization Script
# This script sets up the complete CostWatch database

set -e  # Exit on any error

# Configuration
DB_NAME="costwatch_db"
DB_USER="costwatch_user"
DB_PASSWORD="costwatch_pass123"
DB_HOST="localhost"
DB_PORT="5432"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if PostgreSQL is running
check_postgres() {
    log "Checking PostgreSQL connection..."
    if ! pg_isready -h "$DB_HOST" -p "$DB_PORT" > /dev/null 2>&1; then
        error "PostgreSQL is not running or not accessible on $DB_HOST:$DB_PORT"
        echo "Please ensure PostgreSQL is running and accessible."
        exit 1
    fi
    success "PostgreSQL is running"
}

# Create database and user if they don't exist
create_database() {
    log "Creating database and user..."
    
    # Create user if it doesn't exist
    if ! psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1; then
        log "Creating user: $DB_USER"
        psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "CREATE USER $DB_USER WITH ENCRYPTED PASSWORD '$DB_PASSWORD';"
        success "User $DB_USER created"
    else
        warning "User $DB_USER already exists"
    fi
    
    # Create database if it doesn't exist
    if ! psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
        log "Creating database: $DB_NAME"
        psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"
        success "Database $DB_NAME created"
    else
        warning "Database $DB_NAME already exists"
    fi
    
    # Grant privileges
    psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Set environment variables for psql
    export PGPASSWORD="$DB_PASSWORD"
    
    # Check if migration directory exists
    if [ ! -d "database/migrations" ]; then
        error "Migration directory 'database/migrations' not found"
        echo "Please run this script from the project root directory"
        exit 1
    fi
    
    # Run the initial setup migration
    if [ -f "database/migrations/001_initial_setup.sql" ]; then
        log "Running initial setup migration..."
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "database/migrations/001_initial_setup.sql"
        success "Initial setup migration completed"
    else
        error "Migration file 'database/migrations/001_initial_setup.sql' not found"
        exit 1
    fi
    
    unset PGPASSWORD
}

# Verify database setup
verify_setup() {
    log "Verifying database setup..."
    
    export PGPASSWORD="$DB_PASSWORD"
    
    # Check if core tables exist
    TABLES=("organizations" "users" "aws_accounts" "aws_resources" "cost_data" "alerts" "alert_rules")
    
    for table in "${TABLES[@]}"; do
        if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT to_regclass('$table');" | grep -q "$table"; then
            success "Table '$table' exists"
        else
            error "Table '$table' not found"
            exit 1
        fi
    done
    
    # Check if sample data exists
    ORG_COUNT=$(psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -tAc "SELECT COUNT(*) FROM organizations;")
    if [ "$ORG_COUNT" -gt 0 ]; then
        success "Sample data loaded ($ORG_COUNT organizations found)"
    else
        warning "No sample data found in organizations table"
    fi
    
    unset PGPASSWORD
}

# Main execution
main() {
    echo "   CostWatch Database Initialization"
    echo
    
    log "Starting database initialization process..."
    
    check_postgres
    create_database
    run_migrations
    verify_setup
    
    echo
    success "Database initialization completed successfully!"
    echo
    echo "Database Details:"
    echo "  Host: $DB_HOST"
    echo "  Port: $DB_PORT"
    echo "  Database: $DB_NAME"
    echo "  User: $DB_USER"
    echo
    echo "You can now start the CostWatch services."
    echo "Sample login credentials:"
    echo "  Admin: admin@demo-org.com / admin123"
    echo "  User:  user@demo-org.com / user123"
    echo
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "CostWatch Database Initialization Script"
        echo
        echo "Usage: $0 [OPTIONS]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --verify       Only verify the database setup"
        echo "  --clean        Drop and recreate the database (WARNING: Data loss!)"
        echo
        echo "Environment Variables:"
        echo "  DB_HOST        Database host (default: localhost)"
        echo "  DB_PORT        Database port (default: 5432)"
        echo "  DB_NAME        Database name (default: costwatch_db)"
        echo "  DB_USER        Database user (default: costwatch_user)"
        echo "  DB_PASSWORD    Database password (default: costwatch_pass123)"
        exit 0
        ;;
    --verify)
        log "Verifying database setup only..."
        check_postgres
        verify_setup
        success "Database verification completed"
        exit 0
        ;;
    --clean)
        warning "This will DROP the entire database and recreate it!"
        read -p "Are you sure? Type 'yes' to continue: " -r
        if [[ $REPLY == "yes" ]]; then
            log "Dropping database $DB_NAME..."
            psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
            psql -h "$DB_HOST" -p "$DB_PORT" -U postgres -c "DROP USER IF EXISTS $DB_USER;"
            success "Database dropped"
            main
        else
            log "Operation cancelled"
            exit 0
        fi
        ;;
    "")
        main
        ;;
    *)
        error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac