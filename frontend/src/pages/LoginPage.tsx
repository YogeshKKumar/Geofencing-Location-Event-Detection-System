import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  Tabs,
  Tab,
  Divider,
  Chip,
  CircularProgress,
} from '@mui/material';
import GpsFixedIcon from '@mui/icons-material/GpsFixed';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import PersonAddOutlinedIcon from '@mui/icons-material/PersonAddOutlined';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';

export const LoginPage: React.FC = () => {
  const { login, register, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  const [tabIndex, setTabIndex] = useState(0);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('admin@example.com');
  const [password, setPassword] = useState('Admin@123');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (tabIndex === 0) {
        await login(email, password);
      } else {
        if (!name.trim()) {
          setError('Please provide your full name');
          setLoading(false);
          return;
        }
        await register(name, email, password);
      }
      navigate('/dashboard', { replace: true });
    } catch (err: any) {
      const msg = err.response?.data?.message || err.message || 'Authentication failed';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const setDemoCredentials = (role: 'ADMIN' | 'USER') => {
    setTabIndex(0);
    setError(null);
    if (role === 'ADMIN') {
      setEmail('admin@example.com');
      setPassword('Admin@123');
    } else {
      setEmail('user1@example.com');
      setPassword('User1@123');
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: '#f4f6f8',
        p: 2,
      }}
    >
      <Card sx={{ maxWidth: 440, width: '100%', borderRadius: 3, boxShadow: 3 }}>
        <Box sx={{ p: 3, textAlign: 'center', pb: 1 }}>
          <Box
            sx={{
              width: 52,
              height: 52,
              borderRadius: 2,
              bgcolor: 'primary.main',
              color: 'white',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              mb: 1.5,
            }}
          >
            <GpsFixedIcon fontSize="large" />
          </Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            GeoTrack System
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Geofencing & Location Event Detection Platform
          </Typography>
        </Box>

        <Tabs
          value={tabIndex}
          onChange={(_, val) => {
            setTabIndex(val);
            setError(null);
          }}
          variant="fullWidth"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab icon={<LockOutlinedIcon fontSize="small" />} iconPosition="start" label="Sign In" />
          <Tab icon={<PersonAddOutlinedIcon fontSize="small" />} iconPosition="start" label="Register" />
        </Tabs>

        <CardContent sx={{ p: 3 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit}>
            {tabIndex === 1 && (
              <TextField
                fullWidth
                label="Full Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                margin="normal"
                required
                size="small"
              />
            )}

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
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              margin="normal"
              required
              size="small"
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading}
              sx={{ mt: 3, mb: 2, py: 1.2, fontWeight: 600 }}
            >
              {loading ? (
                <CircularProgress size={24} color="inherit" />
              ) : tabIndex === 0 ? (
                'Sign In'
              ) : (
                'Create Account'
              )}
            </Button>
          </Box>

          <Divider sx={{ my: 2 }}>
            <Typography variant="caption" color="text.secondary">
              DEMO CREDENTIALS
            </Typography>
          </Divider>

          <Box sx={{ display: 'flex', gap: 1, justifyContent: 'center' }}>
            <Chip
              label="Admin: admin@example.com"
              onClick={() => setDemoCredentials('ADMIN')}
              color="primary"
              variant="outlined"
              size="small"
              clickable
            />
            <Chip
              label="User: user1@example.com"
              onClick={() => setDemoCredentials('USER')}
              variant="outlined"
              size="small"
              clickable
            />
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};
