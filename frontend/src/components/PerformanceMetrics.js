import React from 'react';
import {
    Box,
    Paper,
    Typography,
    Chip,
    Grid
} from '@mui/material';
import {
    Speed,
    Storage,
    Timer,
    TrendingUp
} from '@mui/icons-material';

function PerformanceMetrics({ metrics }) {
    if (!metrics) return null;

    const formatTime = (ms) => {
        if (ms < 1000) return `${ms.toFixed(0)}ms`;
        return `${(ms / 1000).toFixed(2)}s`;
    };

    return (
        <Paper elevation={1} sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle2" gutterBottom>
                Performance Metrics
            </Typography>
            <Grid container spacing={2}>
                <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Timer color="primary" />
                        <Box>
                            <Typography variant="caption" color="text.secondary">
                                Execution Time
                            </Typography>
                            <Typography variant="body2" fontWeight="bold">
                                {formatTime(metrics.executionTime || 0)}
                            </Typography>
                        </Box>
                    </Box>
                </Grid>

                <Grid item xs={12} sm={6} md={3}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Storage color="success" />
                        <Box>
                            <Typography variant="caption" color="text.secondary">
                                Rows Returned
                            </Typography>
                            <Typography variant="body2" fontWeight="bold">
                                {metrics.rowCount || 0}
                            </Typography>
                        </Box>
                    </Box>
                </Grid>

                {metrics.tablesUsed && metrics.tablesUsed.length > 0 && (
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <TrendingUp color="info" />
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    Tables Scanned
                                </Typography>
                                <Typography variant="body2" fontWeight="bold">
                                    {metrics.tablesUsed.length}
                                </Typography>
                            </Box>
                        </Box>
                    </Grid>
                )}

                {metrics.ragEnabled && (
                    <Grid item xs={12} sm={6} md={3}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Speed color="warning" />
                            <Box>
                                <Typography variant="caption" color="text.secondary">
                                    RAG Status
                                </Typography>
                                <Chip
                                    label="Enabled"
                                    size="small"
                                    color="success"
                                    sx={{ height: 20 }}
                                />
                            </Box>
                        </Box>
                    </Grid>
                )}
            </Grid>
        </Paper>
    );
}

export default PerformanceMetrics;
