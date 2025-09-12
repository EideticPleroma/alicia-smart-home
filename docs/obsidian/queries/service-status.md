# 📋 Service Status Dashboard

> **Dynamic Content**: This page automatically updates with current service status information

## 🎯 **Service Health Overview**

### **All Services Status**
```dataview
TABLE 
  status as "Status",
  uptime as "Uptime",
  response_time as "Response Time",
  cpu_usage as "CPU %",
  memory_usage as "Memory %"
FROM "services"
WHERE status != null
SORT uptime DESC
```

### **Service Categories**
```dataview
TABLE 
  category as "Category",
  count(rows) as "Total Services",
  count(rows) FILTER WHERE status = "healthy" as "Healthy",
  count(rows) FILTER WHERE status = "warning" as "Warning",
  count(rows) FILTER WHERE status = "error" as "Error"
FROM "services"
GROUP BY category
SORT category ASC
```

### **Performance Metrics**
```dataview
TABLE 
  service_name as "Service",
  avg(response_time) as "Avg Response Time",
  max(response_time) as "Max Response Time",
  avg(cpu_usage) as "Avg CPU %",
  avg(memory_usage) as "Avg Memory %"
FROM "services"
WHERE timestamp > date(today) - dur(1 day)
GROUP BY service_name
SORT avg(response_time) ASC
```

## 🚨 **Alert Summary**

### **Services with Issues**
```dataview
LIST
FROM "services"
WHERE status = "error" OR status = "warning"
SORT status ASC, service_name ASC
```

### **High Resource Usage**
```dataview
LIST
FROM "services"
WHERE cpu_usage > 80 OR memory_usage > 80
SORT cpu_usage DESC, memory_usage DESC
```

### **Slow Response Times**
```dataview
LIST
FROM "services"
WHERE response_time > 1000
SORT response_time DESC
```

## 📊 **Service Dependencies**

### **Service Dependencies Map**
```dataview
TABLE 
  service_name as "Service",
  dependencies as "Dependencies",
  health_status as "Health Status"
FROM "service-dependencies"
WHERE dependencies != null
SORT service_name ASC
```

### **Critical Dependencies**
```dataview
LIST
FROM "service-dependencies"
WHERE health_status = "critical"
SORT service_name ASC
```

## 🎯 **Quick Actions**

### **Restart Services**
- **[[Restart All Services]]** - Restart all services
- **[[Restart Voice Services]]** - Restart voice processing services
- **[[Restart Device Services]]** - Restart device integration services
- **[[Restart Core Services]]** - Restart core infrastructure services

### **Health Checks**
- **[[Run Health Checks]]** - Run comprehensive health checks
- **[[Check Service Dependencies]]** - Verify service dependencies
- **[[Validate Configuration]]** - Validate service configurations
- **[[Test Service Communication]]** - Test inter-service communication

### **Monitoring**
- **[[View Service Logs]]** - View service logs
- **[[Monitor Performance]]** - Monitor system performance
- **[[Check Resource Usage]]** - Check resource utilization
- **[[View Alerts]]** - View current alerts

## 📈 **Historical Data**

### **Service Uptime History**
```dataview
TABLE 
  service_name as "Service",
  date(timestamp) as "Date",
  avg(uptime) as "Avg Uptime %"
FROM "services"
WHERE timestamp > date(today) - dur(7 days)
GROUP BY service_name, date(timestamp)
SORT service_name ASC, date(timestamp) DESC
```

### **Performance Trends**
```dataview
TABLE 
  service_name as "Service",
  date(timestamp) as "Date",
  avg(response_time) as "Avg Response Time",
  avg(cpu_usage) as "Avg CPU %"
FROM "services"
WHERE timestamp > date(today) - dur(7 days)
GROUP BY service_name, date(timestamp)
SORT service_name ASC, date(timestamp) DESC
```

## 🎯 **Service-Specific Information**

### **Voice Services**
- **[[STT Service Status]]** - Speech-to-text service status
- **[[AI Service Status]]** - AI processing service status
- **[[TTS Service Status]]** - Text-to-speech service status
- **[[Voice Router Status]]** - Voice pipeline orchestration status

### **Device Services**
- **[[Device Manager Status]]** - Device management service status
- **[[HA Bridge Status]]** - Home Assistant bridge status
- **[[Sonos Service Status]]** - Sonos integration service status
- **[[Device Control Status]]** - Device control service status

### **Core Services**
- **[[MQTT Broker Status]]** - Message bus broker status
- **[[Security Gateway Status]]** - Security gateway status
- **[[Health Monitor Status]]** - Health monitoring service status
- **[[Config Service Status]]** - Configuration service status

## 🔧 **Troubleshooting**

### **Common Issues**
- **[[Service Won't Start]]** - Troubleshoot service startup issues
- **[[High Resource Usage]]** - Resolve high CPU/memory usage
- **[[Slow Response Times]]** - Fix slow service response times
- **[[Service Communication Issues]]** - Resolve inter-service communication problems

### **Diagnostic Tools**
- **[[Service Logs]]** - View and analyze service logs
- **[[Network Diagnostics]]** - Check network connectivity
- **[[Resource Monitoring]]** - Monitor system resources
- **[[Performance Profiling]]** - Profile service performance

---

**Last Updated**: `=date(now)`

*This dashboard automatically updates with current service status information. Use it to monitor system health and quickly identify issues.*
