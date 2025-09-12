#!/usr/bin/env node
/**
 * Alicia Config Manager - Dependency Validation Script
 * Validates that all projects have consistent and up-to-date dependencies
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const PROJECTS = [
  { name: 'frontend', path: './frontend' },
  { name: 'backend', path: './backend' }
];

function checkDependencies() {
  console.log('🔍 Validating dependencies across all projects...\n');
  
  let allValid = true;
  const issues = [];
  
  PROJECTS.forEach(project => {
    console.log(`📁 Checking ${project.name}...`);
    
    const packageJsonPath = path.join(project.path, 'package.json');
    
    if (!fs.existsSync(packageJsonPath)) {
      console.log(`❌ Package.json not found in ${project.path}`);
      allValid = false;
      return;
    }
    
    const packageJson = JSON.parse(fs.readFileSync(packageJsonPath, 'utf8'));
    
    // Check for missing node_modules
    const nodeModulesPath = path.join(project.path, 'node_modules');
    if (!fs.existsSync(nodeModulesPath)) {
      console.log(`⚠️  node_modules not found in ${project.path}`);
      issues.push(`${project.name}: Missing node_modules`);
    }
    
    // Check for outdated packages
    try {
      console.log(`   Checking for outdated packages...`);
      const outdated = execSync(`cd ${project.path} && npm outdated --json`, { encoding: 'utf8' });
      const outdatedPackages = JSON.parse(outdated);
      
      if (Object.keys(outdatedPackages).length > 0) {
        console.log(`   ⚠️  Found ${Object.keys(outdatedPackages).length} outdated packages`);
        issues.push(`${project.name}: ${Object.keys(outdatedPackages).length} outdated packages`);
      } else {
        console.log(`   ✅ All packages up to date`);
      }
    } catch (error) {
      // npm outdated returns non-zero exit code when packages are outdated
      if (error.status === 1) {
        console.log(`   ⚠️  Some packages are outdated`);
      } else {
        console.log(`   ❌ Error checking outdated packages: ${error.message}`);
        allValid = false;
      }
    }
    
    // Check for security vulnerabilities
    try {
      console.log(`   Checking for security vulnerabilities...`);
      const audit = execSync(`cd ${project.path} && npm audit --json`, { encoding: 'utf8' });
      const auditResult = JSON.parse(audit);
      
      if (auditResult.vulnerabilities && Object.keys(auditResult.vulnerabilities).length > 0) {
        const vulnCount = Object.keys(auditResult.vulnerabilities).length;
        console.log(`   ⚠️  Found ${vulnCount} security vulnerabilities`);
        issues.push(`${project.name}: ${vulnCount} security vulnerabilities`);
      } else {
        console.log(`   ✅ No security vulnerabilities found`);
      }
    } catch (error) {
      console.log(`   ❌ Error checking security vulnerabilities: ${error.message}`);
      allValid = false;
    }
    
    console.log(`   ✅ ${project.name} validation complete\n`);
  });
  
  // Summary
  console.log('📊 Validation Summary:');
  console.log('====================');
  
  if (issues.length === 0) {
    console.log('✅ All projects are valid and up to date!');
  } else {
    console.log('⚠️  Issues found:');
    issues.forEach(issue => console.log(`   - ${issue}`));
    allValid = false;
  }
  
  console.log('\n🔧 Recommended actions:');
  if (issues.some(issue => issue.includes('Missing node_modules'))) {
    console.log('   - Run: npm run install:all');
  }
  if (issues.some(issue => issue.includes('outdated packages'))) {
    console.log('   - Run: npm run update-dependencies');
  }
  if (issues.some(issue => issue.includes('security vulnerabilities'))) {
    console.log('   - Run: npm audit fix');
  }
  
  return allValid;
}

function main() {
  const isValid = checkDependencies();
  process.exit(isValid ? 0 : 1);
}

if (require.main === module) {
  main();
}

module.exports = { checkDependencies };
