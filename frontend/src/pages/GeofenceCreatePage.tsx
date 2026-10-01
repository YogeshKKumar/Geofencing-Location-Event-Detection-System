import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  TextField,
  RadioGroup,
  FormControlLabel,
  Radio,
  Button,
  Slider,
  Switch,
  Alert,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Paper,
} from '@mui/material';
import DeleteIcon from '@mui/icons-material/Delete';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import SaveIcon from '@mui/icons-material/Save';
import AddLocationAltIcon from '@mui/icons-material/AddLocationAlt';
import { useNavigate } from 'react-router-dom';
import { GeofenceMap } from '../components/GeofenceMap';
import { geofenceService } from '../services/geofenceService';
import { GeofenceType } from '../types';

export const GeofenceCreatePage: React.FC = () => {
  const navigate = useNavigate();

  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [type, setType] = useState<GeofenceType>('CIRCLE');
  const [isActive, setIsActive] = useState(true);

  // Circle state
  const [centerLat, setCenterLat] = useState<number>(11.0168);
  const [centerLon, setCenterLon] = useState<number>(76.9558);
  const [radius, setRadius] = useState<number>(300);

  // Polygon state: Array of [lat, lon]
  const [polygonPoints, setPolygonPoints] = useState<Array<[number, number]>>([]);

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleMapClick = (lat: number, lon: number) => {
    if (type === 'CIRCLE') {
      setCenterLat(lat);
      setCenterLon(lon);
    } else {
      setPolygonPoints((prev) => [...prev, [lat, lon]]);
    }
  };

  const handleRemovePoint = (index: number) => {
    setPolygonPoints((prev) => prev.filter((_, idx) => idx !== index));
  };

  const handleClearPoints = () => {
    setPolygonPoints([]);
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!name.trim()) {
      setError('Please provide a geofence name');
      return;
    }

    if (type === 'CIRCLE') {
      if (!radius || radius <= 0) {
        setError('Radius must be greater than 0 meters');
        return;
      }
    } else {
      if (polygonPoints.length < 3) {
        setError('A polygon geofence requires at least 3 boundary points. Click the map to place points.');
        return;
      }
    }

    setSaving(true);
    try {
      if (type === 'CIRCLE') {
        await geofenceService.createGeofence({
          name,
          description: description || undefined,
          type: 'CIRCLE',
          center_latitude: centerLat,
          center_longitude: centerLon,
          radius_meters: radius,
          is_active: isActive,
        });
      } else {
        await geofenceService.createGeofence({
          name,
          description: description || undefined,
          type: 'POLYGON',
          is_active: isActive,
          points: polygonPoints.map((pt, idx) => ({
            latitude: pt[0],
            longitude: pt[1],
            point_order: idx,
          })),
        });
      }

      navigate('/geofences');
    } catch (err: any) {
      const msg = err.response?.data?.message || err.message || 'Failed to save geofence';
      setError(msg);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box sx={{ pb: 4 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/geofences')}
          color="inherit"
        >
          Back
        </Button>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>
          Create Geofence Boundary
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: '5fr 7fr' }, gap: 3 }}>
        {/* Form Controls Column */}
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
          <CardContent component="form" onSubmit={handleSave} sx={{ p: 3 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600 }} gutterBottom>
              Boundary Configuration
            </Typography>

            <TextField
              fullWidth
              label="Geofence Name"
              placeholder="e.g. Headquarters Compound"
              value={name}
              onChange={(e) => setName(e.target.value)}
              margin="normal"
              required
              size="small"
            />

            <TextField
              fullWidth
              label="Description"
              placeholder="Optional purpose and notes..."
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              margin="normal"
              multiline
              rows={2}
              size="small"
            />

            <Typography variant="body2" sx={{ fontWeight: 600, mt: 2, mb: 1 }}>
              Geofence Geometry Type
            </Typography>
            <RadioGroup
              row
              value={type}
              onChange={(e) => {
                setType(e.target.value as GeofenceType);
                setError(null);
              }}
            >
              <FormControlLabel value="CIRCLE" control={<Radio size="small" />} label="Circular" />
              <FormControlLabel value="POLYGON" control={<Radio size="small" />} label="Polygonal" />
            </RadioGroup>

            {type === 'CIRCLE' ? (
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
                <Typography variant="body2" sx={{ fontWeight: 600 }} gutterBottom>
                  Circle Parameters
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                  Click anywhere on the map to set the center coordinates.
                </Typography>

                <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1.5, mb: 2 }}>
                  <TextField
                    label="Center Lat"
                    type="number"
                    size="small"
                    value={centerLat}
                    onChange={(e) => setCenterLat(parseFloat(e.target.value) || 0)}
                  />
                  <TextField
                    label="Center Lon"
                    type="number"
                    size="small"
                    value={centerLon}
                    onChange={(e) => setCenterLon(parseFloat(e.target.value) || 0)}
                  />
                </Box>

                <Typography variant="body2" gutterBottom>
                  Radius: <strong>{radius} meters</strong>
                </Typography>
                <Slider
                  value={radius}
                  min={50}
                  max={5000}
                  step={25}
                  onChange={(_, val) => setRadius(val as number)}
                  valueLabelDisplay="auto"
                />
              </Box>
            ) : (
              <Box sx={{ mt: 2, p: 2, bgcolor: 'grey.50', borderRadius: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="body2" sx={{ fontWeight: 600 }}>
                    Polygon Vertices ({polygonPoints.length})
                  </Typography>
                  {polygonPoints.length > 0 && (
                    <Button size="small" color="error" onClick={handleClearPoints}>
                      Clear
                    </Button>
                  )}
                </Box>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                  Click map points in sequence to define the polygon perimeter (minimum 3 points).
                </Typography>

                {polygonPoints.length > 0 && (
                  <Paper variant="outlined" sx={{ maxHeight: 180, overflow: 'auto', p: 0.5 }}>
                    <List dense disablePadding>
                      {polygonPoints.map((pt, idx) => (
                        <ListItem
                          key={idx}
                          divider={idx < polygonPoints.length - 1}
                          secondaryAction={
                            <IconButton
                              edge="end"
                              size="small"
                              color="error"
                              onClick={() => handleRemovePoint(idx)}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          }
                        >
                          <ListItemText
                            primary={`Vertex #${idx + 1}`}
                            secondary={`(${pt[0].toFixed(5)}, ${pt[1].toFixed(5)})`}
                            sx={{
                              '& .MuiTypography-root': {
                                fontSize: '0.8rem',
                              },
                            }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Paper>
                )}
              </Box>
            )}

            <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Typography variant="body2" sx={{ fontWeight: 500 }}>
                Active immediately
              </Typography>
              <Switch
                checked={isActive}
                onChange={(e) => setIsActive(e.target.checked)}
                color="primary"
              />
            </Box>

            <Button
              type="submit"
              variant="contained"
              size="large"
              fullWidth
              disabled={saving}
              startIcon={<SaveIcon />}
              sx={{ mt: 3, py: 1.2, fontWeight: 600 }}
            >
              {saving ? 'Saving Geofence...' : 'Save Geofence'}
            </Button>
          </CardContent>
        </Card>

        {/* Map Preview Column */}
        <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
          <CardContent sx={{ p: 2 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
              <AddLocationAltIcon color="primary" />
              <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                {type === 'CIRCLE'
                  ? 'Click to position circular center'
                  : 'Click sequentially to add polygon vertices'}
              </Typography>
            </Box>
            <GeofenceMap
              height="560px"
              creationMode={type}
              center={type === 'CIRCLE' ? [centerLat, centerLon] : [11.0168, 76.9558]}
              tempCenter={type === 'CIRCLE' ? [centerLat, centerLon] : null}
              tempRadius={radius}
              tempPoints={polygonPoints}
              onMapClick={handleMapClick}
            />
          </CardContent>
        </Card>
      </Box>
    </Box>
  );
};
