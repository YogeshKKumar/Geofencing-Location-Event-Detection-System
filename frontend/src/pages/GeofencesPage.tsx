import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Card,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Switch,
  IconButton,
  Chip,
  TextField,
  MenuItem,
  Pagination,
  Alert,
  Tooltip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteIcon from '@mui/icons-material/Delete';
import VisibilityOutlinedIcon from '@mui/icons-material/VisibilityOutlined';
import { useNavigate } from 'react-router-dom';
import { geofenceService } from '../services/geofenceService';
import { Geofence } from '../types';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useAuth } from '../context/AuthContext';

export const GeofencesPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAdmin } = useAuth();
  const [geofences, setGeofences] = useState<Geofence[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);

  const fetchGeofences = async () => {
    setLoading(true);
    try {
      const res = await geofenceService.getGeofences({
        page,
        page_size: 15,
        search: search || undefined,
        type: typeFilter || undefined,
      });
      setGeofences(res.data);
      setTotal(res.pagination.total);
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to fetch geofences' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGeofences();
  }, [page, typeFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchGeofences();
  };

  const handleToggleStatus = async (geo: Geofence) => {
    try {
      await geofenceService.setGeofenceStatus(geo.id, !geo.is_active);
      setGeofences((prev) =>
        prev.map((g) => (g.id === geo.id ? { ...g, is_active: !g.is_active } : g))
      );
      setAlert({
        type: 'success',
        message: `Geofence '${geo.name}' ${!geo.is_active ? 'enabled' : 'disabled'}`,
      });
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Status update failed' });
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteId) return;
    try {
      await geofenceService.deleteGeofence(deleteId);
      setAlert({ type: 'success', message: 'Geofence deleted successfully' });
      setConfirmOpen(false);
      setDeleteId(null);
      fetchGeofences();
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Deletion failed' });
    }
  };

  return (
    <Box sx={{ pb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            Geofence Management
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Configure circular and polygonal virtual perimeters
          </Typography>
        </Box>
        {isAdmin && (
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => navigate('/geofences/create')}
          >
            Create Geofence
          </Button>
        )}
      </Box>

      {alert && (
        <Alert severity={alert.type} sx={{ mb: 2 }} onClose={() => setAlert(null)}>
          {alert.message}
        </Alert>
      )}

      {/* Filter Toolbar */}
      <Card elevation={0} sx={{ p: 2, mb: 3, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
        <Box
          component="form"
          onSubmit={handleSearchSubmit}
          sx={{ display: 'flex', gap: 2, flexWrap: 'wrap', alignItems: 'center' }}
        >
          <TextField
            size="small"
            placeholder="Search by geofence name or description..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            sx={{ minWidth: 280, flexGrow: 1 }}
          />
          <TextField
            size="small"
            select
            label="Type"
            value={typeFilter}
            onChange={(e) => {
              setTypeFilter(e.target.value);
              setPage(1);
            }}
            sx={{ minWidth: 140 }}
          >
            <MenuItem value="">All Types</MenuItem>
            <MenuItem value="CIRCLE">Circle</MenuItem>
            <MenuItem value="POLYGON">Polygon</MenuItem>
          </TextField>
          <Button type="submit" variant="outlined">
            Filter
          </Button>
        </Box>
      </Card>

      {/* Geofences Table */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
        {loading ? (
          <LoadingSpinner message="Loading geofences..." />
        ) : (
          <TableContainer>
            <Table>
              <TableHead sx={{ bgcolor: 'grey.50' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>ID</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Name</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Type</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Geometry Details</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Active</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Created</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 600 }}>
                    Actions
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {geofences.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 4, color: 'text.secondary' }}>
                      No geofences found matching the criteria.
                    </TableCell>
                  </TableRow>
                ) : (
                  geofences.map((geo) => (
                    <TableRow key={geo.id} hover>
                      <TableCell sx={{ fontWeight: 600 }}>#{geo.id}</TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 600 }}>
                          {geo.name}
                        </Typography>
                        {geo.description && (
                          <Typography variant="caption" color="text.secondary" noWrap sx={{ maxWidth: 220, display: 'block' }}>
                            {geo.description}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={geo.type}
                          size="small"
                          color={geo.type === 'CIRCLE' ? 'success' : 'info'}
                          variant="outlined"
                          sx={{ fontWeight: 600, fontSize: '0.7rem' }}
                        />
                      </TableCell>
                      <TableCell sx={{ fontSize: '0.8125rem' }}>
                        {geo.type === 'CIRCLE' ? (
                          <>
                            Radius: <strong>{geo.radius_meters}m</strong>
                            <Typography variant="caption" sx={{ display: 'block' }} color="text.secondary">
                              Center: ({geo.center_latitude?.toFixed(4)}, {geo.center_longitude?.toFixed(4)})
                            </Typography>
                          </>
                        ) : (
                          <>
                            Polygon Vertices: <strong>{geo.points?.length ?? 0} points</strong>
                          </>
                        )}
                      </TableCell>
                      <TableCell>
                        <Switch
                          checked={geo.is_active}
                          onChange={() => handleToggleStatus(geo)}
                          disabled={!isAdmin}
                          size="small"
                        />
                      </TableCell>
                      <TableCell sx={{ fontSize: '0.8125rem' }}>
                        {new Date(geo.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="View details & map">
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => navigate(`/geofences/${geo.id}`)}
                          >
                            <VisibilityOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        {isAdmin && (
                          <Tooltip title="Delete geofence">
                            <IconButton
                              size="small"
                              color="error"
                              onClick={() => {
                                setDeleteId(geo.id);
                                setConfirmOpen(true);
                              }}
                            >
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        )}

        {total > 15 && (
          <Box sx={{ p: 2, display: 'flex', justifyContent: 'center' }}>
            <Pagination
              count={Math.ceil(total / 15)}
              page={page}
              onChange={(_, val) => setPage(val)}
              color="primary"
            />
          </Box>
        )}
      </Card>

      <ConfirmDialog
        open={confirmOpen}
        title="Delete Geofence"
        message="Are you sure you want to permanently delete this geofence boundary? Historical events associated with it will remain intact."
        confirmText="Delete"
        onConfirm={handleDeleteConfirm}
        onCancel={() => {
          setConfirmOpen(false);
          setDeleteId(null);
        }}
      />
    </Box>
  );
};
