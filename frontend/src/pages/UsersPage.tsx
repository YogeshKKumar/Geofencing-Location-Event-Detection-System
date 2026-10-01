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
  Pagination,
  Alert,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  MenuItem,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditOutlinedIcon from '@mui/icons-material/EditOutlined';
import DevicesIcon from '@mui/icons-material/Devices';
import { userService } from '../services/userService';
import { User, Device } from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const UsersPage: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  // Dialog State
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<'ADMIN' | 'USER'>('USER');

  // User Devices Dialog State
  const [devicesModalOpen, setDevicesModalOpen] = useState(false);
  const [userDevices, setUserDevices] = useState<Device[]>([]);
  const [selectedUserName, setSelectedUserName] = useState('');

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await userService.getUsers({
        page,
        page_size: 15,
        search: search || undefined,
      });
      setUsers(res.data);
      setTotal(res.pagination.total);
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Failed to fetch users' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [page]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchUsers();
  };

  const handleOpenDialog = (u?: User) => {
    if (u) {
      setEditingUser(u);
      setName(u.name);
      setEmail(u.email);
      setPassword('');
      setRole(u.role);
    } else {
      setEditingUser(null);
      setName('');
      setEmail('');
      setPassword('');
      setRole('USER');
    }
    setDialogOpen(true);
  };

  const handleSaveUser = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingUser) {
        await userService.updateUser(editingUser.id, {
          name,
          email,
          role,
          password: password ? password : undefined,
        });
        setAlert({ type: 'success', message: 'User updated successfully' });
      } else {
        await userService.createUser({
          name,
          email,
          password,
          role,
          is_active: true,
        });
        setAlert({ type: 'success', message: 'User created successfully' });
      }
      setDialogOpen(false);
      fetchUsers();
    } catch (err: any) {
      const msg = err.response?.data?.message || err.message || 'Failed to save user';
      setAlert({ type: 'error', message: msg });
    }
  };

  const handleToggleStatus = async (u: User) => {
    try {
      await userService.setUserStatus(u.id, !u.is_active);
      setUsers((prev) =>
        prev.map((user) => (user.id === u.id ? { ...user, is_active: !user.is_active } : user))
      );
      setAlert({
        type: 'success',
        message: `User '${u.name}' ${!u.is_active ? 'activated' : 'deactivated'}`,
      });
    } catch (err: any) {
      setAlert({ type: 'error', message: err.message || 'Status update failed' });
    }
  };

  const handleViewUserDevices = async (u: User) => {
    try {
      const res = await userService.getUserDevices(u.id);
      setUserDevices(res.data);
      setSelectedUserName(u.name);
      setDevicesModalOpen(true);
    } catch (err) {
      console.error('Failed to load user devices:', err);
    }
  };

  return (
    <Box sx={{ pb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            User Management
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Manage administrative staff, field agents, and roles
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Create User
        </Button>
      </Box>

      {alert && (
        <Alert severity={alert.type} sx={{ mb: 2 }} onClose={() => setAlert(null)}>
          {alert.message}
        </Alert>
      )}

      {/* Search */}
      <Card elevation={0} sx={{ p: 2, mb: 3, border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
        <Box component="form" onSubmit={handleSearchSubmit} sx={{ display: 'flex', gap: 2 }}>
          <TextField
            size="small"
            placeholder="Search by user name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            sx={{ flexGrow: 1 }}
          />
          <Button type="submit" variant="outlined">
            Search
          </Button>
        </Box>
      </Card>

      {/* Users Table */}
      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
        {loading ? (
          <LoadingSpinner message="Loading users..." />
        ) : (
          <TableContainer>
            <Table>
              <TableHead sx={{ bgcolor: 'grey.50' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>ID</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Name</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Email</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Role</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Active</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Created</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 600 }}>
                    Actions
                  </TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {users.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 4, color: 'text.secondary' }}>
                      No users found.
                    </TableCell>
                  </TableRow>
                ) : (
                  users.map((u) => (
                    <TableRow key={u.id} hover>
                      <TableCell sx={{ fontWeight: 600 }}>#{u.id}</TableCell>
                      <TableCell sx={{ fontWeight: 600 }}>{u.name}</TableCell>
                      <TableCell>{u.email}</TableCell>
                      <TableCell>
                        <Chip
                          label={u.role}
                          size="small"
                          color={u.role === 'ADMIN' ? 'primary' : 'default'}
                          sx={{ fontWeight: 600, fontSize: '0.7rem' }}
                        />
                      </TableCell>
                      <TableCell>
                        <Switch
                          checked={u.is_active}
                          onChange={() => handleToggleStatus(u)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell sx={{ fontSize: '0.8125rem' }}>
                        {new Date(u.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell align="right">
                        <Tooltip title="View assigned devices">
                          <IconButton
                            size="small"
                            color="info"
                            onClick={() => handleViewUserDevices(u)}
                          >
                            <DevicesIcon fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Edit user">
                          <IconButton
                            size="small"
                            onClick={() => handleOpenDialog(u)}
                          >
                            <EditOutlinedIcon fontSize="small" />
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

      {/* User Create / Edit Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="xs" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          {editingUser ? 'Edit User' : 'Create New User'}
        </DialogTitle>
        <Box component="form" onSubmit={handleSaveUser}>
          <DialogContent sx={{ pt: 1 }}>
            <TextField
              fullWidth
              label="Full Name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              margin="normal"
              required
              size="small"
            />
            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              margin="normal"
              required
              size="small"
            />
            <TextField
              fullWidth
              label={editingUser ? 'New Password (leave blank to keep current)' : 'Password'}
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              required={!editingUser}
              size="small"
            />
            <TextField
              fullWidth
              select
              label="Role"
              value={role}
              onChange={(e) => setRole(e.target.value as any)}
              margin="normal"
              size="small"
            >
              <MenuItem value="USER">USER (Field Agent)</MenuItem>
              <MenuItem value="ADMIN">ADMIN (System Administrator)</MenuItem>
            </TextField>
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

      {/* User Devices Modal */}
      <Dialog open={devicesModalOpen} onClose={() => setDevicesModalOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          Devices Assigned to {selectedUserName}
        </DialogTitle>
        <DialogContent dividers>
          {userDevices.length === 0 ? (
            <Typography variant="body2" color="text.secondary">
              No devices are currently assigned to this user.
            </Typography>
          ) : (
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>Identifier</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Device Name</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {userDevices.map((d) => (
                  <TableRow key={d.id}>
                    <TableCell sx={{ fontFamily: 'monospace' }}>{d.device_identifier}</TableCell>
                    <TableCell>{d.name}</TableCell>
                    <TableCell>
                      <Chip
                        label={d.is_active ? 'Active' : 'Inactive'}
                        size="small"
                        color={d.is_active ? 'success' : 'default'}
                        sx={{ height: 20, fontSize: '0.675rem' }}
                      />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDevicesModalOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
