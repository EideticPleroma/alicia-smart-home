// Security headers middleware for production hardening
const helmet = require('helmet');

// Security headers configuration
const securityHeaders = (req, res, next) => {
  // Set security headers manually (can be replaced with helmet if installed)

  // Prevent clickjacking
  res.setHeader('X-Frame-Options', 'DENY');

  // Prevent MIME type sniffing
  res.setHeader('X-Content-Type-Options', 'nosniff');

  // Enable XSS protection
  res.setHeader('X-XSS-Protection', '1; mode=block');

  // Referrer policy
  res.setHeader('Referrer-Policy', 'strict-origin-when-cross-origin');

  // Permissions policy (restrict features)
  res.setHeader('Permissions-Policy',
    'camera=(), microphone=(), geolocation=(), payment=(), usb=()'
  );

  // Content Security Policy (strict for production)
  if (process.env.NODE_ENV === 'production') {
    res.setHeader('Content-Security-Policy',
      "default-src 'self'; " +
      "script-src 'self' 'unsafe-inline' 'unsafe-eval'; " +
      "style-src 'self' 'unsafe-inline'; " +
      "img-src 'self' data: https:; " +
      "font-src 'self'; " +
      "connect-src 'self' ws: wss: http: https:; " +
      "frame-ancestors 'none'; " +
      "base-uri 'self'; " +
      "form-action 'self';"
    );
  } else {
    // Relaxed CSP for development
    res.setHeader('Content-Security-Policy',
      "default-src 'self'; " +
      "script-src 'self' 'unsafe-inline' 'unsafe-eval'; " +
      "style-src 'self' 'unsafe-inline'; " +
      "img-src 'self' data: https: http:; " +
      "font-src 'self'; " +
      "connect-src 'self' ws: wss: http: https:; " +
      "frame-ancestors 'none';"
    );
  }

  // HSTS (HTTP Strict Transport Security) - only in production with HTTPS
  if (process.env.NODE_ENV === 'production' && req.secure) {
    res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
  }

  // Remove server information
  res.removeHeader('X-Powered-By');

  next();
};

// Create comprehensive security middleware
const createSecurityMiddleware = () => {
  // Use manual security headers for now
  return securityHeaders;
};

module.exports = {
  securityHeaders,
  createSecurityMiddleware
};
