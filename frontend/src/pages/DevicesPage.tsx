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
  TextField,
  Pagination,
  Alert,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  MenuItem,
  Chip,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import DeleteOutlineIcon from '@mui/icons-material/Delete';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import MyLocationIcon from '@mui/icons-material/MyLocation';
import { useNavigate } from 'react-router-dom';
import { deviceService } from '../services/deviceService';
import { userService } from '../services/userService';
import { Device, User } from '../types';
import { ConfirmDialog } from '../components/ConfirmDialog';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { useAuth } from '../context/AuthContext';

export const DevicesPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAdmin, user: currentUser } = useAuth();

  const [devices, setDevices] = useState<Device[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Create / Edit modal
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingDevice, setEditingDevice] = useState<Device | null>(null);
  const [identifier, setIdentifier] = useState('');
  const [name, setName] = useState('');
  const [assignedUserId, setAssignedUserId] = useState<number | ''>('');

  // Delete confirm
  const [deleteId, setDeleteId] = useState<number | null>(null);
  const [confirmOpen, setConfirmOpen] = useState(false);

  const fetchDevices = async () => {
    setLoading(true);
    try {
      const res = await deviceService.getDevices({
        page,
        page_size: 15,
        search: search || undefined,
      });
      setDevices(res.data);
      setTotal(res.pagination.total);
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to fetch devices' });
    } finally {
      setLoading(false);
    }
  };

  const fetchUsers = async () => {
    if (isAdmin) {
      try {
        const res = await userService.getUsers({ page_size: 100 });
        setUsers(res.data);
      } catch (err) {
        console.error('Failed to fetch users:', err);
      }
    }
  };

  useEffect(() => {
    fetchDevices();
    fetchUsers();
  }, [page]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchDevices();
  };

  const handleOpenDialog = (dev?: Device) => {
    if (dev) {
      setEditingDevice(dev);
      setIdentifier(dev.device_identifier);
      setName(dev.name);
      setAssignedUserId(dev.user_id ?? '');
    } else {
      setEditingDevice(null);
      setIdentifier('');
      setName('');
      setAssignedUserId(currentUser ? currentUser.id : '');
    }
    setDialogOpen(true);
  };

  const handleSaveDevice = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingDevice) {
        await deviceService.updateDevice(editingDevice.id, {
          name,
          user_id: assignedUserId === '' ? null : Number(assignedUserId),
        });
        setAlert({ type: 'success', message: 'Device updated successfully' });
      } else {
        await deviceService.createDevice({
          device_identifier: identifier,
          name,
          user_id: assignedUserId === '' ? null : Number(assignedUserId),
          is_active: true,
        });
        setAlert({ type: 'success', message: 'Device registered successfully' });
      }
      setDialogOpen(false);
      fetchDevices();
    } catch (err: any) {
      const msg = err.response?.data?.message || err.message || 'Failed to save device';
      setAlert({ type: 'error', message: msg });
    }
  };

  const handleToggleStatus = async (dev: Device) => {
    try {
      await deviceService.setDeviceStatus(dev.id, !dev.is_active);
      setDevices((prev) =>
        prev.map((d) => (d.id === dev.id ? { ...d, is_active: !d.is_active } : d))
      );
      setAlert({
        type: 'success',
        message: `Device '${dev.name}' ${!dev.is_active ? 'activated' : 'deactivated'}`,
      });
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Status change failed' });
    }
  };

  const handleDeleteConfirm = async () => {
    if (!deleteId) return;
    try {
      await deviceService.deleteDevice(deleteId);
      setAlert({ type: 'success', message: 'Device deleted successfully' });
      setConfirmOpen(false);
      setDeleteId(null);
      fetchDevices();
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Deletion failed' });
    }
  };

  return (
    <Box sx={{ pb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            Registered Devices
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Manage tracking hardware, field devices, and user assignments
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Register Device
        </Button>
      </Box>

      {alert && (
        <Alert severity={alert.type} sx={{ mb: 2 }} onClose={() => setAlert(null)}>
          {alert.message}
        </Alert>
      )}

      {/* Search Bar */}
      <Card elevation={0} sx={{ p: 2, mb: 3, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
        <Box component="form" onSubmit={handleSearchSubmit} sx={{ display: 'flex', gap: 2 }}>
          <TextField
            size="small"
            placeholder="Search by device identifier or name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            sx={{ flexGrow: 1 }}
          />
          <Button type="submit" variant="outlined">
            Search
          </Button>
        </Box>
      </Card>

      {/* Table */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
        {loading ? (
          <LoadingSpinner message="Loading devices..." />
        ) : (
          <TableContainer>
            <Table>
              <TableHead sx={{ bgcolor: 'grey.50' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>ID</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Identifier</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Name</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Assigned User</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Latest Location</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Active</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 600 }}>
                    Actions
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {devices.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 4, color: 'text.secondary' }}>
                      No devices registered.
                    </TableCell>
                  </TableRow>
                ) : (
                  devices.map((dev) => (
                    <TableRow key={dev.id} hover>
                      <TableCell sx={{ fontWeight: 600 }}>#{dev.id}</TableCell>
                      <TableCell>
                        <Chip
                          label={dev.device_identifier}
                          size="small"
                          sx={{ fontFamily: 'monospace', fontWeight: 600 }}
                        />
                      </TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>{dev.name}</TableCell>
                      <TableCell>{dev.user_name || <Typography variant="caption" color="text.secondary">Unassigned</Typography>}</TableCell>
                      <TableCell sx={{ fontSize: '0.8125rem' }}>
                        {dev.last_latitude != null && dev.last_longitude != null ? (
                          <>
                            <Typography variant="body2" sx={{ fontFamily: 'monospace', fontSize: '0.75rem' }}>
                              {dev.last_latitude.toFixed(4)}, {dev.last_longitude.toFixed(4)}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                              {dev.last_location_at ? new Date(dev.last_location_at).toLocaleTimeString() : ''}
                            </Typography>
                          </>
                        ) : (
                          <Typography variant="caption" color="text.secondary">No fix yet</Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Switch
                          checked={dev.is_active}
                          onChange={() => handleToggleStatus(dev)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="View location history">
                          <IconButton
                            size="small"
                            color="primary"
                            onClick={() => navigate(`/locations?device_id=${dev.id}`)}
                          >
                            <MyLocationIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit device">
                          <IconButton
                            size="small"
                            onClick={() => handleOpenDialog(dev)}
                          >
                            <EditOutlinedIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete device">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => {
                              setDeleteId(dev.id);
                              setConfirmOpen(true);
                            }}
                          >
                            <DeleteOutlineIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
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

      {/* Create / Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          {editingDevice ? 'Edit Device' : 'Register New Device'}
        </DialogTitle>
        <Box component="form" onSubmit={handleSaveDevice}>
          <DialogContent sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Device Identifier"
              placeholder="e.g. DEV-FLEET-101"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              margin="normal"
              required
              disabled={!!editingDevice}
              size="small"
              helperText={editingDevice ? 'Identifier cannot be modified' : 'Unique hardware or serial ID'}
            />
            <TextField
              fullWidth
              label="Device Name"
              placeholder="e.g. Delivery Van Delta"
              value={name}
              onChange={(e) => setName(e.target.value)}
              margin="normal"
              required
              size="small"
            />
            {isAdmin && (
              <TextField
                fullWidth
                select
                label="Assign to User"
                value={assignedUserId}
                onChange={(e) => setAssignedUserId(e.target.value as any)}
                margin="normal"
                size="small"
              >
                <MenuItem value="">Unassigned</MenuItem>
                {users.map((u) => (
                  <MenuItem key={u.id} value={u.id}>
                    {u.name} ({u.email})
                  </MenuItem>
                ))}
              </TextField>
            )}
          </DialogContent>
          <DialogActions sx={{ p: 2, pt: 0 }}>
            <Button onClick={() => setDialogOpen(false)} color="inherit">
              Cancel
            </Button>
            <Button type="submit" variant="contained">
              Save
            </Button>
          </DialogActions>
        </Box>
      </Dialog>

      <ConfirmDialog
        open={confirmOpen}
        title="Delete Device"
        message="Are you sure you want to delete this device? Historical location and geofence events for this device will also be removed."
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
