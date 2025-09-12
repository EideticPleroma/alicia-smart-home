# Chapter 17: Metrics Collector

## 🎯 **Metrics Collection Architecture Overview**

The Metrics Collector service provides **comprehensive system monitoring** by collecting, aggregating, and analyzing metrics from all Alicia bus services. It implements real-time alerting, performance analysis, and system-wide health monitoring to ensure optimal system performance and reliability. This chapter analyzes the Metrics Collector implementation, examining its data collection strategies, alerting system, and performance insights.

## 📊 **Metrics Collection Architecture**

### **Multi-Type Metrics Support**

The Metrics Collector implements **comprehensive metrics support**:

```python
class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"
```

**Why Multiple Metric Types?**

1. **Different Data Types**: Different metrics require different storage and analysis
2. **Performance Optimization**: Optimize storage and querying for each type
3. **Statistical Analysis**: Enable different statistical operations
4. **Alerting Flexibility**: Support different alerting patterns
5. **Visualization**: Enable appropriate visualization for each type

### **Metrics Data Structure**

The Metrics Collector uses **sophisticated data structures**:

```python
@dataclass
class MetricData:
    """Individual metric data point."""
    name: str
    value: Union[int, float]
    timestamp: float
    labels: Dict[str, str] = field(default_factory=dict)
    metric_type: MetricType = MetricType.GAUGE

@dataclass
class ServiceMetrics:
    """Metrics for a specific service."""
    service_name: str
    instance_id: str
    metrics: List[MetricData] = field(default_factory=list)
    last_updated: float = 0.0
    health_status: str = "unknown"
```

**Data Structure Features:**
- **Flexible Values**: Support integer and float values
- **Labeling System**: Support metric labels for filtering
- **Type Classification**: Classify metrics by type
- **Service Grouping**: Group metrics by service and instance
- **Timestamp Tracking**: Track metric timestamps

### **Metrics Collector Configuration**

The Metrics Collector uses **extensive configuration options**:

```python
def __init__(self):
    # Metrics storage
    self.service_metrics: Dict[str, Dict[str, ServiceMetrics]] = {}
    self.metrics_history: Dict[str, List[MetricData]] = {}
    self.alert_rules: Dict[str, AlertRule] = {}
    self.active_alerts: Dict[str, Alert] = {}
    
    # Configuration
    self.collection_interval = 30  # seconds
    self.retention_period = 3600  # 1 hour
    self.max_history_per_metric = 1000
    self.system_metrics_interval = 60  # seconds
    
    # Alert thresholds
    self.default_alert_rules = self._create_default_alert_rules()
```

**Configuration Features:**
- **Collection Intervals**: Configurable collection frequencies
- **Retention Periods**: Data retention management
- **History Limits**: Limit historical data storage
- **Alert Rules**: Configurable alerting rules

## 📈 **Metrics Collection Strategies**

### **Real-time Metrics Collection**

The Metrics Collector implements **real-time metrics collection**:

```python
def _metrics_collection_loop(self):
    """Background loop for collecting metrics from services."""
    while True:
        try:
            # Collect metrics from all services
            for service_name in self.service_metrics:
                for instance_id in self.service_metrics[service_name]:
                    self._collect_service_metrics(service_name, instance_id)
            
            # Process collected metrics
            self._process_collected_metrics()
            
            # Check alert conditions
            self._check_alert_conditions()
            
            time.sleep(self.collection_interval)
            
        except Exception as e:
            self.logger.error(f"Metrics collection failed: {e}")
            time.sleep(self.collection_interval)
```

**Collection Features:**
- **Periodic Collection**: Regular metrics collection intervals
- **Service Iteration**: Collect from all registered services
- **Instance Processing**: Process metrics per instance
- **Alert Checking**: Check alert conditions during collection

### **Service Metrics Collection**

The Metrics Collector implements **service-specific metrics collection**:

```python
def _collect_service_metrics(self, service_name: str, instance_id: str):
    """Collect metrics from a specific service instance."""
    try:
        # Get service instance information
        service_data = self.service_metrics[service_name][instance_id]
        
        # Collect basic metrics
        basic_metrics = self._collect_basic_metrics(service_name, instance_id)
        
        # Collect performance metrics
        performance_metrics = self._collect_performance_metrics(service_name, instance_id)
        
        # Collect health metrics
        health_metrics = self._collect_health_metrics(service_name, instance_id)
        
        # Combine all metrics
        all_metrics = basic_metrics + performance_metrics + health_metrics
        
        # Update service metrics
        service_data.metrics = all_metrics
        service_data.last_updated = time.time()
        
        # Store in history
        self._store_metrics_history(service_name, instance_id, all_metrics)
        
    except Exception as e:
        self.logger.error(f"Service metrics collection failed: {e}")
```

**Service Collection Features:**
- **Multi-metric Collection**: Collect different types of metrics
- **Real-time Updates**: Update metrics in real-time
- **History Storage**: Store metrics in history
- **Error Handling**: Handle collection errors gracefully

### **System Metrics Collection**

The Metrics Collector implements **system-wide metrics collection**:

```python
def _system_metrics_loop(self):
    """Background loop for collecting system metrics."""
    while True:
        try:
            # Collect CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_metrics = [
                MetricData("system_cpu_percent", cpu_percent, time.time(), {"type": "system"}),
                MetricData("system_cpu_count", psutil.cpu_count(), time.time(), {"type": "system"})
            ]
            
            # Collect memory metrics
            memory = psutil.virtual_memory()
            memory_metrics = [
                MetricData("system_memory_percent", memory.percent, time.time(), {"type": "system"}),
                MetricData("system_memory_total", memory.total, time.time(), {"type": "system"}),
                MetricData("system_memory_available", memory.available, time.time(), {"type": "system"})
            ]
            
            # Collect disk metrics
            disk = psutil.disk_usage('/')
            disk_metrics = [
                MetricData("system_disk_percent", disk.percent, time.time(), {"type": "system"}),
                MetricData("system_disk_total", disk.total, time.time(), {"type": "system"}),
                MetricData("system_disk_free", disk.free, time.time(), {"type": "system"})
            ]
            
            # Store system metrics
            system_metrics = cpu_metrics + memory_metrics + disk_metrics
            self._store_system_metrics(system_metrics)
            
            time.sleep(self.system_metrics_interval)
            
        except Exception as e:
            self.logger.error(f"System metrics collection failed: {e}")
```

**System Collection Features:**
- **CPU Monitoring**: Monitor CPU usage and count
- **Memory Monitoring**: Monitor memory usage and availability
- **Disk Monitoring**: Monitor disk usage and space
- **System-wide View**: Provide system-wide metrics

## 🚨 **Alerting System**

### **Alert Rule Management**

The Metrics Collector implements **sophisticated alert rule management**:

```python
@dataclass
class AlertRule:
    """Alert rule configuration."""
    name: str
    metric_name: str
    condition: str  # e.g., "value > 90"
    severity: AlertSeverity
    description: str
    enabled: bool = True
    cooldown_period: int = 300  # seconds

@dataclass
class Alert:
    """Active alert instance."""
    alert_id: str
    rule_name: str
    service_name: str
    instance_id: str
    severity: AlertSeverity
    message: str
    value: Union[int, float]
    threshold: Union[int, float]
    timestamp: float
    resolved: bool = False
    resolved_at: Optional[float] = None
```

**Alert Rule Features:**
- **Flexible Conditions**: Support complex alert conditions
- **Severity Levels**: Multiple alert severity levels
- **Cooldown Periods**: Prevent alert spam
- **Enable/Disable**: Toggle alert rules
- **Alert Tracking**: Track active alerts

### **Alert Condition Evaluation**

The Metrics Collector implements **intelligent alert condition evaluation**:

```python
def _check_alert_conditions(self):
    """Check all alert rules and trigger alerts if conditions are met."""
    try:
        for rule_name, rule in self.alert_rules.items():
            if not rule.enabled:
                continue
            
            # Check if rule is in cooldown
            if self._is_rule_in_cooldown(rule_name):
                continue
            
            # Evaluate rule condition
            if self._evaluate_alert_condition(rule):
                # Trigger alert
                self._trigger_alert(rule)
            else:
                # Resolve alert if it was active
                self._resolve_alert(rule_name)
        
    except Exception as e:
        self.logger.error(f"Alert condition checking failed: {e}")
```

**Alert Evaluation Features:**
- **Rule Iteration**: Check all enabled rules
- **Cooldown Management**: Respect cooldown periods
- **Condition Evaluation**: Evaluate alert conditions
- **Alert Triggering**: Trigger alerts when conditions are met
- **Alert Resolution**: Resolve alerts when conditions are no longer met

### **Alert Triggering and Resolution**

The Metrics Collector implements **comprehensive alert management**:

```python
def _trigger_alert(self, rule: AlertRule):
    """Trigger an alert based on rule."""
    try:
        # Find matching metrics
        matching_metrics = self._find_matching_metrics(rule.metric_name)
        
        for metric in matching_metrics:
            # Create alert
            alert = Alert(
                alert_id=str(uuid.uuid4()),
                rule_name=rule.name,
                service_name=metric.labels.get("service", "unknown"),
                instance_id=metric.labels.get("instance", "unknown"),
                severity=rule.severity,
                message=f"{rule.description}: {metric.value}",
                value=metric.value,
                threshold=self._extract_threshold(rule.condition),
                timestamp=time.time()
            )
            
            # Store alert
            self.active_alerts[alert.alert_id] = alert
            
            # Publish alert event
            self._publish_alert_event(alert)
            
            # Update rule cooldown
            self._update_rule_cooldown(rule.name)
            
    except Exception as e:
        self.logger.error(f"Alert triggering failed: {e}")
```

**Alert Management Features:**
- **Metric Matching**: Find metrics matching alert rules
- **Alert Creation**: Create alert instances
- **Event Publishing**: Publish alert events
- **Cooldown Management**: Update rule cooldowns
- **Alert Storage**: Store active alerts

## 📊 **Performance Analysis and Insights**

### **Metrics Aggregation**

The Metrics Collector implements **sophisticated metrics aggregation**:

```python
def _aggregate_metrics(self, service_name: str, metric_name: str, time_range: int = 3600) -> Dict[str, Any]:
    """Aggregate metrics for analysis."""
    try:
        # Get metrics for time range
        metrics = self._get_metrics_in_range(service_name, metric_name, time_range)
        
        if not metrics:
            return {}
        
        # Calculate statistics
        values = [m.value for m in metrics]
        
        aggregation = {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
            "percentile_95": self._calculate_percentile(values, 95),
            "percentile_99": self._calculate_percentile(values, 99),
            "time_range": time_range,
            "timestamp": time.time()
        }
        
        return aggregation
        
    except Exception as e:
        self.logger.error(f"Metrics aggregation failed: {e}")
        return {}
```

**Aggregation Features:**
- **Time Range Filtering**: Filter metrics by time range
- **Statistical Analysis**: Calculate comprehensive statistics
- **Percentile Calculation**: Calculate percentiles
- **Performance Insights**: Provide performance insights

### **Trend Analysis**

The Metrics Collector implements **trend analysis capabilities**:

```python
def _analyze_trends(self, service_name: str, metric_name: str, time_range: int = 3600) -> Dict[str, Any]:
    """Analyze trends in metrics."""
    try:
        # Get metrics for time range
        metrics = self._get_metrics_in_range(service_name, metric_name, time_range)
        
        if len(metrics) < 2:
            return {"trend": "insufficient_data"}
        
        # Sort by timestamp
        metrics.sort(key=lambda x: x.timestamp)
        
        # Calculate trend
        values = [m.value for m in metrics]
        timestamps = [m.timestamp for m in metrics]
        
        # Linear regression for trend
        trend_slope = self._calculate_trend_slope(values, timestamps)
        
        # Determine trend direction
        if trend_slope > 0.1:
            trend_direction = "increasing"
        elif trend_slope < -0.1:
            trend_direction = "decreasing"
        else:
            trend_direction = "stable"
        
        # Calculate trend strength
        trend_strength = abs(trend_slope)
        
        return {
            "trend": trend_direction,
            "strength": trend_strength,
            "slope": trend_slope,
            "data_points": len(values),
            "time_range": time_range
        }
        
    except Exception as e:
        self.logger.error(f"Trend analysis failed: {e}")
        return {"trend": "error"}
```

**Trend Analysis Features:**
- **Linear Regression**: Calculate trend slopes
- **Trend Direction**: Determine increasing/decreasing/stable trends
- **Trend Strength**: Calculate trend strength
- **Data Point Analysis**: Analyze data point distribution

### **Performance Insights**

The Metrics Collector implements **performance insights generation**:

```python
def _generate_performance_insights(self, service_name: str) -> Dict[str, Any]:
    """Generate performance insights for a service."""
    try:
        insights = {
            "service_name": service_name,
            "timestamp": time.time(),
            "insights": []
        }
        
        # Analyze response time trends
        response_time_trend = self._analyze_trends(service_name, "response_time")
        if response_time_trend.get("trend") == "increasing":
            insights["insights"].append({
                "type": "performance_degradation",
                "message": "Response time is increasing",
                "severity": "warning",
                "metric": "response_time"
            })
        
        # Analyze error rate
        error_rate = self._calculate_error_rate(service_name)
        if error_rate > 0.05:  # 5% error rate
            insights["insights"].append({
                "type": "high_error_rate",
                "message": f"Error rate is {error_rate:.2%}",
                "severity": "error",
                "metric": "error_rate"
            })
        
        # Analyze resource usage
        cpu_usage = self._get_latest_metric(service_name, "cpu_usage")
        if cpu_usage and cpu_usage > 80:
            insights["insights"].append({
                "type": "high_cpu_usage",
                "message": f"CPU usage is {cpu_usage:.1f}%",
                "severity": "warning",
                "metric": "cpu_usage"
            })
        
        return insights
        
    except Exception as e:
        self.logger.error(f"Performance insights generation failed: {e}")
        return {"service_name": service_name, "insights": [], "error": str(e)}
```

**Performance Insights Features:**
- **Trend Analysis**: Analyze performance trends
- **Error Rate Monitoring**: Monitor error rates
- **Resource Usage**: Monitor resource usage
- **Insight Generation**: Generate actionable insights
- **Severity Classification**: Classify insights by severity

## 📡 **MQTT Integration and Event Publishing**

### **Metrics Event Publishing**

The Metrics Collector publishes **comprehensive metrics events**:

```python
def _publish_metrics_event(self, event_type: str, event_data: Dict[str, Any]):
    """Publish metrics-related events."""
    try:
        event = {
            "event_type": event_type,
            "event_data": event_data,
            "timestamp": time.time(),
            "source": "metrics_collector"
        }
        
        # Publish to general metrics topic
        self.publish_message("alicia/metrics/events", event)
        
        # Publish to specific event topic
        self.publish_message(f"alicia/metrics/{event_type}", event)
        
    except Exception as e:
        self.logger.error(f"Failed to publish metrics event: {e}")
```

**Event Publishing Features:**
- **Metrics Events**: Publish metrics collection events
- **Alert Events**: Publish alert events
- **Insight Events**: Publish performance insight events
- **System Events**: Publish system-wide events

### **Service Integration**

The Metrics Collector integrates **with all bus services**:

```python
def _on_service_metrics_event(self, client, userdata, message):
    """Handle metrics events from services."""
    try:
        event_data = json.loads(message.payload.decode())
        service_name = event_data.get("service_name")
        instance_id = event_data.get("instance_id")
        metrics_data = event_data.get("metrics", [])
        
        # Process metrics from service
        self._process_service_metrics(service_name, instance_id, metrics_data)
        
    except Exception as e:
        self.logger.error(f"Service metrics event handling failed: {e}")
```

**Service Integration Features:**
- **Event Handling**: Handle metrics events from services
- **Data Processing**: Process metrics data from services
- **Service Tracking**: Track metrics per service and instance
- **Real-time Updates**: Update metrics in real-time

## 🚀 **Performance Optimization**

### **Metrics Storage Optimization**

The Metrics Collector implements **efficient metrics storage**:

```python
def _optimize_metrics_storage(self):
    """Optimize metrics storage for performance."""
    try:
        current_time = time.time()
        
        # Clean up old metrics
        for metric_name in list(self.metrics_history.keys()):
            metrics = self.metrics_history[metric_name]
            
            # Remove metrics older than retention period
            metrics[:] = [m for m in metrics if current_time - m.timestamp < self.retention_period]
            
            # Limit metrics per metric name
            if len(metrics) > self.max_history_per_metric:
                metrics[:] = metrics[-self.max_history_per_metric:]
        
        # Clean up empty metric histories
        empty_metrics = [name for name, metrics in self.metrics_history.items() if not metrics]
        for name in empty_metrics:
            del self.metrics_history[name]
        
    except Exception as e:
        self.logger.error(f"Metrics storage optimization failed: {e}")
```

**Storage Optimization Features:**
- **Retention Management**: Remove old metrics
- **Size Limits**: Limit metrics per metric name
- **Memory Management**: Clean up empty histories
- **Performance Improvement**: Optimize storage performance

### **Alert Optimization**

The Metrics Collector implements **alert optimization**:

```python
def _optimize_alert_processing(self):
    """Optimize alert processing for performance."""
    try:
        # Group alerts by service for batch processing
        alerts_by_service = defaultdict(list)
        for alert in self.active_alerts.values():
            alerts_by_service[alert.service_name].append(alert)
        
        # Process alerts in batches
        for service_name, alerts in alerts_by_service.items():
            self._process_service_alerts(service_name, alerts)
        
        # Clean up resolved alerts
        resolved_alerts = [aid for aid, alert in self.active_alerts.items() if alert.resolved]
        for alert_id in resolved_alerts:
            del self.active_alerts[alert_id]
        
    except Exception as e:
        self.logger.error(f"Alert optimization failed: {e}")
```

**Alert Optimization Features:**
- **Batch Processing**: Process alerts in batches
- **Service Grouping**: Group alerts by service
- **Cleanup**: Clean up resolved alerts
- **Performance Improvement**: Optimize alert processing

## 🔧 **Error Handling and Recovery**

### **Metrics Collection Error Handling**

The Metrics Collector implements **comprehensive error handling**:

```python
def _handle_metrics_collection_error(self, error: Exception, service_name: str, instance_id: str):
    """Handle metrics collection errors."""
    self.logger.error(f"Metrics collection failed for {service_name}/{instance_id}: {error}")
    
    # Publish error event
    error_event = {
        "service_name": service_name,
        "instance_id": instance_id,
        "error": str(error),
        "timestamp": time.time()
    }
    
    self.publish_message("alicia/metrics/collection_errors", error_event)
    
    # Attempt recovery
    if "connection" in str(error).lower():
        self._attempt_connection_recovery(service_name, instance_id)
    elif "timeout" in str(error).lower():
        self._adjust_collection_timeout(service_name, instance_id)
```

**Error Handling Features:**
- **Error Classification**: Classify errors by type
- **Error Publishing**: Publish error events
- **Recovery Strategies**: Implement recovery strategies
- **Connection Recovery**: Attempt connection recovery

### **Alert System Recovery**

The Metrics Collector implements **alert system recovery**:

```python
def _recover_alert_system(self):
    """Recover alert system from errors."""
    try:
        # Reset alert rules
        self.alert_rules = self._create_default_alert_rules()
        
        # Clear active alerts
        self.active_alerts.clear()
        
        # Publish recovery event
        self.publish_message("alicia/metrics/alert_recovery", {
            "status": "recovered",
            "timestamp": time.time()
        })
        
        self.logger.info("Alert system recovered successfully")
        
    except Exception as e:
        self.logger.error(f"Alert system recovery failed: {e}")
```

**Alert Recovery Features:**
- **Rule Reset**: Reset alert rules to defaults
- **Alert Clearing**: Clear active alerts
- **Event Publishing**: Publish recovery events
- **Error Handling**: Handle recovery errors gracefully

## 🚀 **Next Steps**

The Metrics Collector provides comprehensive system monitoring and alerting. In the next chapter, we'll examine the **Event Scheduler** that provides task scheduling and automation, including:

1. **Event Scheduling** - Schedule events and tasks
2. **Cron Integration** - Cron-like scheduling capabilities
3. **Execution Tracking** - Track task execution
4. **Recurring Tasks** - Manage recurring tasks
5. **Time-based Triggers** - Time-based event triggers

The Metrics Collector demonstrates how **comprehensive monitoring** can be implemented in a microservices architecture, providing real-time insights, alerting, and performance analysis that enable proactive system management.

---

**The Metrics Collector in Alicia represents a mature, production-ready approach to system monitoring and alerting. Every design decision is intentional, every metric serves a purpose, and every optimization contributes to the greater goal of creating a fully observable, self-healing system.**
