#!/bin/bash
set -e

echo "Installing pgvector extension..."

# Update package lists
apt-get update

# Install pgvector
apt-get install -y postgresql-15-pgvector

echo "pgvector installation completed successfully"
