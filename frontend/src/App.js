import React, { useState, useEffect } from 'react';
import {
    Box,
    Container,
    Paper,
    TextField,
    Button,
    Typography,
    CircularProgress,
    Alert,
    Chip,
    Divider,
    IconButton,
    Tooltip,
    AppBar,
    Toolbar
} from '@mui/material';
import {
    History as HistoryIcon,
    DarkMode,
    LightMode,
    FormatAlignLeft
} from '@mui/icons-material';
import Editor from '@monaco-editor/react';
import axios from 'axios';
import { format } from 'sql-formatter';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ResultsTable from './components/ResultsTable';
import SchemaExplorer from './components/SchemaExplorer';
import QueryHistory from './components/QueryHistory';
import DataVisualization from './components/DataVisualization';
import ExportButton from './components/ExportButton';
import PerformanceMetrics from './components/PerformanceMetrics';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App({ darkMode, setDarkMode }) {
    const [question, setQuestion] = useState('');
    const [sql, setSql] = useState('');
    const [results, setResults] = useState(null);
    const [explanation, setExplanation] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [tablesUsed, setTablesUsed] = useState([]);
    const [historyOpen, setHistoryOpen] = useState(false);
    const [performanceMetrics, setPerformanceMetrics] = useState(null);

    const handleNL2SQL = async () => {
        if (!question.trim()) return;

        setLoading(true);
        setError(null);

        try {
            const response = await axios.post(`${API_BASE_URL}/api/v1/query/nl2sql`, {
                question: question
            });

            setSql(response.data.sql);
            setExplanation(response.data.explanation);
            setTablesUsed(response.data.tables_used || []);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to convert question to SQL');
        } finally {
            setLoading(false);
        }
    };

    const handleExecute = async () => {
        if (!sql.trim()) return;

        setLoading(true);
        setError(null);

        try {
            const startTime = performance.now();
            const response = await axios.post(`${API_BASE_URL}/api/v1/query/execute`, {
                sql: sql
            });
            const endTime = performance.now();

            setResults(response.data.results);

            // Set performance metrics
            setPerformanceMetrics({
                executionTime: endTime - startTime,
                rowCount: response.data.results.length,
                tablesUsed: tablesUsed,
                ragEnabled: tablesUsed.length > 0
            });

            // Save to history
            saveToHistory(question, sql, response.data.results);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to execute query');
        } finally {
            setLoading(false);
        }
    };

    const handleExplain = async () => {
        if (!sql.trim()) return;

        setLoading(true);
        setError(null);

        try {
            const response = await axios.post(`${API_BASE_URL}/api/v1/query/explain`, {
                sql: sql
            });

            setExplanation(response.data.explanation);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to explain query');
        } finally {
            setLoading(false);
        }
    };

    const handleFormatSQL = () => {
        if (!sql.trim()) return;

        try {
            const formatted = format(sql, {
                language: 'sqlite',
                tabWidth: 2,
                keywordCase: 'upper'
            });
            setSql(formatted);
        } catch (err) {
            console.error('Failed to format SQL:', err);
        }
    };

    const saveToHistory = (question, sql, results) => {
        const history = JSON.parse(localStorage.getItem('queryHistory') || '[]');
        const newEntry = {
            id: Date.now(),
            question,
            sql,
            rowCount: results.length,
            timestamp: new Date().toISOString()
        };

        const updatedHistory = [newEntry, ...history].slice(0, 50); // Keep last 50
        localStorage.setItem('queryHistory', JSON.stringify(updatedHistory));
    };

    const handleSelectFromHistory = (query) => {
        setQuestion(query.question);
        setSql(query.sql);
    };

    return (
        <Box sx={{ minHeight: '100vh', pb: 4 }}>
            {/* App Bar */}
            <AppBar position="static" elevation={1}>
                <Toolbar>
                    <Typography variant="h6" sx={{ flexGrow: 1 }}>
                        🤖 SQL Copilot
                    </Typography>
                    <Tooltip title="Query History">
                        <IconButton color="inherit" onClick={() => setHistoryOpen(true)}>
                            <HistoryIcon />
                        </IconButton>
                    </Tooltip>
                    <Tooltip title={darkMode ? 'Light Mode' : 'Dark Mode'}>
                        <IconButton color="inherit" onClick={() => setDarkMode(!darkMode)}>
                            {darkMode ? <LightMode /> : <DarkMode />}
                        </IconButton>
                    </Tooltip>
                </Toolbar>
            </AppBar>

            <Container maxWidth="xl" sx={{ mt: 3 }}>
                <Box sx={{ display: 'flex', gap: 3 }}>
                    {/* Left Panel - Schema Explorer */}
                    <Box sx={{ width: '300px', flexShrink: 0 }}>
                        <SchemaExplorer />
                    </Box>

                    {/* Main Content */}
                    <Box sx={{ flexGrow: 1 }}>
                        {/* Natural Language Input */}
                        <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
                            <Typography variant="h6" gutterBottom>
                                Ask a Question
                            </Typography>
                            <TextField
                                fullWidth
                                multiline
                                rows={2}
                                placeholder="e.g., Show me top 10 customers by total spending"
                                value={question}
                                onChange={(e) => setQuestion(e.target.value)}
                                onKeyPress={(e) => {
                                    if (e.key === 'Enter' && e.ctrlKey) {
                                        handleNL2SQL();
                                    }
                                }}
                                sx={{ mb: 2 }}
                            />
                            <Button
                                variant="contained"
                                onClick={handleNL2SQL}
                                disabled={loading || !question.trim()}
                                startIcon={loading ? <CircularProgress size={20} /> : null}
                            >
                                Convert to SQL
                            </Button>
                        </Paper>

                        {/* SQL Editor */}
                        <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                <Typography variant="h6">
                                    SQL Query
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                                    {tablesUsed.length > 0 && (
                                        <Box>
                                            <Typography variant="caption" sx={{ mr: 1 }}>
                                                Tables:
                                            </Typography>
                                            {tablesUsed.map((table) => (
                                                <Chip key={table} label={table} size="small" sx={{ mr: 0.5 }} />
                                            ))}
                                        </Box>
                                    )}
                                    <Tooltip title="Format SQL">
                                        <IconButton size="small" onClick={handleFormatSQL}>
                                            <FormatAlignLeft />
                                        </IconButton>
                                    </Tooltip>
                                </Box>
                            </Box>

                            <Box sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 1, mb: 2 }}>
                                <Editor
                                    height="200px"
                                    defaultLanguage="sql"
                                    value={sql}
                                    onChange={(value) => setSql(value || '')}
                                    theme={darkMode ? 'vs-dark' : 'vs-light'}
                                    options={{
                                        minimap: { enabled: false },
                                        fontSize: 14,
                                        lineNumbers: 'on',
                                        scrollBeyondLastLine: false,
                                    }}
                                />
                            </Box>

                            <Box sx={{ display: 'flex', gap: 1 }}>
                                <Button
                                    variant="contained"
                                    color="success"
                                    onClick={handleExecute}
                                    disabled={loading || !sql.trim()}
                                >
                                    Execute
                                </Button>
                                <Button
                                    variant="outlined"
                                    onClick={handleExplain}
                                    disabled={loading || !sql.trim()}
                                >
                                    Explain
                                </Button>
                            </Box>
                        </Paper>

                        {/* Error Display */}
                        {error && (
                            <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
                                {error}
                            </Alert>
                        )}

                        {/* Performance Metrics */}
                        {performanceMetrics && (
                            <PerformanceMetrics metrics={performanceMetrics} />
                        )}

                        {/* Explanation */}
                        {explanation && (
                            <Paper elevation={2} sx={{ p: 3, mb: 3 }}>
                                <Typography variant="h6" gutterBottom>
                                    Explanation
                                </Typography>
                                <Box sx={{
                                    '& h1, & h2, & h3': {
                                        marginTop: 2,
                                        marginBottom: 1,
                                        color: 'primary.main'
                                    },
                                    '& p': {
                                        marginBottom: 1
                                    },
                                    '& ul, & ol': {
                                        paddingLeft: 3,
                                        marginBottom: 1
                                    },
                                    '& code': {
                                        backgroundColor: darkMode ? '#2d2d2d' : '#f5f5f5',
                                        padding: '2px 6px',
                                        borderRadius: 1,
                                        fontFamily: 'monospace',
                                        fontSize: '0.9em'
                                    },
                                    '& pre': {
                                        backgroundColor: darkMode ? '#2d2d2d' : '#f5f5f5',
                                        padding: 2,
                                        borderRadius: 1,
                                        overflow: 'auto'
                                    }
                                }}>
                                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                                        {explanation}
                                    </ReactMarkdown>
                                </Box>
                            </Paper>
                        )}

                        {/* Results */}
                        {results && (
                            <Paper elevation={2} sx={{ p: 3 }}>
                                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                                    <Typography variant="h6">
                                        Results ({results.length} rows)
                                    </Typography>
                                    <ExportButton data={results} filename="query_results" />
                                </Box>
                                <Divider sx={{ mb: 2 }} />

                                {/* Data Visualization */}
                                <DataVisualization data={results} />

                                {/* Results Table */}
                                <Box sx={{ mt: 2 }}>
                                    <ResultsTable data={results} />
                                </Box>
                            </Paper>
                        )}
                    </Box>
                </Box>
            </Container>

            {/* Query History Drawer */}
            <QueryHistory
                open={historyOpen}
                onClose={() => setHistoryOpen(false)}
                onSelectQuery={handleSelectFromHistory}
            />
        </Box>
    );
}

export default App;
