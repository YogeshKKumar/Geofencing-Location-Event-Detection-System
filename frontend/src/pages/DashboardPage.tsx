import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  CardHeader,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import DevicesIcon from '@mui/icons-material/Devices';
import LayersIcon from '@mui/icons-material/Layers';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import LoginIcon from '@mui/icons-material/Login';
import LogoutIcon from '@mui/icons-material/Logout';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import LocationOffIcon from '@mui/icons-material/LocationOff';
import { StatCard } from '../components/StatCard';
import { GeofenceMap } from '../components/GeofenceMap';
import { EventBadge } from '../components/EventBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { dashboardService } from '../services/dashboardService';
import { geofenceService } from '../services/geofenceService';
import { deviceService } from '../services/deviceService';
import {
  DashboardSummary,
  GeofenceEvent,
  Geofence,
  Device,
  GeofenceStatus,
} from '../types';

export const DashboardPage: React.FC = () => {
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [recentEvents, setRecentEvents] = useState<GeofenceEvent[]>([]);
  const [geofences, setGeofences] = useState<Geofence[]>([]);
  const [devices, setDevices] = useState<Device[]>([]);
  const [geofenceStatuses, setGeofenceStatuses] = useState<GeofenceStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState<Date>(new Date());

  const fetchData = async () => {
    try {
      const [sumRes, evRes, geoRes, devRes, geoStatRes] = await Promise.all([
        dashboardService.getSummary(),
        dashboardService.getRecentEvents(8),
        geofenceService.getGeofences({ page_size: 100, is_active: true }),
        deviceService.getDevices({ page_size: 100 }),
        dashboardService.getGeofenceStatuses(),
      ]);

      setSummary(sumRes);
      setRecentEvents(evRes);
      setGeofences(geoRes.data);
      setDevices(devRes.data);
      setGeofenceStatuses(geoStatRes);
      setLastRefreshed(new Date());
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  if (loading && !summary) {
    return <LoadingSpinner message="Loading dashboard telemetry..." />;
  }

  return (
    <Box sx={{ pb: 4 }}>
      {/* Header bar */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            Dashboard Overview
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Real-time geofencing metrics • Last updated: {lastRefreshed.toLocaleTimeString()}
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchData}
          size="small"
        >
          Refresh
        </Button>
      </Box>

      {/* KPI Cards Grid */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr', md: 'repeat(4, 1fr)' },
          gap: 2,
          mb: 3,
        }}
      >
        <StatCard
          title="Total Devices"
          value={summary?.total_devices ?? 0}
          subtitle={`${summary?.active_devices ?? 0} active in system`}
          icon={<DevicesIcon />}
          color="#1976d2"
        />
        <StatCard
          title="Active Geofences"
          value={summary?.active_geofences ?? 0}
          subtitle="Circles & Polygons deployed"
          icon={<LayersIcon />}
          color="#2e7d32"
        />
        <StatCard
          title="Devices Inside"
          value={summary?.devices_currently_inside ?? 0}
          subtitle="Currently within a geofence"
          icon={<CheckCircleIcon />}
          color="#0288d1"
        />
        <StatCard
          title="Devices Outside"
          value={summary?.devices_currently_outside ?? 0}
          subtitle="Clear of active perimeters"
          icon={<LocationOffIcon />}
          color="#ed6c02"
        />
      </Box>

      {/* Secondary Metrics Row */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' },
          gap: 2,
          mb: 3,
        }}
      >
        <StatCard
          title="Events Today"
          value={summary?.events_today ?? 0}
          subtitle="Total detected transitions"
          icon={<NotificationsActiveIcon />}
          color="#9c27b0"
        />
        <StatCard
          title="Enter Events"
          value={summary?.enter_events ?? 0}
          subtitle="Perimeter entries detected"
          icon={<LoginIcon />}
          color="#2e7d32"
        />
        <StatCard
          title="Exit Events"
          value={summary?.exit_events ?? 0}
          subtitle="Perimeter departures detected"
          icon={<LogoutIcon />}
          color="#d32f2f"
        />
      </Box>

      {/* Main Content: Map & Geofence Status */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', lg: '2fr 1fr' },
          gap: 3,
          mb: 3,
        }}
      >
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
          <CardHeader
            title="Live Operational Map"
            subheader="Active Geofence Perimeters & Current Device Positions"
            titleTypographyProps={{ variant: 'subtitle1', sx: { fontWeight: 600 } }}
            subheaderTypographyProps={{ variant: 'caption' }}
          />
          <CardContent sx={{ pt: 0 }}>
            <GeofenceMap
              geofences={geofences}
              devices={devices}
              height="460px"
            />
          </CardContent>
        </Card>

        {/* Geofence Occupancy Panel */}
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2, height: '100%' }}>
          <CardHeader
            title="Geofence Occupancy"
            subheader="Current device presence per boundary"
            titleTypographyProps={{ variant: 'subtitle1', sx: { fontWeight: 600 } }}
          />
          <CardContent sx={{ pt: 0 }}>
            {geofenceStatuses.length === 0 ? (
              <Typography variant="body2" color="text.secondary">
                No geofences found.
              </Typography>
            ) : (
              geofenceStatuses.map((status) => (
                <Box key={status.geofence_id} sx={{ mb: 2.5 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {status.geofence_name}
                    </Typography>
                    <Chip
                      label={`${status.current_device_count} devices`}
                      size="small"
                      color={status.current_device_count > 0 ? 'primary' : 'default'}
                      sx={{ height: 20, fontSize: '0.7rem' }}
                    />
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={Math.min(100, status.current_device_count * 33.3)}
                    sx={{ height: 6, borderRadius: 3 }}
                  />
                  {status.devices_inside.length > 0 && (
                    <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5, display: 'block' }}>
                      Inside: {status.devices_inside.join(', ')}
                    </Typography>
                  )}
                </Box>
              ))
            )}
          </CardContent>
        </Card>
      </Box>

      {/* Recent Events Table */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
        <CardHeader
          title="Recent Geofence Transitions"
          subheader="Latest detected enter, exit, and state events"
          titleTypographyProps={{ variant: 'subtitle1', sx: { fontWeight: 600 } }}
        />
        <TableContainer>
          <Table size="small">
            <TableHead sx={{ bgcolor: 'grey.50' }}>
              <TableRow>
                <TableCell sx={{ fontWeight: 600 }}>Timestamp</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Device</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Geofence</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Event Type</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Transition</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Coordinates</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {recentEvents.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 3, color: 'text.secondary' }}>
                    No events detected yet.
                  </TableCell>
                </TableRow>
              ) : (
                recentEvents.map((ev) => (
                  <TableRow key={ev.id} hover>
                    <TableCell sx={{ fontSize: '0.8125rem' }}>
                      {new Date(ev.timestamp).toLocaleTimeString()} ({new Date(ev.timestamp).toLocaleDateString()})
                    </TableCell>
                    <TableCell sx={{ fontWeight: 500 }}>{ev.device_name || `Device #${ev.device_id}`}</TableCell>
                    <TableCell>{ev.geofence_name || `Geofence #${ev.geofence_id}`}</TableCell>
                    <TableCell>
                      <EventBadge type={ev.event_type} />
                    </TableCell>
                    <TableCell sx={{ fontSize: '0.8125rem' }}>
                      {ev.previous_state} → {ev.current_state}
                    </TableCell>
                    <TableCell sx={{ fontSize: '0.75rem', color: 'text.secondary', fontFamily: 'monospace' }}>
                      {ev.latitude.toFixed(5)}, {ev.longitude.toFixed(5)}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Card>
    </Box>
  );
};
