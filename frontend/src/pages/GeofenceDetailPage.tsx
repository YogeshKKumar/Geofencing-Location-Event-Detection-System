import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Button,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Divider,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import { useParams, useNavigate } from 'react-router-dom';
import { geofenceService } from '../services/geofenceService';
import { eventService } from '../services/eventService';
import { Geofence, GeofenceEvent } from '../types';
import { GeofenceMap } from '../components/GeofenceMap';
import { EventBadge } from '../components/EventBadge';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const GeofenceDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [geofence, setGeofence] = useState<Geofence | null>(null);
  const [events, setEvents] = useState<GeofenceEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    const fetchDetails = async () => {
      try {
        const geoId = parseInt(id, 10);
        const [geoRes, evRes] = await Promise.all([
          geofenceService.getGeofenceById(geoId),
          eventService.getGeofenceEvents(geoId, { page_size: 20 }),
        ]);
        setGeofence(geoRes);
        setEvents(evRes.data);
      } catch (err) {
        console.error('Error fetching geofence detail:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDetails();
  }, [id]);

  if (loading || !geofence) {
    return <LoadingSpinner message="Loading geofence details..." />;
  }

  // Calculate center coordinate for map
  let mapCenter: [number, number] = [11.0168, 76.9558];
  if (geofence.type === 'CIRCLE' && geofence.center_latitude && geofence.center_longitude) {
    mapCenter = [geofence.center_latitude, geofence.center_longitude];
  } else if (geofence.type === 'POLYGON' && geofence.points && geofence.points.length > 0) {
    const avgLat = geofence.points.reduce((sum, p) => sum + p.latitude, 0) / geofence.points.length;
    const avgLon = geofence.points.reduce((sum, p) => sum + p.longitude, 0) / geofence.points.length;
    mapCenter = [avgLat, avgLon];
  }

  return (
    <Box sx={{ pb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/geofences')}
          color="inherit"
        >
          Back to List
        </Button>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>
          {geofence.name}
        </Typography>
        <Chip
          label={geofence.type}
          size="small"
          color={geofence.type === 'CIRCLE' ? 'success' : 'info'}
          sx={{ fontWeight: 600 }}
        />
        <Chip
          label={geofence.is_active ? 'Active' : 'Disabled'}
          size="small"
          color={geofence.is_active ? 'primary' : 'default'}
        />
      </Box>

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '1fr 2fr' }, gap: 3, mb: 3 }}>
        {/* Info Card */}
        <Box>
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2, mb: 3 }}>
            <CardContent sx={{ p: 2.5 }}>
              <Typography variant="subtitle1" sx={{ fontWeight: 600 }} gutterBottom>
                Perimeter Information
              </Typography>
              <Divider sx={{ my: 1.5 }} />

              <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                Description
              </Typography>
              <Typography variant="body2" sx={{ mb: 2 }}>
                {geofence.description || 'No description provided.'}
              </Typography>

              {geofence.type === 'CIRCLE' ? (
                <>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                    Center Coordinates
                  </Typography>
                  <Typography variant="body2" sx={{ fontFamily: 'monospace', mb: 2 }}>
                    {geofence.center_latitude?.toFixed(6)}, {geofence.center_longitude?.toFixed(6)}
                  </Typography>

                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                    Radius
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 2 }}>
                    {geofence.radius_meters} meters
                  </Typography>
                </>
              ) : (
                <>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                    Polygon Vertices
                  </Typography>
                  <Typography variant="body2" sx={{ fontWeight: 600, mb: 1 }}>
                    {geofence.points?.length ?? 0} boundary points
                  </Typography>
                  <Paper variant="outlined" sx={{ maxHeight: 160, overflow: 'auto', p: 1, mb: 2 }}>
                    {geofence.points?.map((pt, idx) => (
                      <Typography key={idx} variant="caption" sx={{ display: 'block', fontFamily: 'monospace' }}>
                        #{idx + 1}: ({pt.latitude.toFixed(5)}, {pt.longitude.toFixed(5)})
                      </Typography>
                    ))}
                  </Paper>
                </>
              )}

              <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                Created At
              </Typography>
              <Typography variant="body2">
                {new Date(geofence.created_at).toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Box>

        {/* Map View */}
        <Box>
          <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
            <CardContent sx={{ p: 2 }}>
              <GeofenceMap
                geofences={[geofence]}
                center={mapCenter}
                zoom={15}
                height="420px"
              />
            </CardContent>
          </Card>
        </Box>
      </Box>

      {/* Geofence Event History */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
        <CardContent sx={{ p: 2.5 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600 }} gutterBottom>
            Events in this Geofence ({events.length})
          </Typography>
          <TableContainer>
            <Table size="small">
              <TableHead sx={{ bgcolor: 'grey.50' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>Timestamp</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Device</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>User</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Event Type</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Transition</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Coordinates</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {events.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} align="center" sx={{ py: 3, color: 'text.secondary' }}>
                      No events recorded yet for this geofence.
                    </TableCell>
                  </TableRow>
                ) : (
                  events.map((ev) => (
                    <TableRow key={ev.id} hover>
                      <TableCell sx={{ fontSize: '0.8125rem' }}>
                        {new Date(ev.timestamp).toLocaleString()}
                      </TableCell>
                      <TableCell sx={{ fontWeight: 500 }}>{ev.device_name || `Device #${ev.device_id}`}</TableCell>
                      <TableCell>{ev.user_name || '-'}</TableCell>
                      <TableCell>
                        <EventBadge type={ev.event_type} />
                      </TableCell>
                      <TableCell sx={{ fontSize: '0.8125rem' }}>
                        {ev.previous_state} → {ev.current_state}
                      </TableCell>
                      <TableCell sx={{ fontSize: '0.75rem', fontFamily: 'monospace' }}>
                        {ev.latitude.toFixed(5)}, {ev.longitude.toFixed(5)}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};
