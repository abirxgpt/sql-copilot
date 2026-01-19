import React, { useState } from 'react';
import {
    Drawer,
    List,
    ListItem,
    ListItemButton,
    ListItemText,
    ListItemIcon,
    IconButton,
    Typography,
    Box,
    TextField,
    Chip,
    Divider,
    Tooltip
} from '@mui/material';
import {
    History,
    Star,
    StarBorder,
    Delete,
    Search,
    Close
} from '@mui/icons-material';

function QueryHistory({ open, onClose, onSelectQuery }) {
    const [searchTerm, setSearchTerm] = useState('');
    const [history, setHistory] = useState(() => {
        const saved = localStorage.getItem('queryHistory');
        return saved ? JSON.parse(saved) : [];
    });
    const [favorites, setFavorites] = useState(() => {
        const saved = localStorage.getItem('queryFavorites');
        return saved ? JSON.parse(saved) : [];
    });

    const toggleFavorite = (queryId) => {
        const newFavorites = favorites.includes(queryId)
            ? favorites.filter(id => id !== queryId)
            : [...favorites, queryId];

        setFavorites(newFavorites);
        localStorage.setItem('queryFavorites', JSON.stringify(newFavorites));
    };

    const deleteQuery = (queryId) => {
        const newHistory = history.filter(q => q.id !== queryId);
        setHistory(newHistory);
        localStorage.setItem('queryHistory', JSON.stringify(newHistory));

        // Also remove from favorites if present
        if (favorites.includes(queryId)) {
            const newFavorites = favorites.filter(id => id !== queryId);
            setFavorites(newFavorites);
            localStorage.setItem('queryFavorites', JSON.stringify(newFavorites));
        }
    };

    const filteredHistory = history.filter(q =>
        q.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
        q.sql.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const favoriteQueries = filteredHistory.filter(q => favorites.includes(q.id));
    const recentQueries = filteredHistory.filter(q => !favorites.includes(q.id));

    return (
        <Drawer anchor="right" open={open} onClose={onClose}>
            <Box sx={{ width: 400, p: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                    <Typography variant="h6">
                        <History sx={{ mr: 1, verticalAlign: 'middle' }} />
                        Query History
                    </Typography>
                    <IconButton onClick={onClose}>
                        <Close />
                    </IconButton>
                </Box>

                <TextField
                    fullWidth
                    size="small"
                    placeholder="Search queries..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    InputProps={{
                        startAdornment: <Search sx={{ mr: 1, color: 'text.secondary' }} />
                    }}
                    sx={{ mb: 2 }}
                />

                {favoriteQueries.length > 0 && (
                    <>
                        <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                            Favorites
                        </Typography>
                        <List dense>
                            {favoriteQueries.map((query) => (
                                <ListItem
                                    key={query.id}
                                    disablePadding
                                    secondaryAction={
                                        <Box>
                                            <IconButton
                                                edge="end"
                                                size="small"
                                                onClick={() => toggleFavorite(query.id)}
                                            >
                                                <Star color="warning" />
                                            </IconButton>
                                            <IconButton
                                                edge="end"
                                                size="small"
                                                onClick={() => deleteQuery(query.id)}
                                            >
                                                <Delete />
                                            </IconButton>
                                        </Box>
                                    }
                                >
                                    <ListItemButton onClick={() => {
                                        onSelectQuery(query);
                                        onClose();
                                    }}>
                                        <ListItemText
                                            primary={query.question}
                                            secondary={
                                                <>
                                                    <Typography variant="caption" component="div" noWrap>
                                                        {query.sql}
                                                    </Typography>
                                                    <Chip
                                                        label={`${query.rowCount} rows`}
                                                        size="small"
                                                        sx={{ mt: 0.5, height: 18 }}
                                                    />
                                                </>
                                            }
                                        />
                                    </ListItemButton>
                                </ListItem>
                            ))}
                        </List>
                        <Divider sx={{ my: 2 }} />
                    </>
                )}

                <Typography variant="subtitle2" color="text.secondary" sx={{ mb: 1 }}>
                    Recent Queries
                </Typography>
                <List dense>
                    {recentQueries.length === 0 ? (
                        <Typography variant="body2" color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
                            No queries yet
                        </Typography>
                    ) : (
                        recentQueries.map((query) => (
                            <ListItem
                                key={query.id}
                                disablePadding
                                secondaryAction={
                                    <Box>
                                        <IconButton
                                            edge="end"
                                            size="small"
                                            onClick={() => toggleFavorite(query.id)}
                                        >
                                            <StarBorder />
                                        </IconButton>
                                        <IconButton
                                            edge="end"
                                            size="small"
                                            onClick={() => deleteQuery(query.id)}
                                        >
                                            <Delete />
                                        </IconButton>
                                    </Box>
                                }
                            >
                                <ListItemButton onClick={() => {
                                    onSelectQuery(query);
                                    onClose();
                                }}>
                                    <ListItemText
                                        primary={query.question}
                                        secondary={
                                            <>
                                                <Typography variant="caption" component="div" noWrap>
                                                    {query.sql}
                                                </Typography>
                                                <Box sx={{ display: 'flex', gap: 0.5, mt: 0.5 }}>
                                                    <Chip
                                                        label={`${query.rowCount} rows`}
                                                        size="small"
                                                        sx={{ height: 18 }}
                                                    />
                                                    <Chip
                                                        label={new Date(query.timestamp).toLocaleDateString()}
                                                        size="small"
                                                        sx={{ height: 18 }}
                                                    />
                                                </Box>
                                            </>
                                        }
                                    />
                                </ListItemButton>
                            </ListItem>
                        ))
                    )}
                </List>
            </Box>
        </Drawer>
    );
}

export default QueryHistory;
