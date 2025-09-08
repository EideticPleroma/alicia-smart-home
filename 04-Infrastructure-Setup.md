---
tags: #docker-setup #postgresql #database-setup #pgvector #containerization #infrastructure #setup-guide #alicia-project #database-configuration #docker-compose
---

# Alicia PostgreSQL Docker Setup Guide

This guide provides a complete Docker container configuration for PostgreSQL with pgvector support for the Alicia memory system.

## 🚀 Quick Start

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Start the PostgreSQL container:**
   ```bash
   docker-compose up -d
   ```

3. **Wait for initialization (first run may take a few minutes):**
   ```bash
   docker-compose logs -f postgres
   ```

4. **Verify the setup:**
   ```bash
   docker-compose exec postgres psql -U alicia_user -d alicia_db -c "\dt"
   ```

## 📁 Project Structure

```
.
├── docker-compose.yml          # Main Docker configuration
├── .env.example               # Environment variables template
├── init-scripts/              # Database initialization scripts
│   ├── 01-install-pgvector.sh # pgvector installation
│   ├── 02-setup-extensions.sql # Enable PostgreSQL extensions
│   └── 03-create-schema.sql   # Create database schema
└── Postgres/                  # Persistent data directory
    └── pg-data/              # PostgreSQL data files
```

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env` and adjust the values:

```bash
# Required
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=alicia_db
POSTGRES_USER=alicia_user

# Optional
VECTOR_DIMENSION=768  # Adjust based on your embedding model
```

### Database Schema

The setup creates two main tables:

- **memories**: Stores chat messages with vector embeddings
- **conversations**: Groups related messages by conversation

## 🛠️ Available Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f postgres
```

### Access PostgreSQL Shell
```bash
docker-compose exec postgres psql -U alicia_user -d alicia_db
```

### Check Database Status
```bash
docker-compose exec postgres pg_isready -U alicia_user -d alicia_db
```

### Backup Database
```bash
docker-compose exec postgres pg_dump -U alicia_user -d alicia_db > backup.sql
```

### Restore Database
```bash
docker-compose exec -T postgres psql -U alicia_user -d alicia_db < backup.sql
```

## 🔍 Troubleshooting

### Common Issues

1. **Port 5432 already in use:**
   ```bash
   # Find process using port 5432
   netstat -ano | findstr :5432
   # Kill the process or change port in docker-compose.yml
   ```

2. **Permission issues with data directory:**
   ```bash
   # Fix permissions on Windows
   icacls Postgres/pg-data /grant "Everyone:(OI)(CI)F" /T
   ```

3. **pgvector installation fails:**
   ```bash
   # Check container logs
   docker-compose logs pgvector-setup
   # Manual installation
   docker-compose exec postgres bash -c "apt-get update && apt-get install -y postgresql-15-pgvector"
   ```

### Health Checks

The setup includes health checks. Monitor container health:

```bash
docker-compose ps
```

## 📊 Database Operations

### Insert Sample Data
```sql
INSERT INTO memories (content, message_type)
VALUES ('Hello, this is a test message', 'user');
```

### Query with Vector Search
```sql
-- Example vector similarity search
SELECT content, 1 - (embedding <=> '[0.1, 0.2, ...]') as similarity
FROM memories
ORDER BY embedding <=> '[0.1, 0.2, ...]'
LIMIT 5;
```

### View Table Structure
```sql
\d memories
\d conversations
```

## 🔒 Security Considerations

1. **Change default password** in `.env` file
2. **Use strong passwords** for database users
3. **Limit network exposure** - consider using internal networks
4. **Regular backups** of the `Postgres/pg-data` directory
5. **Monitor access logs** for suspicious activity

## 📈 Performance Tuning

### Connection Pooling
Consider adding PgBouncer for connection pooling in production:

```yaml
# Add to docker-compose.yml
services:
  pgbouncer:
    image: brainsam/pgbouncer:latest
    depends_on:
      - postgres
    ports:
      - "6432:6432"
```

### Memory Configuration
Adjust PostgreSQL memory settings in custom configuration:

```sql
-- In PostgreSQL shell
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET work_mem = '4MB';
SELECT pg_reload_conf();
```

## 🔄 Updates and Maintenance

### Update PostgreSQL Version
```bash
# Stop containers
docker-compose down

# Update version in docker-compose.yml
# image: postgres:16

# Remove old data (WARNING: This will delete all data!)
docker volume rm $(docker volume ls -q)

# Start with new version
docker-compose up -d
```

### Clean Up
```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: Deletes all data!)
docker-compose down -v

# Remove images
docker-compose down --rmi all
```

## 📚 Additional Resources

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [pgvector GitHub](https://github.com/pgvector/pgvector)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Vector Search Guide](https://github.com/pgvector/pgvector#vector-search)

## 🤝 Support

If you encounter issues:

1. Check the logs: `docker-compose logs`
2. Verify environment variables in `.env`
3. Ensure Docker Desktop is running
4. Check available disk space
5. Review firewall settings for port 5432
