#!/usr/bin/env node
/**
 * Alicia Config Manager - Dependency Update Script
 * Ensures all projects use consistent dependency versions
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Standardized dependency versions
const STANDARD_VERSIONS = {
  // React ecosystem
  'react': '^18.3.1',
  'react-dom': '^18.3.1',
  '@types/react': '^18.3.12',
  '@types/react-dom': '^18.3.1',
  
  // TypeScript
  'typescript': '^5.6.3',
  '@types/node': '^20.0.0',
  
  // Build tools
  'vite': '^4.4.0',
  '@vitejs/plugin-react': '^4.0.0',
  
  // Styling
  'tailwindcss': '^3.3.0',
  'autoprefixer': '^10.4.0',
  'postcss': '^8.4.0',
  '@tailwindcss/forms': '^0.5.0',
  
  // Utilities
  'axios': '^1.6.0',
  'socket.io-client': '^4.7.0',
  'reactflow': '^11.10.1',
  
  // Backend
  'express': '^4.18.2',
  'socket.io': '^4.7.0',
  'mqtt': '^5.1.0',
  'cors': '^2.8.5',
  'helmet': '^7.1.0',
  'joi': '^17.11.0',
  'winston': '^3.10.0',
  'dotenv': '^17.2.2',
  'fs-extra': '^11.1.0',
  'chokidar': '^3.5.0',
  'express-rate-limit': '^7.1.5',
  
  // Development
  'nodemon': '^3.0.0',
  'concurrently': '^8.2.0',
  'eslint': '^8.57.0',
  '@typescript-eslint/eslint-plugin': '^6.21.0',
  '@typescript-eslint/parser': '^6.21.0',
  'eslint-plugin-react': '^7.34.0',
  'eslint-plugin-react-hooks': '^4.6.0'
};

const PROJECTS = [
  { name: 'frontend', path: './frontend' },
  { name: 'backend', path: './backend' }
];

function updatePackageJson(projectPath) {
  const packageJsonPath = path.join(projectPath, 'package.json');
  
  if (!fs.existsSync(packageJsonPath)) {
    console.log(`⚠️  Package.json not found in ${projectPath}`);
    return;
  }
  
  const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
  let updated = false;
  
  // Update dependencies
  if (packageJson.dependencies) {
    for (const [dep, version] of Object.entries(STANDARD_VERSIONS)) {
      if (packageJson.dependencies[dep] && packageJson.dependencies[dep] !== version) {
        console.log(`📦 Updating ${dep} in dependencies: ${packageJson.dependencies[dep]} → ${version}`);
        packageJson.dependencies[dep] = version;
        updated = true;
      }
    }
  }
  
  // Update devDependencies
  if (packageJson.devDependencies) {
    for (const [dep, version] of Object.entries(STANDARD_VERSIONS)) {
      if (packageJson.devDependencies[dep] && packageJson.devDependencies[dep] !== version) {
        console.log(`📦 Updating ${dep} in devDependencies: ${packageJson.devDependencies[dep]} → ${version}`);
        packageJson.devDependencies[dep] = version;
        updated = true;
      }
    }
  }
  
  if (updated) {
    fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2) + '\n');
    console.log(`✅ Updated ${projectPath}/package.json`);
  } else {
    console.log(`✅ ${projectPath}/package.json is already up to date`);
  }
}

function main() {
  console.log('🚀 Updating dependencies to standard versions...\n');
  
  // Update each project
  PROJECTS.forEach(project => {
    console.log(`\n📁 Processing ${project.name}...`);
    updatePackageJson(project.path);
  });
  
  console.log('\n🎉 Dependency update complete!');
  console.log('\nNext steps:');
  console.log('1. Run: npm run install:all');
  console.log('2. Run: npm run type-check');
  console.log('3. Run: npm run build');
}

if (require.main === module) {
  main();
}

module.exports = { updatePackageJson, STANDARD_VERSIONS };
