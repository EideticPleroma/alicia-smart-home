import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  CircularProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
} from '@mui/material';
import {
  Science as ScienceIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

import { apiService, TestRequest, TestResult } from '../services/api';

const Testing: React.FC = () => {
  const [testType, setTestType] = useState('end_to_end');
  const [inputText, setInputText] = useState('Hello Alicia, how are you?');
  const [component, setComponent] = useState('');
  const [running, setRunning] = useState(false);
  const [testResults, setTestResults] = useState<TestResult[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const testTypes = [
    { value: 'stt', label: 'Speech-to-Text' },
    { value: 'tts', label: 'Text-to-Speech' },
    { value: 'grok4', label: 'Grok-4 AI' },
    { value: 'end_to_end', label: 'End-to-End' },
    { value: 'component', label: 'Component' },
  ];

  const components = [
    { value: 'whisper', label: 'Whisper STT' },
    { value: 'piper', label: 'Piper TTS' },
    { value: 'alicia_assistant', label: 'Alicia Assistant' },
    { value: 'mqtt', label: 'MQTT Broker' },
    { value: 'homeassistant', label: 'Home Assistant' },
  ];

  const fetchTestResults = async () => {
    try {
      setLoading(true);
      const results = await apiService.getTestResults(20);
      setTestResults(results);
      setError(null);
    } catch (err) {
      setError('Failed to fetch test results');
      console.error('Error fetching test results:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTestResults();
  }, []);

  const handleRunTest = async () => {
    try {
      setRunning(true);
      setError(null);

      const testRequest: TestRequest = {
        test_type: testType,
        input_text: inputText,
        component: testType === 'component' ? component : undefined,
      };

      const result = await apiService.runTest(testRequest);
      console.log('Test started:', result);

      // Refresh test results after a short delay
      setTimeout(() => {
        fetchTestResults();
      }, 2000);

    } catch (err) {
      setError('Failed to run test');
      console.error('Error running test:', err);
    } finally {
      setRunning(false);
    }
  };

  const handleRunTestSuite = async () => {
    try {
      setRunning(true);
      setError(null);

      const result = await apiService.runTestSuite();
      console.log('Test suite started:', result);

      // Refresh test results after a short delay
      setTimeout(() => {
        fetchTestResults();
      }, 2000);

    } catch (err) {
      setError('Failed to run test suite');
      console.error('Error running test suite:', err);
    } finally {
      setRunning(false);
    }
  };

  const handleDeleteTest = async (testId: string) => {
    try {
      await apiService.deleteTestResult(testId);
      await fetchTestResults();
    } catch (err) {
      console.error('Error deleting test:', err);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'running':
        return 'info';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    return `${(ms / 1000).toFixed(1)}s`;
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <ScienceIcon />
        <Typography variant="h4" component="h1">
          Testing Interface
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Test Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Run Test
              </Typography>

              <FormControl fullWidth margin="normal">
                <InputLabel>Test Type</InputLabel>
                <Select
                  value={testType}
                  onChange={(e) => setTestType(e.target.value)}
                  label="Test Type"
                >
                  {testTypes.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {testType === 'component' && (
                <FormControl fullWidth margin="normal">
                  <InputLabel>Component</InputLabel>
                  <Select
                    value={component}
                    onChange={(e) => setComponent(e.target.value)}
                    label="Component"
                  >
                    {components.map((comp) => (
                      <MenuItem key={comp.value} value={comp.value}>
                        {comp.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              )}

              <TextField
                fullWidth
                label="Input Text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                margin="normal"
                multiline
                rows={3}
              />

              <Box display="flex" gap={2} mt={2}>
                <Button
                  variant="contained"
                  startIcon={<PlayIcon />}
                  onClick={handleRunTest}
                  disabled={running || !inputText.trim()}
                >
                  {running ? 'Running...' : 'Run Test'}
                </Button>
                <Button
                  variant="outlined"
                  startIcon={<PlayIcon />}
                  onClick={handleRunTestSuite}
                  disabled={running}
                >
                  Run Test Suite
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>

        {/* Test Results */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">
                  Recent Test Results
                </Typography>
                <IconButton onClick={fetchTestResults} size="small">
                  <RefreshIcon />
                </IconButton>
              </Box>

              {testResults.length === 0 ? (
                <Typography color="text.secondary">
                  No test results available
                </Typography>
              ) : (
                <List dense>
                  {testResults.map((result) => (
                    <ListItem key={result.test_id} divider>
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="body2">
                              {result.test_type.toUpperCase()}
                            </Typography>
                            <Chip
                              label={result.status.toUpperCase()}
                              color={getStatusColor(result.status) as any}
                              size="small"
                            />
                          </Box>
                        }
                        secondary={
                          <Box>
                            <Typography variant="caption" color="text.secondary">
                              {result.input}
                            </Typography>
                            <br />
                            <Typography variant="caption" color="text.secondary">
                              {formatDuration(result.duration_ms)} • {new Date(result.timestamp).toLocaleString()}
                            </Typography>
                            {result.error && (
                              <Typography variant="caption" color="error" display="block">
                                Error: {result.error}
                              </Typography>
                            )}
                          </Box>
                        }
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          onClick={() => handleDeleteTest(result.test_id)}
                          size="small"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default Testing;

