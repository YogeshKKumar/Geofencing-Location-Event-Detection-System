import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  MenuItem,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Pagination,
} from '@mui/material';
import MyLocationIcon from '@mui/icons-material/MyLocation';
import RefreshIcon from '@mui/icons-material/Refresh';
import { useSearchParams } from 'react-router-dom';
import { locationService } from '../services/locationService';
import { deviceService } from '../services/deviceService';
import { geofenceService } from '../services/geofenceService';
import { LocationRecord, Device, Geofence } from '../types';
import { GeofenceMap } from '../components/GeofenceMap';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const LocationsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialDeviceId = searchParams.get('device_id');

  const [devices, setDevices] = useState<Device[]>([]);
  const [geofences, setGeofences] = useState<Geofence[]>([]);
  const [selectedDeviceId, setSelectedDeviceId] = useState<number | ''>(
    initialDeviceId ? parseInt(initialDeviceId, 10) : ''
  );
  const [locations, setLocations] = useState<LocationRecord[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  // Load devices and geofences list
  useEffect(() => {
    const initData = async () => {
      try {
        const [devRes, geoRes] = await Promise.all([
          deviceService.getDevices({ page_size: 100 }),
          geofenceService.getGeofences({ page_size: 100, is_active: true }),
        ]);
        setDevices(devRes.data);
        setGeofences(geoRes.data);

        // If no device selected yet, default to first device
        if (!selectedDeviceId && devRes.data.length > 0) {
          setSelectedDeviceId(devRes.data[0].id);
        }
      } catch (err) {
        console.error('Failed to load initial location data:', err);
      }
    };
    initData();
  }, []);

  const fetchLocations = async () => {
    setLoading(true);
    try {
      const res = await locationService.getLocations({
        page,
        page_size: 20,
        device_id: selectedDeviceId !== '' ? Number(selectedDeviceId) : undefined,
      });
      setLocations(res.data);
      setTotal(res.pagination.total);
    } catch (err) {
      console.error('Failed to fetch locations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLocations();
  }, [selectedDeviceId, page]);

  const handleDeviceChange = (devId: number | '') => {
    setSelectedDeviceId(devId);
    setPage(1);
    if (devId) {
      setSearchParams({ device_id: devId.toString() });
    } else {
      setSearchParams({});
    }
  };

  const selectedDevice = devices.find((d) => d.id === selectedDeviceId);

  // Derive center for map
  let mapCenter: [number, number] = [11.0168, 76.9558];
  if (selectedDevice?.last_latitude && selectedDevice?.last_longitude) {
    mapCenter = [selectedDevice.last_latitude, selectedDevice.last_longitude];
  } else if (locations.length > 0) {
    mapCenter = [locations[0].latitude, locations[0].longitude];
  }

  return (
    <Box sx={{ pb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            Location Tracking & Route History
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Inspect live coordinates, route paths, and GPS accuracy fixes
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchLocations}
          size="small"
        >
          Refresh Route
        </Button>
      </Box>

      {/* Filter Toolbar */}
      <Card elevation={0} sx={{ p: 2, mb: 3, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center', flexWrap: 'wrap' }}>
          <TextField
            select
            size="small"
            label="Select Device"
            value={selectedDeviceId}
            onChange={(e) => handleDeviceChange(e.target.value as any)}
            sx={{ minWidth: 260 }}
          >
            <MenuItem value="">All Devices</MenuItem>
            {devices.map((d) => (
              <MenuItem key={d.id} value={d.id}>
                {d.name} ({d.device_identifier})
              </MenuItem>
            ))}
          </TextField>

          {selectedDevice && (
            <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
              <Chip
                icon={<MyLocationIcon fontSize="small" />}
                label={
                  selectedDevice.last_latitude != null
                    ? `Latest: ${selectedDevice.last_latitude.toFixed(4)}, ${selectedDevice.last_longitude?.toFixed(4)}`
                    : 'No fix recorded'
                }
                color="primary"
                variant="outlined"
                size="small"
              />
            </Box>
          )}
        </Box>
      </Card>

      {/* Route Map */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2, mb: 3 }}>
        <CardContent sx={{ p: 2 }}>
          <GeofenceMap
            center={mapCenter}
            zoom={14}
            height="460px"
            geofences={geofences}
            devices={selectedDevice ? [selectedDevice] : devices}
            routeHistory={locations}
          />
        </CardContent>
      </Card>

      {/* History Table */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
        {loading ? (
          <LoadingSpinner message="Loading location trail..." />
        ) : (
          <TableContainer>
            <Table size="small">
              <TableHead sx={{ bgcolor: 'grey.50' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>Fix Timestamp</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Device</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Latitude</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Longitude</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Accuracy</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Recorded</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {locations.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center" sx={{ py: 3, color: 'text.secondary' }}>
                      No location records found for this selection.
                    </TableCell>
                  </TableRow>
                ) : (
                  locations.map((loc) => (
                    <TableRow key={loc.id} hover>
                      <TableCell sx={{ fontSize: '0.8125rem' }}>
                        {new Date(loc.timestamp).toLocaleString()}
                      </TableCell>
                      <TableCell sx={{ fontWeight: 500 }}>
                        {loc.device_name || `Device #${loc.device_id}`}
                      </TableCell>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.8125rem' }}>
                        {loc.latitude.toFixed(6)}
                      </TableCell>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.8125rem' }}>
                        {loc.longitude.toFixed(6)}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={`±${loc.accuracy_meters}m`}
                          size="small"
                          color={loc.accuracy_meters <= 15 ? 'success' : 'warning'}
                          sx={{ height: 20, fontSize: '0.7rem' }}
                        />
                      </TableCell>
                      <TableCell sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>
                        {new Date(loc.created_at).toLocaleTimeString()}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {total > 20 && (
          <Box sx={{ p: 2, display: 'flex', justifyContent: 'center' }}>
            <Pagination
              count={Math.ceil(total / 20)}
              page={page}
              onChange={(_, val) => setPage(val)}
              color="primary"
            />
          </Box>
        )}
      </Card>
    </Box>
  );
};
