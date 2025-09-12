# Dependency Management Guide

This document outlines the standardized dependency management approach for the Alicia Config Manager project.

## 📦 Standardized Versions

All projects use consistent dependency versions to ensure compatibility and reduce conflicts:

### React Ecosystem
- **React**: `^18.3.1`
- **React DOM**: `^18.3.1`
- **@types/react**: `^18.3.12`
- **@types/react-dom**: `^18.3.1`

### TypeScript
- **TypeScript**: `^5.6.3`
- **@types/node**: `^20.0.0`

### Build Tools
- **Vite**: `^4.4.0`
- **@vitejs/plugin-react**: `^4.0.0`

### Styling
- **Tailwind CSS**: `^3.3.0`
- **Autoprefixer**: `^10.4.0`
- **PostCSS**: `^8.4.0`
- **@tailwindcss/forms**: `^0.5.0`

### Backend Dependencies
- **Express**: `^4.18.2`
- **Socket.io**: `^4.7.0`
- **MQTT**: `^5.1.0`
- **CORS**: `^2.8.5`
- **Helmet**: `^7.1.0`
- **Joi**: `^17.11.0`
- **Winston**: `^3.10.0`

## 🛠️ Available Scripts

### Installation
```bash
# Install all dependencies
npm run install:all

# Install specific project
npm run install:frontend
npm run install:backend
```

### Development
```bash
# Start all services in development mode
npm run dev

# Start specific service
npm run dev:frontend
npm run dev:backend
```

### Building
```bash
# Build all projects
npm run build

# Build specific project
npm run build:frontend
npm run build:backend
```

### Validation
```bash
# Validate all dependencies
npm run validate-dependencies

# Update dependencies to standard versions
npm run update-dependencies

# Check for security vulnerabilities
npm run audit
```

### Type Checking
```bash
# Type check all TypeScript projects
npm run type-check

# Type check specific project
npm run type-check:frontend
```

### Linting
```bash
# Lint all projects
npm run lint

# Lint specific project
npm run lint:frontend
```

### Cleanup
```bash
# Clean all node_modules
npm run clean

# Clean specific project
npm run clean:frontend
npm run clean:backend
```

## 🔧 Dependency Management Scripts

### `scripts/update-dependencies.js`
Automatically updates all projects to use standardized dependency versions.

**Usage:**
```bash
npm run update-dependencies
```

**What it does:**
- Reads standardized versions from the script
- Updates package.json files in all projects
- Ensures consistency across the entire codebase

### `scripts/validate-dependencies.js`
Validates that all projects have consistent and up-to-date dependencies.

**Usage:**
```bash
npm run validate-dependencies
```

**What it checks:**
- Missing node_modules directories
- Outdated packages
- Security vulnerabilities
- Package consistency

## 📋 Best Practices

### 1. Adding New Dependencies
When adding new dependencies:

1. **Check if it's already standardized** in `scripts/update-dependencies.js`
2. **Add to the appropriate project** (frontend/backend)
3. **Update the standardization script** if it's a common dependency
4. **Run validation** to ensure no conflicts

### 2. Updating Dependencies
When updating dependencies:

1. **Update the standardization script** first
2. **Run the update script** to apply changes
3. **Test thoroughly** to ensure compatibility
4. **Update documentation** if needed

### 3. Security Updates
Regularly check for security vulnerabilities:

```bash
# Check all projects
npm run audit

# Fix automatically (be careful!)
npm audit fix

# Fix specific project
cd frontend && npm audit fix
```

### 4. Version Conflicts
If you encounter version conflicts:

1. **Check the standardization script** for the correct version
2. **Update the conflicting project** to match
3. **Run validation** to ensure consistency
4. **Test the integration** thoroughly

## 🚨 Troubleshooting

### Common Issues

#### "Module not found" errors
```bash
# Clean and reinstall
npm run clean
npm run install:all
```

#### TypeScript compilation errors
```bash
# Check types
npm run type-check

# Update dependencies
npm run update-dependencies
```

#### Security vulnerabilities
```bash
# Check for vulnerabilities
npm run audit

# Fix automatically (review changes first!)
npm audit fix
```

#### Outdated packages
```bash
# Update to standard versions
npm run update-dependencies

# Or update specific project
cd frontend && npm update
```

## 📊 Project Structure

```
alicia-config-manager/
├── frontend/                 # React + Vite frontend
│   ├── package.json         # Frontend dependencies
│   ├── tsconfig.json        # TypeScript configuration
│   └── .eslintrc.json       # ESLint configuration
├── backend/                 # Node.js + Express backend
│   ├── package.json         # Backend dependencies
│   └── src/                 # Backend source code
├── scripts/                 # Dependency management scripts
│   ├── update-dependencies.js
│   └── validate-dependencies.js
├── package.json             # Root workspace configuration
└── DEPENDENCY_MANAGEMENT.md # This file
```

## 🔄 Workflow

### Daily Development
1. `npm run dev` - Start development servers
2. Make changes
3. `npm run type-check` - Check types
4. `npm run lint` - Check code quality

### Before Committing
1. `npm run validate-dependencies` - Check dependencies
2. `npm run type-check` - Check types
3. `npm run lint` - Check code quality
4. `npm run build` - Ensure build works

### Weekly Maintenance
1. `npm run audit` - Check security
2. `npm run update-dependencies` - Update to latest standards
3. `npm run validate-dependencies` - Verify consistency

## 📚 Additional Resources

- [npm Documentation](https://docs.npmjs.com/)
- [TypeScript Configuration](https://www.typescriptlang.org/docs/handbook/tsconfig-json.html)
- [ESLint Configuration](https://eslint.org/docs/user-guide/configuring/)
- [Vite Configuration](https://vitejs.dev/config/)
