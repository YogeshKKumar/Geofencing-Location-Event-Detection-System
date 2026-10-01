import React from 'react';
import { Chip } from '@mui/material';
import LoginIcon from '@mui/icons-material/Login';
import LogoutIcon from '@mui/icons-material/Logout';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircle';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import { EventType, GeofenceState } from '../types';

interface EventBadgeProps {
  type: EventType | GeofenceState | string;
  size?: 'small' | 'medium';
}

export const EventBadge: React.FC<EventBadgeProps> = ({ type, size = 'small' }) => {
  const normalized = type.toUpperCase();

  switch (normalized) {
    case 'ENTER':
      return (
        <Chip
          icon={<LoginIcon fontSize="small" />}
          label="ENTER"
          size={size}
          sx={{
            bgcolor: 'success.light',
            color: 'success.dark',
            fontWeight: 600,
            border: '1px solid',
            borderColor: 'success.main',
          }}
        />
      );
    case 'EXIT':
      return (
        <Chip
          icon={<LogoutIcon fontSize="small" />}
          label="EXIT"
          size={size}
          sx={{
            bgcolor: 'error.light',
            color: 'error.dark',
            fontWeight: 600,
            border: '1px solid',
            borderColor: 'error.main',
          }}
        />
      );
    case 'INSIDE':
      return (
        <Chip
          icon={<CheckCircleOutlineIcon fontSize="small" />}
          label="INSIDE"
          size={size}
          sx={{
            bgcolor: 'info.light',
            color: 'info.dark',
            fontWeight: 600,
            border: '1px solid',
            borderColor: 'info.main',
          }}
        />
      );
    case 'OUTSIDE':
      return (
        <Chip
          icon={<RadioButtonUncheckedIcon fontSize="small" />}
          label="OUTSIDE"
          size={size}
          sx={{
            bgcolor: 'grey.100',
            color: 'text.secondary',
            fontWeight: 600,
            border: '1px solid',
            borderColor: 'grey.300',
          }}
        />
      );
    default:
      return <Chip label={normalized} size={size} />;
  }
};
