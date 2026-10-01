import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  TextField,
  Button,
  MenuItem,
  Alert,
  Paper,
  Divider,
  Chip,
  CircularProgress,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import GpsFixedIcon from '@mui/icons-material/GpsFixed';
import TuneIcon from '@mui/icons-material/Tune';
import { deviceService } from '../services/deviceService';
import { locationService, LocationProcessResult } from '../services/locationService';
import { Device } from '../types';
import { EventBadge } from '../components/EventBadge';

export const SettingsPage: React.FC = () => {
  const [devices, setDevices] = useState<Device[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<number | ''>('');
  const [latitude, setLatitude] = useState<number>(11.0168);
  const [longitude, setLongitude] = useState<number>(76.9558);
  const [accuracy, setAccuracy] = useState<number>(5.0);

  const [simulating, setSimulating] = useState(false);
  const [result, setResult] = useState<LocationProcessResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadDevices = async () => {
      try {
        const res = await deviceService.getDevices({ page_size: 100, is_active: true });
        setDevices(res.data);
        if (res.data.length > 0) {
          setSelectedDeviceId(res.data[0].id);
        }
      } catch (err) {
        console.error('Failed to load devices:', err);
      }
    };
    loadDevices();
  }, []);

  const handleApplyPreset = (lat: number, lon: number, acc: number) => {
    setLatitude(lat);
    setLongitude(lon);
    setAccuracy(acc);
    setResult(null);
    setError(null);
  };

  const handleSendLocation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedDeviceId) {
      setError('Please select a device to simulate GPS fix');
      return;
    }

    setSimulating(true);
    setError(null);
    try {
      const res = await locationService.sendLocation({
        device_id: Number(selectedDeviceId),
        latitude,
        longitude,
        accuracy_meters: accuracy,
      });
      setResult(res);
    } catch (err: any) {
      const msg = err.response?.data?.message || err.message || 'Failed to simulate GPS location fix';
      setError(msg);
    } finally {
      setSimulating(false);
    }
  };

  return (
    <Box sx={{ pb: 4 }}>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>
          System Settings & GPS Simulator
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Platform parameters, geofencing rules, and interactive event detection tester
        </Typography>
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '7fr 5fr' }, gap: 3 }}>
        {/* Left Column: Live GPS Simulator */}
        <Box>
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
                <GpsFixedIcon color="primary" />
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  Live GPS Ingestion Simulator
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2.5 }}>
                Simulate a real-time GPS coordinate transmission from a device and immediately inspect the geofencing engine's state transitions.
              </Typography>

              {error && (
                <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
                  {error}
                </Alert>
              )}

              {/* Presets */}
              <Box sx={{ mb: 2.5 }}>
                <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600, display: 'block', mb: 1 }}>
                  QUICK PRESET COORDINATES:
                </Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  <Chip
                    label="Inside Office Circle"
                    onClick={() => handleApplyPreset(11.0168, 76.9558, 5.0)}
                    color="primary"
                    variant="outlined"
                    clickable
                  />
                  <Chip
                    label="Inside Warehouse Polygon"
                    onClick={() => handleApplyPreset(11.0165, 76.9560, 5.0)}
                    color="info"
                    variant="outlined"
                    clickable
                  />
                  <Chip
                    label="Outside All Geofences (~4km)"
                    onClick={() => handleApplyPreset(11.0500, 76.9600, 10.0)}
                    variant="outlined"
                    clickable
                  />
                  <Chip
                    label="Boundary Jitter (±50m noise)"
                    onClick={() => handleApplyPreset(11.0213, 76.9558, 50.0)}
                    color="warning"
                    variant="outlined"
                    clickable
                  />
                </Box>
              </Box>

              <Box component="form" onSubmit={handleSendLocation}>
                <TextField
                  fullWidth
                  select
                  label="Target Device"
                  value={selectedDeviceId}
                  onChange={(e) => setSelectedDeviceId(e.target.value as any)}
                  margin="normal"
                  size="small"
                  required
                >
                  {devices.map((d) => (
                    <MenuItem key={d.id} value={d.id}>
                      {d.name} ({d.device_identifier})
                    </MenuItem>
                  ))}
                </TextField>

                <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr 1fr' }, gap: 2, mt: 1 }}>
                  <TextField
                    fullWidth
                    label="Latitude"
                    type="number"
                    value={latitude}
                    onChange={(e) => setLatitude(parseFloat(e.target.value))}
                    size="small"
                    required
                    slotProps={{ htmlInput: { step: '0.0001' } }}
                  />
                  <TextField
                    fullWidth
                    label="Longitude"
                    type="number"
                    value={longitude}
                    onChange={(e) => setLongitude(parseFloat(e.target.value))}
                    size="small"
                    required
                    slotProps={{ htmlInput: { step: '0.0001' } }}
                  />
                  <TextField
                    fullWidth
                    label="Accuracy (meters)"
                    type="number"
                    value={accuracy}
                    onChange={(e) => setAccuracy(parseFloat(e.target.value))}
                    size="small"
                    required
                    slotProps={{ htmlInput: { min: 0, step: '1' } }}
                  />
                </Box>

                <Button
                  type="submit"
                  variant="contained"
                  fullWidth
                  size="large"
                  disabled={simulating}
                  startIcon={<SendIcon />}
                  sx={{ mt: 3, py: 1.2, fontWeight: 600 }}
                >
                  {simulating ? <CircularProgress size={24} color="inherit" /> : 'Send GPS Location Fix'}
                </Button>
              </Box>

              {/* Simulation Result Output */}
              {result && (
                <Paper variant="outlined" sx={{ mt: 3, p: 2, bgcolor: '#fbfbfb', borderRadius: 2 }}>
                  <Typography variant="subtitle2" color="primary" sx={{ fontWeight: 700 }} gutterBottom>
                    Engine Processing Result (Location #{result.location_id})
                  </Typography>
                  <Typography variant="body2" sx={{ mb: 1 }}>
                    Detected Transitions: <strong>{result.events.length}</strong>
                  </Typography>

                  {result.events.length === 0 ? (
                    <Typography variant="caption" color="text.secondary">
                      No new boundary state transition occurred for this fix (duplicate or steady state).
                    </Typography>
                  ) : (
                    result.events.map((ev, idx) => (
                      <Box
                        key={idx}
                        sx={{
                          p: 1.5,
                          mt: 1,
                          bgcolor: 'white',
                          borderRadius: 1.5,
                          border: '1px solid',
                          borderColor: 'divider',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'space-between',
                        }}
                      >
                        <Box>
                          <Typography variant="body2" sx={{ fontWeight: 600 }}>
                            {ev.geofence_name || `Geofence #${ev.geofence_id}`}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            Previous: {ev.previous_state} → Current: {ev.current_state}
                          </Typography>
                        </Box>
                        <EventBadge type={ev.event_type} />
                      </Box>
                    ))
                  )}
                </Paper>
              )}
            </CardContent>
          </Card>
        </Box>

        {/* Right Column: Engine Rules & Parameters */}
        <Box>
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2, mb: 3 }}>
            <CardContent sx={{ p: 3 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 1 }}>
                <TuneIcon color="primary" />
                <Typography variant="subtitle1" sx={{ fontWeight: 600 }}>
                  Geofencing Rules & Engine Parameters
                </Typography>
              </Box>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 2 }}>
                Current production thresholds governing debounce and noise suppression
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  GPS Accuracy Threshold:
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>100 meters</strong> — Fixes with accuracy greater than 100m are classified as degraded; previous boundary states are conservatively maintained.
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  Boundary Buffer (Hysteresis):
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>10 meters</strong> — Devices inside a boundary are granted an exit buffer to prevent rapid flip-flop oscillations at border perimeters.
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  Duplicate Prevention Window:
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  <strong>5 seconds</strong> — Identical GPS coordinates from the same hardware within 5 seconds are safely deduplicated.
                </Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }}>
                  Geodetic Algorithms:
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Haversine formula on WGS-84 ellipsoid (6,371,000m radius) for circular perimeters; Jordan Curve Theorem & Shapely GEOS for polygonal perimeters.
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Box>
      </Box>
    </Box>

  );
};
