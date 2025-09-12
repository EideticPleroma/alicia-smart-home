# Frontend Rules for Alicia Config Manager

## Component Architecture Rules

### 1. Component Structure
- **Use functional components only** - No class components
- **Custom hooks for complex logic** - Extract reusable stateful logic
- **Single responsibility principle** - Each component has one clear purpose
- **Props interface definitions** - Use TypeScript interfaces for all props
- **Default props** - Provide sensible defaults for optional props

### 2. State Management Rules
- **Local state with useState** - For component-specific state
- **Context API for global state** - Config, devices, socket connection
- **Custom hooks for shared logic** - useSocket, useConfig, useDevices
- **Immutable updates** - Always create new objects/arrays
- **State normalization** - Keep data structures flat and normalized

### 3. Effect Management Rules
- **useEffect for side effects** - API calls, subscriptions, cleanup
- **Dependency arrays** - Always include all dependencies
- **Cleanup functions** - Remove event listeners, cancel requests
- **Effect separation** - One effect per concern
- **Conditional effects** - Use conditions to prevent unnecessary effects

### 4. Performance Optimization Rules
- **React.memo for expensive components** - Prevent unnecessary re-renders
- **useCallback for event handlers** - Stable function references
- **useMemo for computed values** - Expensive calculations
- **Lazy loading** - Code splitting for large components
- **Virtual scrolling** - For large lists of services/devices

## Styling and UI Rules

### 1. Design System
- **Tailwind CSS only** - No custom CSS files
- **Consistent spacing** - Use Tailwind spacing scale
- **Color palette** - Dark theme with accent colors
- **Typography scale** - Consistent font sizes and weights
- **Component variants** - Use Tailwind variants for different states

### 2. Responsive Design
- **Mobile-first approach** - Start with mobile, enhance for desktop
- **Breakpoint consistency** - Use Tailwind breakpoints (sm, md, lg, xl)
- **Touch-friendly** - Minimum 44px touch targets
- **Flexible layouts** - Use flexbox and grid appropriately
- **Content prioritization** - Most important content visible on mobile

### 3. Accessibility Rules
- **Semantic HTML** - Use proper HTML elements
- **ARIA labels** - For screen readers
- **Keyboard navigation** - All interactive elements accessible via keyboard
- **Focus management** - Clear focus indicators
- **Color contrast** - WCAG AA compliance

### 4. Animation and Transitions
- **Smooth transitions** - Use CSS transitions for state changes
- **Loading states** - Show loading indicators for async operations
- **Error states** - Clear error messages and recovery options
- **Success feedback** - Toast notifications for successful actions
- **Micro-interactions** - Subtle animations for better UX

## Data Flow Rules

### 1. Data Fetching
- **Custom hooks for API calls** - useConfig, useDevices, useSocket
- **Error handling** - Try-catch blocks and error boundaries
- **Loading states** - Show loading indicators during API calls
- **Retry logic** - Automatic retry for failed requests
- **Caching** - Cache API responses when appropriate

### 2. Real-time Updates
- **Socket.io integration** - Real-time updates via WebSocket
- **MQTT message handling** - Process MQTT messages from bus
- **Optimistic updates** - Update UI before server confirmation
- **Conflict resolution** - Handle concurrent updates gracefully
- **Debounced updates** - Prevent excessive re-renders

### 3. Form Handling
- **Controlled components** - All form inputs controlled by React state
- **Validation** - Client-side validation with real-time feedback
- **Error display** - Show validation errors clearly
- **Form submission** - Prevent double submission
- **Reset functionality** - Clear form after successful submission

## Error Handling Rules

### 1. Error Boundaries
- **Wrap major sections** - App, main components
- **Fallback UI** - Show error message instead of crashing
- **Error reporting** - Log errors for debugging
- **Recovery options** - Allow users to retry or refresh

### 2. API Error Handling
- **HTTP status codes** - Handle different error types appropriately
- **Network errors** - Show connection issues clearly
- **Timeout handling** - Handle slow or failed requests
- **User feedback** - Clear error messages for users
- **Retry mechanisms** - Allow users to retry failed operations

### 3. Validation Errors
- **Field-level validation** - Show errors next to specific fields
- **Form-level validation** - Prevent submission with invalid data
- **Real-time validation** - Validate as user types
- **Clear error messages** - Specific, actionable error messages
- **Error persistence** - Keep errors visible until fixed

## Testing Rules

### 1. Component Testing
- **React Testing Library** - Test user interactions, not implementation
- **Test user flows** - Focus on what users can do
- **Mock external dependencies** - Mock API calls, socket connections
- **Test error states** - Ensure error handling works correctly
- **Accessibility testing** - Test keyboard navigation, screen readers

### 2. Hook Testing
- **Custom hook testing** - Test hooks in isolation
- **Mock dependencies** - Mock external APIs and services
- **Test all code paths** - Success, error, and loading states
- **Test cleanup** - Ensure proper cleanup of effects
- **Test edge cases** - Empty data, network failures, etc.

### 3. Integration Testing
- **End-to-end flows** - Test complete user workflows
- **Real API calls** - Test with actual backend (in test environment)
- **Socket.io testing** - Test real-time functionality
- **Cross-browser testing** - Ensure compatibility across browsers
- **Performance testing** - Test with large datasets

## Code Quality Rules

### 1. Code Organization
- **Feature-based structure** - Group related components together
- **Barrel exports** - Use index.js files for clean imports
- **Consistent naming** - Use descriptive, consistent names
- **File naming** - Use PascalCase for components, camelCase for utilities
- **Import organization** - Group imports by type (React, third-party, local)

### 2. TypeScript Rules
- **Strict mode** - Use strict TypeScript configuration
- **Interface definitions** - Define interfaces for all data structures
- **Type safety** - Avoid any types, use proper typing
- **Generic types** - Use generics for reusable components
- **Type guards** - Use type guards for runtime type checking

### 3. Documentation
- **JSDoc comments** - Document all public functions and components
- **README files** - Document setup and usage instructions
- **Code comments** - Explain complex logic and business rules
- **API documentation** - Document all API endpoints and data structures
- **Changelog** - Keep track of changes and new features

## Security Rules

### 1. Input Sanitization
- **Validate all inputs** - Client-side and server-side validation
- **Sanitize user data** - Prevent XSS attacks
- **Escape special characters** - Handle user input safely
- **Limit input length** - Prevent buffer overflow attacks
- **Type checking** - Ensure data types are correct

### 2. API Security
- **HTTPS only** - Use secure connections
- **API key masking** - Don't expose sensitive data in UI
- **Rate limiting** - Prevent abuse of API endpoints
- **CORS configuration** - Restrict cross-origin requests
- **Authentication** - Implement proper authentication (future)

### 3. Data Protection
- **Sensitive data handling** - Mask API keys and passwords
- **Local storage** - Don't store sensitive data in localStorage
- **Session management** - Proper session handling
- **Data encryption** - Encrypt sensitive data (future)
- **Audit logging** - Log security-relevant events

## Performance Rules

### 1. Rendering Performance
- **Minimize re-renders** - Use React.memo, useCallback, useMemo
- **Virtual scrolling** - For large lists
- **Lazy loading** - Load components and data on demand
- **Code splitting** - Split code into smaller chunks
- **Bundle optimization** - Minimize bundle size

### 2. Network Performance
- **Request batching** - Combine multiple API calls
- **Caching** - Cache API responses
- **Compression** - Use gzip compression
- **CDN usage** - Serve static assets from CDN
- **Image optimization** - Optimize images and use appropriate formats

### 3. Memory Management
- **Cleanup effects** - Remove event listeners and subscriptions
- **Memory leaks** - Avoid memory leaks in long-running apps
- **Garbage collection** - Help garbage collector by nulling references
- **Large datasets** - Handle large datasets efficiently
- **Memory monitoring** - Monitor memory usage in development

## Deployment Rules

### 1. Build Optimization
- **Production builds** - Use optimized production builds
- **Tree shaking** - Remove unused code
- **Minification** - Minify JavaScript and CSS
- **Asset optimization** - Optimize images and fonts
- **Source maps** - Generate source maps for debugging

### 2. Environment Configuration
- **Environment variables** - Use env vars for configuration
- **Build-time configuration** - Configure app at build time
- **Runtime configuration** - Allow some configuration at runtime
- **Feature flags** - Use feature flags for gradual rollouts
- **Error tracking** - Implement error tracking in production

### 3. Monitoring and Analytics
- **Performance monitoring** - Track app performance
- **Error tracking** - Monitor and report errors
- **User analytics** - Track user behavior (privacy-compliant)
- **Health checks** - Monitor app health
- **Logging** - Implement proper logging

These rules ensure the frontend is maintainable, performant, secure, and provides an excellent user experience while integrating seamlessly with the existing Alicia monitoring system.

