import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  TextField,
  Button,
  Chip,
  Alert,
  Collapse,
  IconButton,
} from '@mui/material';
import {
  Save as SaveIcon,
  PlayArrow as TestIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';

interface ServiceConfigCardProps {
  serviceName: string;
  config: Record<string, any>;
  onUpdate: (config: Record<string, any>) => void;
  onTest: () => void;
}

const ServiceConfigCard: React.FC<ServiceConfigCardProps> = ({
  serviceName,
  config,
  onUpdate,
  onTest,
}) => {
  const [editedConfig, setEditedConfig] = useState<Record<string, any>>(config);
  const [expanded, setExpanded] = useState(false);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const formatServiceName = (name: string) => {
    return name
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const handleConfigChange = (key: string, value: any) => {
    setEditedConfig(prev => ({
      ...prev,
      [key]: value
    }));
  };

  const handleSave = async () => {
    try {
      setSaving(true);
      setMessage(null);
      await onUpdate(editedConfig);
      setMessage({ type: 'success', text: 'Configuration updated successfully' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to update configuration' });
    } finally {
      setSaving(false);
    }
  };

  const handleTest = async () => {
    try {
      setTesting(true);
      setMessage(null);
      await onTest();
      setMessage({ type: 'success', text: 'Configuration test completed' });
    } catch (error) {
      setMessage({ type: 'error', text: 'Configuration test failed' });
    } finally {
      setTesting(false);
    }
  };

  const hasChanges = JSON.stringify(editedConfig) !== JSON.stringify(config);

  return (
    <Card>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" component="h3">
            {formatServiceName(serviceName)}
          </Typography>
          <Box display="flex" gap={1}>
            <Chip
              label={hasChanges ? 'Modified' : 'Saved'}
              color={hasChanges ? 'warning' : 'success'}
              size="small"
            />
            <IconButton
              onClick={() => setExpanded(!expanded)}
              size="small"
            >
              {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
            </IconButton>
          </Box>
        </Box>

        <Collapse in={expanded}>
          <Box>
            {Object.entries(editedConfig).map(([key, value]) => (
              <TextField
                key={key}
                fullWidth
                label={key.replace(/_/g, ' ').toUpperCase()}
                value={value}
                onChange={(e) => handleConfigChange(key, e.target.value)}
                margin="normal"
                size="small"
                type={key.toLowerCase().includes('password') ? 'password' : 'text'}
              />
            ))}

            <Box display="flex" gap={2} mt={2}>
              <Button
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={handleSave}
                disabled={!hasChanges || saving}
                size="small"
              >
                {saving ? 'Saving...' : 'Save'}
              </Button>
              <Button
                variant="outlined"
                startIcon={<TestIcon />}
                onClick={handleTest}
                disabled={testing}
                size="small"
              >
                {testing ? 'Testing...' : 'Test'}
              </Button>
            </Box>

            {message && (
              <Alert 
                severity={message.type} 
                sx={{ mt: 2 }}
                onClose={() => setMessage(null)}
              >
                {message.text}
              </Alert>
            )}
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default ServiceConfigCard;
