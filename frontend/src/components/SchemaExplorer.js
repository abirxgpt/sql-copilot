import React, { useState, useEffect } from 'react';
import {
    Paper,
    Typography,
    List,
    ListItem,
    ListItemButton,
    ListItemText,
    Collapse,
    Chip,
    Box,
    CircularProgress
} from '@mui/material';
import {
    ExpandLess,
    ExpandMore,
    TableChart,
    Key
} from '@mui/icons-material';
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function SchemaExplorer() {
    const [schema, setSchema] = useState({});
    const [loading, setLoading] = useState(true);
    const [expandedTables, setExpandedTables] = useState({});

    useEffect(() => {
        fetchSchema();
    }, []);

    const fetchSchema = async () => {
        try {
            const response = await axios.get(`${API_BASE_URL}/api/v1/schema`);
            setSchema(response.data);
        } catch (error) {
            console.error('Failed to fetch schema:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleToggleTable = (tableName) => {
        setExpandedTables((prev) => ({
            ...prev,
            [tableName]: !prev[tableName]
        }));
    };

    if (loading) {
        return (
            <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
                <CircularProgress size={30} />
                <Typography variant="body2" sx={{ mt: 2 }}>
                    Loading schema...
                </Typography>
            </Paper>
        );
    }

    return (
        <Paper elevation={2} sx={{ p: 2, maxHeight: '80vh', overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
                Database Schema
            </Typography>

            <List dense>
                {Object.entries(schema).map(([tableName, tableInfo]) => (
                    <Box key={tableName}>
                        <ListItemButton onClick={() => handleToggleTable(tableName)}>
                            <TableChart sx={{ mr: 1, fontSize: 20, color: 'primary.main' }} />
                            <ListItemText
                                primary={tableName}
                                secondary={`${tableInfo.row_count} rows`}
                            />
                            {expandedTables[tableName] ? <ExpandLess /> : <ExpandMore />}
                        </ListItemButton>

                        <Collapse in={expandedTables[tableName]} timeout="auto" unmountOnExit>
                            <List component="div" disablePadding dense>
                                {tableInfo.columns.map((column) => (
                                    <ListItem key={column.name} sx={{ pl: 4 }}>
                                        <ListItemText
                                            primary={
                                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                                                    {column.primary_key && (
                                                        <Key sx={{ fontSize: 14, color: 'warning.main' }} />
                                                    )}
                                                    <Typography variant="body2">
                                                        {column.name}
                                                    </Typography>
                                                    <Chip
                                                        label={column.type}
                                                        size="small"
                                                        sx={{ height: 18, fontSize: 10 }}
                                                    />
                                                </Box>
                                            }
                                            secondary={
                                                column.nullable ? 'NULL' : 'NOT NULL'
                                            }
                                        />
                                    </ListItem>
                                ))}

                                {tableInfo.foreign_keys && tableInfo.foreign_keys.length > 0 && (
                                    <ListItem sx={{ pl: 4 }}>
                                        <ListItemText
                                            secondary={
                                                <Typography variant="caption" color="text.secondary">
                                                    Foreign Keys: {tableInfo.foreign_keys.map(fk =>
                                                        `${fk.column} → ${fk.referenced_table}.${fk.referenced_column}`
                                                    ).join(', ')}
                                                </Typography>
                                            }
                                        />
                                    </ListItem>
                                )}
                            </List>
                        </Collapse>
                    </Box>
                ))}
            </List>
        </Paper>
    );
}

export default SchemaExplorer;
