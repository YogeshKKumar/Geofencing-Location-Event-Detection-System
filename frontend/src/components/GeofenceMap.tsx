import React from 'react';
import {
  MapContainer,
  TileLayer,
  Circle,
  Polygon,
  Marker,
  Popup,
  Polyline,
  useMapEvents,
} from 'react-leaflet';
import L from 'leaflet';
import { Box, Typography, Chip, Paper } from '@mui/material';
import { Geofence, Device, LocationRecord } from '../types';

// Fix for default Leaflet icon paths in bundlers
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom device icon
const createDeviceIcon = (color: string = '#1976d2') =>
  L.divIcon({
    className: 'custom-device-marker',
    html: `<div style="
      background-color: ${color};
      width: 28px;
      height: 28px;
      border-radius: 50%;
      border: 3px solid white;
      box-shadow: 0 2px 5px rgba(0,0,0,0.4);
      display: flex;
      align-items: center;
      justify-content: center;
      color: white;
      font-size: 14px;
    ">📍</div>`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    popupAnchor: [0, -14],
  });

interface MapClickHandlerProps {
  onMapClick?: (lat: number, lon: number) => void;
}

const MapClickHandler: React.FC<MapClickHandlerProps> = ({ onMapClick }) => {
  useMapEvents({
    click(e) {
      if (onMapClick) {
        onMapClick(e.latlng.lat, e.latlng.lng);
      }
    },
  });
  return null;
};

interface GeofenceMapProps {
  geofences?: Geofence[];
  devices?: Device[];
  routeHistory?: LocationRecord[];
  center?: [number, number];
  zoom?: number;
  height?: string | number;
  onMapClick?: (lat: number, lon: number) => void;
  creationMode?: 'NONE' | 'CIRCLE' | 'POLYGON';
  tempCenter?: [number, number] | null;
  tempRadius?: number;
  tempPoints?: Array<[number, number]>;
}

export const GeofenceMap: React.FC<GeofenceMapProps> = ({
  geofences = [],
  devices = [],
  routeHistory = [],
  center = [11.0168, 76.9558],
  zoom = 14,
  height = '500px',
  onMapClick,
  creationMode = 'NONE',
  tempCenter,
  tempRadius = 300,
  tempPoints = [],
}) => {
  return (
    <Box
      sx={{
        height,
        width: '100%',
        borderRadius: 2,
        overflow: 'hidden',
        border: '1px solid',
        borderColor: 'divider',
        position: 'relative',
      }}
    >
      <MapContainer
        center={center}
        zoom={zoom}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {/* Map click listener */}
        <MapClickHandler onMapClick={onMapClick} />

        {/* Existing Geofences */}
        {geofences.map((geo) => {
          if (!geo.is_active) return null;

          if (geo.type === 'CIRCLE' && geo.center_latitude && geo.center_longitude && geo.radius_meters) {
            return (
              <Circle
                key={`circle-${geo.id}`}
                center={[geo.center_latitude, geo.center_longitude]}
                radius={geo.radius_meters}
                pathOptions={{
                  color: '#2e7d32',
                  fillColor: '#4caf50',
                  fillOpacity: 0.2,
                  weight: 2,
                }}
              >
                <Popup>
                  <Paper elevation={0} sx={{ p: 0.5 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      {geo.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                      Type: Circular Geofence
                    </Typography>
                    <Typography variant="caption" sx={{ display: 'block' }}>
                      Radius: {geo.radius_meters}m
                    </Typography>
                    {geo.description && (
                      <Typography variant="caption" color="text.secondary">
                        {geo.description}
                      </Typography>
                    )}
                  </Paper>
                </Popup>
              </Circle>
            );
          }

          if (geo.type === 'POLYGON' && geo.points && geo.points.length >= 3) {
            const positions: [number, number][] = geo.points
              .sort((a, b) => (a.point_order ?? 0) - (b.point_order ?? 0))
              .map((p) => [p.latitude, p.longitude]);

            return (
              <Polygon
                key={`polygon-${geo.id}`}
                positions={positions}
                pathOptions={{
                  color: '#0288d1',
                  fillColor: '#03a9f4',
                  fillOpacity: 0.25,
                  weight: 2,
                }}
              >
                <Popup>
                  <Paper elevation={0} sx={{ p: 0.5 }}>
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                      {geo.name}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                      Type: Polygon Geofence ({positions.length} points)
                    </Typography>
                    {geo.description && (
                      <Typography variant="caption" color="text.secondary">
                        {geo.description}
                      </Typography>
                    )}
                  </Paper>
                </Popup>
              </Polygon>
            );
          }

          return null;
        })}

        {/* Temporary Draft Elements during creation */}
        {creationMode === 'CIRCLE' && tempCenter && (
          <Circle
            center={tempCenter}
            radius={tempRadius}
            pathOptions={{
              color: '#ed6c02',
              fillColor: '#ff9800',
              fillOpacity: 0.35,
              weight: 2,
              dashArray: '4, 4',
            }}
          />
        )}

        {creationMode === 'POLYGON' && tempPoints.length > 0 && (
          <>
            {tempPoints.map((pt, idx) => (
              <Marker
                key={`temp-pt-${idx}`}
                position={pt}
                icon={createDeviceIcon('#ed6c02')}
              />
            ))}
            {tempPoints.length >= 3 ? (
              <Polygon
                positions={tempPoints}
                pathOptions={{
                  color: '#ed6c02',
                  fillColor: '#ff9800',
                  fillOpacity: 0.35,
                  weight: 2,
                  dashArray: '4, 4',
                }}
              />
            ) : tempPoints.length === 2 ? (
              <Polyline
                positions={tempPoints}
                pathOptions={{ color: '#ed6c02', weight: 2, dashArray: '4, 4' }}
              />
            ) : null}
          </>
        )}

        {/* Route History Polyline */}
        {routeHistory.length > 1 && (
          <Polyline
            positions={routeHistory.map((loc) => [loc.latitude, loc.longitude])}
            pathOptions={{
              color: '#9c27b0',
              weight: 3,
              opacity: 0.85,
            }}
          />
        )}

        {/* Device Markers */}
        {devices.map((dev) => {
          if (dev.last_latitude == null || dev.last_longitude == null) return null;

          return (
            <Marker
              key={`device-${dev.id}`}
              position={[dev.last_latitude, dev.last_longitude]}
              icon={createDeviceIcon(dev.is_active ? '#1976d2' : '#757575')}
            >
              <Popup>
                <Paper elevation={0} sx={{ p: 1, minWidth: 180 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 700 }}>
                    {dev.name}
                  </Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                    ID: {dev.device_identifier}
                  </Typography>
                  {dev.user_name && (
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                      User: {dev.user_name}
                    </Typography>
                  )}
                  <Box sx={{ mt: 1, mb: 1 }}>
                    <Chip
                      label={dev.is_active ? 'Active' : 'Inactive'}
                      size="small"
                      color={dev.is_active ? 'success' : 'default'}
                      sx={{ height: 20, fontSize: '0.65rem', mr: 0.5 }}
                    />
                  </Box>
                  <Typography variant="caption" sx={{ display: 'block' }}>
                    Lat: {dev.last_latitude.toFixed(5)}, Lon: {dev.last_longitude.toFixed(5)}
                  </Typography>
                  {dev.last_location_at && (
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                      Updated: {new Date(dev.last_location_at).toLocaleTimeString()}
                    </Typography>
                  )}
                </Paper>
              </Popup>
            </Marker>
          );
        })}
      </MapContainer>
    </Box>
  );
};
