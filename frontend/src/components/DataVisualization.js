import React, { useState } from 'react';
import {
    Box,
    ToggleButtonGroup,
    ToggleButton,
    Typography,
    Select,
    MenuItem,
    FormControl,
    InputLabel
} from '@mui/material';
import {
    TableChart,
    BarChart as BarChartIcon,
    ShowChart,
    PieChart as PieChartIcon
} from '@mui/icons-material';
import {
    BarChart,
    Bar,
    LineChart,
    Line,
    PieChart,
    Pie,
    Cell,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer
} from 'recharts';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

function DataVisualization({ data }) {
    const [viewMode, setViewMode] = useState('table');
    const [chartType, setChartType] = useState('bar');
    const [xAxis, setXAxis] = useState('');
    const [yAxis, setYAxis] = useState('');

    if (!data || data.length === 0) {
        return null;
    }

    const columns = Object.keys(data[0]);
    const numericColumns = columns.filter(col =>
        data.some(row => typeof row[col] === 'number')
    );
    const categoricalColumns = columns.filter(col =>
        data.every(row => typeof row[col] === 'string' || row[col] === null)
    );

    // Auto-select axes if not set
    if (!xAxis && categoricalColumns.length > 0) {
        setXAxis(categoricalColumns[0]);
    }
    if (!yAxis && numericColumns.length > 0) {
        setYAxis(numericColumns[0]);
    }

    const prepareChartData = () => {
        if (!xAxis || !yAxis) return [];

        return data.map(row => ({
            name: String(row[xAxis] || 'N/A'),
            value: Number(row[yAxis]) || 0
        }));
    };

    const chartData = prepareChartData();

    const renderChart = () => {
        if (chartData.length === 0) {
            return (
                <Typography color="text.secondary" sx={{ p: 2, textAlign: 'center' }}>
                    Select X and Y axes to visualize data
                </Typography>
            );
        }

        switch (chartType) {
            case 'bar':
                return (
                    <ResponsiveContainer width="100%" height={400}>
                        <BarChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="value" fill="#1976d2" name={yAxis} />
                        </BarChart>
                    </ResponsiveContainer>
                );

            case 'line':
                return (
                    <ResponsiveContainer width="100%" height={400}>
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="value" stroke="#1976d2" name={yAxis} />
                        </LineChart>
                    </ResponsiveContainer>
                );

            case 'pie':
                return (
                    <ResponsiveContainer width="100%" height={400}>
                        <PieChart>
                            <Pie
                                data={chartData}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                                outerRadius={120}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {chartData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                        </PieChart>
                    </ResponsiveContainer>
                );

            default:
                return null;
        }
    };

    return (
        <Box>
            <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap', alignItems: 'center' }}>
                <ToggleButtonGroup
                    value={viewMode}
                    exclusive
                    onChange={(e, newMode) => newMode && setViewMode(newMode)}
                    size="small"
                >
                    <ToggleButton value="table">
                        <TableChart sx={{ mr: 0.5 }} />
                        Table
                    </ToggleButton>
                    <ToggleButton value="chart">
                        <BarChartIcon sx={{ mr: 0.5 }} />
                        Chart
                    </ToggleButton>
                </ToggleButtonGroup>

                {viewMode === 'chart' && (
                    <>
                        <ToggleButtonGroup
                            value={chartType}
                            exclusive
                            onChange={(e, newType) => newType && setChartType(newType)}
                            size="small"
                        >
                            <ToggleButton value="bar">
                                <BarChartIcon />
                            </ToggleButton>
                            <ToggleButton value="line">
                                <ShowChart />
                            </ToggleButton>
                            <ToggleButton value="pie">
                                <PieChartIcon />
                            </ToggleButton>
                        </ToggleButtonGroup>

                        <FormControl size="small" sx={{ minWidth: 120 }}>
                            <InputLabel>X Axis</InputLabel>
                            <Select
                                value={xAxis}
                                label="X Axis"
                                onChange={(e) => setXAxis(e.target.value)}
                            >
                                {columns.map(col => (
                                    <MenuItem key={col} value={col}>{col}</MenuItem>
                                ))}
                            </Select>
                        </FormControl>

                        <FormControl size="small" sx={{ minWidth: 120 }}>
                            <InputLabel>Y Axis</InputLabel>
                            <Select
                                value={yAxis}
                                label="Y Axis"
                                onChange={(e) => setYAxis(e.target.value)}
                            >
                                {numericColumns.map(col => (
                                    <MenuItem key={col} value={col}>{col}</MenuItem>
                                ))}
                            </Select>
                        </FormControl>
                    </>
                )}
            </Box>

            {viewMode === 'chart' ? renderChart() : null}
        </Box>
    );
}

export default DataVisualization;
