import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TextField,
  MenuItem,
  Pagination,
  Button,
  Chip,
} from '@mui/material';
import FilterListIcon from '@mui/icons-material/FilterList';
import RefreshIcon from '@mui/icons-material/Refresh';
import { eventService } from '../services/eventService';
import { deviceService } from '../services/deviceService';
import { geofenceService } from '../services/geofenceService';
import { GeofenceEvent, Device, Geofence } from '../types';
import { EventBadge } from '../components/EventBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const EventsPage: React.FC = () => {
  const [events, setEvents] = useState<GeofenceEvent[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [geofences, setGeofences] = useState<Geofence[]>([]);

  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [deviceId, setDeviceId] = useState<number | ''>('');
  const [geofenceId, setGeofenceId] = useState<number | ''>('');
  const [eventType, setEventType] = useState('');
  const [loading, setLoading] = useState(true);

  // Fetch filter options
  useEffect(() => {
    const fetchOptions = async () => {
      try {
        const [devRes, geoRes] = await Promise.all([
          deviceService.getDevices({ page_size: 100 }),
          geofenceService.getGeofences({ page_size: 100 }),
        ]);
        setDevices(devRes.data);
        setGeofences(geoRes.data);
      } catch (err) {
        console.error('Failed to load filter options:', err);
      }
    };
    fetchOptions();
  }, []);

  const fetchEvents = async () => {
    setLoading(true);
    try {
      const res = await eventService.getEvents({
        page,
        page_size: 20,
        device_id: deviceId !== '' ? Number(deviceId) : undefined,
        geofence_id: geofenceId !== '' ? Number(geofenceId) : undefined,
        event_type: eventType || undefined,
      });
      setEvents(res.data);
      setTotal(res.pagination.total);
    } catch (err) {
      console.error('Failed to fetch events:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [page, deviceId, geofenceId, eventType]);

  const handleResetFilters = () => {
    setDeviceId('');
    setGeofenceId('');
    setEventType('');
    setPage(1);
  };

  return (
    <Box sx={{ pb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            Geofence Event History
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Audit of boundary entries, departures, and state confirmations
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchEvents}
          size="small"
        >
          Refresh Events
        </Button>
      </Box>

      {/* Filter Toolbar */}
      <Card elevation={0} sx={{ p: 2, mb: 3, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}>
          <TextField
            select
            size="small"
            label="Device"
            value={deviceId}
            onChange={(e) => {
              setDeviceId(e.target.value as any);
              setPage(1);
            }}
            sx={{ minWidth: 200 }}
          >
            <MenuItem value="">All Devices</MenuItem>
            {devices.map((d) => (
              <MenuItem key={d.id} value={d.id}>
                {d.name}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            select
            size="small"
            label="Geofence"
            value={geofenceId}
            onChange={(e) => {
              setGeofenceId(e.target.value as any);
              setPage(1);
            }}
            sx={{ minWidth: 200 }}
          >
            <MenuItem value="">All Geofences</MenuItem>
            {geofences.map((g) => (
              <MenuItem key={g.id} value={g.id}>
                {g.name}
              </MenuItem>
            ))}
          </TextField>

          <TextField
            select
            size="small"
            label="Event Type"
            value={eventType}
            onChange={(e) => {
              setEventType(e.target.value);
              setPage(1);
            }}
            sx={{ minWidth: 160 }}
          >
            <MenuItem value="">All Event Types</MenuItem>
            <MenuItem value="ENTER">ENTER</MenuItem>
            <MenuItem value="EXIT">EXIT</MenuItem>
            <MenuItem value="INSIDE">INSIDE</MenuItem>
            <MenuItem value="OUTSIDE">OUTSIDE</MenuItem>
          </TextField>

          {(deviceId !== '' || geofenceId !== '' || eventType !== '') && (
            <Button size="small" color="inherit" onClick={handleResetFilters}>
              Reset Filters
            </Button>
          )}
        </Box>
      </Card>

      {/* Events Table */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
        {loading ? (
          <LoadingSpinner message="Loading events..." />
        ) : (
          <TableContainer>
            <Table>
              <TableHead sx={{ bgcolor: 'grey.50' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>Timestamp</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Device</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>User</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Geofence</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Event</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>State Transition</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>GPS Coordinates</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Accuracy</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {events.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} align="center" sx={{ py: 4, color: 'text.secondary' }}>
                      No events matching the specified filter criteria.
                    </TableCell>
                  </TableRow>
                ) : (
                  events.map((ev) => (
                    <TableRow key={ev.id} hover>
                      <TableCell sx={{ fontSize: '0.8125rem' }}>
                        {new Date(ev.timestamp).toLocaleString()}
                      </TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>
                        {ev.device_name || `Device #${ev.device_id}`}
                      </TableCell>
                      <TableCell sx={{ fontSize: '0.8125rem' }}>{ev.user_name || '-'}</TableCell>
                      <TableCell sx={{ fontWeight: 500 }}>
                        {ev.geofence_name || `Geofence #${ev.geofence_id}`}
                      </TableCell>
                      <TableCell>
                        <EventBadge type={ev.event_type} />
                      </TableCell>
                      <TableCell sx={{ fontSize: '0.8125rem' }}>
                        <Chip
                          label={`${ev.previous_state} → ${ev.current_state}`}
                          size="small"
                          variant="outlined"
                          sx={{ height: 22, fontSize: '0.7rem' }}
                        />
                      </TableCell>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                        {ev.latitude.toFixed(5)}, {ev.longitude.toFixed(5)}
                      </TableCell>
                      <TableCell sx={{ fontSize: '0.75rem' }}>
                        ±{ev.accuracy_meters}m
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
