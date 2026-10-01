import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  Button,
  FormControlLabel,
  Checkbox,
  Paper,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import LayersIcon from '@mui/icons-material/Layers';
import { geofenceService } from '../services/geofenceService';
import { deviceService } from '../services/deviceService';
import { Geofence, Device } from '../types';
import { GeofenceMap } from '../components/GeofenceMap';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const LiveMapPage: React.FC = () => {
  const [geofences, setGeofences] = useState<Geofence[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [loading, setLoading] = useState(true);

  const [showCircles, setShowCircles] = useState(true);
  const [showPolygons, setShowPolygons] = useState(true);

  const fetchData = async () => {
    try {
      const [geoRes, devRes] = await Promise.all([
        geofenceService.getGeofences({ page_size: 100, is_active: true }),
        deviceService.getDevices({ page_size: 100 }),
      ]);
      setGeofences(geoRes.data);
      setDevices(devRes.data);
    } catch (err) {
      console.error('Failed to load map data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000); // 10s live polling
    return () => clearInterval(interval);
  }, []);

  const filteredGeofences = geofences.filter((g) => {
    if (g.type === 'CIRCLE' && !showCircles) return false;
    if (g.type === 'POLYGON' && !showPolygons) return false;
    return true;
  });

  return (
    <Box sx={{ pb: 4, height: 'calc(100vh - 110px)', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            Live Operational Map
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Continuous real-time positioning and active geofence coverage
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <FormControlLabel
            control={
              <Checkbox
                checked={showCircles}
                onChange={(e) => setShowCircles(e.target.checked)}
                size="small"
                color="success"
              />
            }
            label={<Typography variant="body2">Circles ({geofences.filter(g => g.type === 'CIRCLE').length})</Typography>}
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={showPolygons}
                onChange={(e) => setShowPolygons(e.target.checked)}
                size="small"
                color="info"
              />
            }
            label={<Typography variant="body2">Polygons ({geofences.filter(g => g.type === 'POLYGON').length})</Typography>}
          />
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={fetchData}
            size="small"
          >
            Poll Now
          </Button>
        </Box>
      </Box>

      <Card elevation={0} sx={{ flexGrow: 1, border: '1px solid', borderColor: 'divider', borderRadius: 2, overflow: 'hidden' }}>
        {loading ? (
          <LoadingSpinner message="Rendering GIS map canvas..." minHeight="100%" />
        ) : (
          <GeofenceMap
            geofences={filteredGeofences}
            devices={devices}
            height="100%"
            zoom={14}
          />
        )}
      </Card>
    </Box>
  );
};
