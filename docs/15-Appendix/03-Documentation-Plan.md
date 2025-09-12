# Documentation Consolidation Plan

## 🎯 **Objective**
Consolidate all documentation into a clean, organized structure that reflects the new 23-service bus architecture implementation.

## 📊 **Current State Analysis**

### **Documentation Files to Consolidate:**
- `ALICIA_BUS_ARCHITECTURE_COMPLETE_REPORT.md` - **KEEP** (Master reference)
- `BUS_ARCHITECTURE_IMPLEMENTATION_GUIDE.md` - **MERGE** into docs
- `BUS_ARCHITECTURE_MIGRATION_OUTLINE.md` - **MERGE** into docs
- `BUS_ARCHITECTURE_PHASE_GUIDES.md` - **MERGE** into docs
- `CLINE_BUS_ARCHITECTURE_PROMPT.md` - **MOVE** to docs/tools
- `CLINE_GROK_PROMPT.md` - **MOVE** to docs/tools
- `IMPLEMENTATION_PLAN.md` - **MOVE** to docs/implementation
- `MIGRATION_GUIDE.md` - **MOVE** to docs/implementation
- `docs/00-Table-of-Contents-Bus-Architecture.md` - **KEEP** (New structure)
- `docs/00-Table-of-Contents.md` - **REPLACE** (Legacy)

### **Legacy Folders to Clean:**
- `alicia-monitoring-app/` - **REMOVE** (Legacy monolithic app)
- `home-assistant/` - **REMOVE** (Legacy HA setup)
- `mqtt/` - **REMOVE** (Legacy MQTT setup)
- `mqtt-testing/` - **REMOVE** (Legacy testing)
- `postgres/` - **REMOVE** (Legacy database)
- `voice-processing/` - **REMOVE** (Legacy voice processing)
- `test-pack/` - **KEEP** (Update for bus architecture)
- `tmp/` - **REMOVE** (Temporary files)

### **Core Folders to Keep:**
- `bus-services/` - **KEEP** (23 microservices)
- `bus-config/` - **KEEP** (MQTT configuration)
- `bus-data/` - **KEEP** (Data storage)
- `bus-logs/` - **KEEP** (Log storage)
- `archive/` - **KEEP** (Cleaned up)
- `docs/` - **RESTRUCTURE** (New organization)

## 🏗️ **New Documentation Structure**

```
docs/
├── 00-Table-of-Contents.md          # Master TOC
├── 01-Introduction.md               # Project overview
├── 02-Architecture-Overview.md      # Bus architecture overview
├── 03-Quick-Start.md                # Quick start guide
├── 04-Installation.md               # Installation guide
├── 05-Configuration.md              # Configuration guide
├── 06-API-Reference.md              # API documentation
├── 07-Services/                     # Service-specific docs
│   ├── 01-Core-Infrastructure.md
│   ├── 02-Voice-Processing.md
│   ├── 03-Device-Integration.md
│   ├── 04-Advanced-Features.md
│   └── 05-Supporting-Services.md
├── 08-Deployment.md                 # Deployment guide
├── 09-Monitoring.md                 # Monitoring and health
├── 10-Security.md                   # Security guide
├── 11-Troubleshooting.md            # Troubleshooting
├── 12-Development.md                # Development guide
├── 13-Implementation/               # Implementation docs
│   ├── 01-Implementation-Plan.md
│   ├── 02-Migration-Guide.md
│   └── 03-Architecture-Report.md
├── 14-Tools/                        # Development tools
│   ├── 01-Cline-Prompts.md
│   └── 02-Development-Tools.md
└── 15-Appendix/                     # Additional resources
    ├── 01-Glossary.md
    └── 02-References.md
```

## 🧹 **Cleanup Actions**

### **Phase 1: Remove Legacy Folders**
1. Remove `alicia-monitoring-app/`
2. Remove `home-assistant/`
3. Remove `mqtt/`
4. Remove `mqtt-testing/`
5. Remove `postgres/`
6. Remove `voice-processing/`
7. Remove `tmp/`

### **Phase 2: Consolidate Documentation**
1. Create new `docs/` structure
2. Move and merge documentation files
3. Update all internal links
4. Create comprehensive TOC

### **Phase 3: Update Project Structure**
1. Keep only essential folders
2. Update README.md
3. Clean up loose files
4. Organize remaining files

## 📋 **Implementation Steps**

1. **Backup current state**
2. **Remove legacy folders**
3. **Create new docs structure**
4. **Consolidate documentation**
5. **Update all references**
6. **Test documentation links**
7. **Update README.md**

## ✅ **Success Criteria**

- [ ] Clean project structure with only essential folders
- [ ] Comprehensive documentation in organized structure
- [ ] All internal links working
- [ ] Updated README.md reflecting bus architecture
- [ ] No loose files in project root
- [ ] Documentation reflects current 23-service implementation
