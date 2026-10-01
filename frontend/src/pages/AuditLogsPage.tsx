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
  Chip,
  Pagination,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Paper,
} from '@mui/material';
import RefreshIcon from '@mui/icons-material/Refresh';
import CodeIcon from '@mui/icons-material/Code';
import { auditService } from '../services/auditService';
import { AuditLog } from '../types';
import { LoadingSpinner } from '../components/LoadingSpinner';

export const AuditLogsPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  // Payload inspect modal
  const [inspectModalOpen, setInspectModalOpen] = useState(false);
  const [inspectedLog, setInspectedLog] = useState<AuditLog | null>(null);

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const res = await auditService.getLogs({
        page,
        page_size: 20,
      });
      setLogs(res.data);
      setTotal(res.pagination.total);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page]);

  const handleInspect = (log: AuditLog) => {
    setInspectedLog(log);
    setInspectModalOpen(true);
  };

  return (
    <Box sx={{ pb: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 700 }}>
            System Audit Trail
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Immutable administrative and event telemetry records
          </Typography>
        </Box>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchLogs}
          size="small"
        >
          Refresh Logs
        </Button>
      </Box>

      <Card elevation={0} sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}>
        {loading ? (
          <LoadingSpinner message="Loading audit records..." />
        ) : (
          <TableContainer>
            <Table size="small">
              <TableHead sx={{ bgcolor: 'grey.50' }}>
                <TableRow>
                  <TableCell sx={{ fontWeight: 600 }}>Timestamp</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Action</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Entity Type</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Entity ID</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Actor</TableCell>
                  <TableCell sx={{ fontWeight: 600 }}>Client IP</TableCell>
                  <TableCell align="right" sx={{ fontWeight: 600 }}>Payload</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {logs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} align="center" sx={{ py: 4, color: 'text.secondary' }}>
                      No audit log records recorded.
                    </TableCell>
                  </TableRow>
                ) : (
                  logs.map((log) => (
                    <TableRow key={log.id} hover>
                      <TableCell sx={{ fontSize: '0.8125rem' }}>
                        {new Date(log.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={log.action}
                          size="small"
                          sx={{ fontWeight: 600, fontSize: '0.7rem' }}
                          color={
                            log.action.includes('CREATE') || log.action.includes('REGISTER')
                              ? 'success'
                              : log.action.includes('DELETE')
                              ? 'error'
                              : log.action.includes('FAIL')
                              ? 'warning'
                              : 'primary'
                          }
                          variant="outlined"
                        />
                      </TableCell>
                      <TableCell sx={{ fontWeight: 500 }}>{log.entity_type}</TableCell>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.8125rem' }}>
                        {log.entity_id ? `#${log.entity_id}` : '-'}
                      </TableCell>
                      <TableCell>{log.user_name || (log.user_id ? `User #${log.user_id}` : 'System')}</TableCell>
                      <TableCell sx={{ fontFamily: 'monospace', fontSize: '0.75rem', color: 'text.secondary' }}>
                        {log.ip_address || '-'}
                      </TableCell>
                      <TableCell align="right">
                        {(log.old_value || log.new_value) && (
                          <Button
                            size="small"
                            variant="text"
                            startIcon={<CodeIcon fontSize="small" />}
                            onClick={() => handleInspect(log)}
                          >
                            Diff
                          </Button>
                        )}
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

      {/* Inspect Diff Modal */}
      <Dialog open={inspectModalOpen} onClose={() => setInspectModalOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ fontWeight: 600 }}>
          Audit Record Payload #{inspectedLog?.id}
        </DialogTitle>
        <DialogContent dividers>
          {inspectedLog?.old_value && (
            <Box sx={{ mb: 2 }}>
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                PREVIOUS STATE:
              </Typography>
              <Paper variant="outlined" sx={{ p: 1.5, bgcolor: '#fbfbfb', overflow: 'auto' }}>
                <pre style={{ margin: 0, fontSize: '0.75rem' }}>
                  {JSON.stringify(inspectedLog.old_value, null, 2)}
                </pre>
              </Paper>
            </Box>
          )}

          {inspectedLog?.new_value && (
            <Box>
              <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 600 }}>
                NEW STATE / PAYLOAD:
              </Typography>
              <Paper variant="outlined" sx={{ p: 1.5, bgcolor: '#fbfbfb', overflow: 'auto' }}>
                <pre style={{ margin: 0, fontSize: '0.75rem' }}>
                  {JSON.stringify(inspectedLog.new_value, null, 2)}
                </pre>
              </Paper>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setInspectModalOpen(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
