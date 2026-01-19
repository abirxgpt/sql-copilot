import React from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
    Paper,
    Typography
} from '@mui/material';

function ResultsTable({ data }) {
    if (!data || data.length === 0) {
        return (
            <Typography variant="body2" color="text.secondary">
                No results to display
            </Typography>
        );
    }

    const columns = Object.keys(data[0]);

    return (
        <TableContainer component={Paper} sx={{ maxHeight: 500 }}>
            <Table stickyHeader size="small">
                <TableHead>
                    <TableRow>
                        {columns.map((column) => (
                            <TableCell key={column} sx={{ fontWeight: 'bold', bgcolor: '#f5f5f5' }}>
                                {column}
                            </TableCell>
                        ))}
                    </TableRow>
                </TableHead>
                <TableBody>
                    {data.map((row, index) => (
                        <TableRow key={index} hover>
                            {columns.map((column) => (
                                <TableCell key={column}>
                                    {row[column] !== null && row[column] !== undefined
                                        ? String(row[column])
                                        : <Typography variant="body2" color="text.secondary">NULL</Typography>
                                    }
                                </TableCell>
                            ))}
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </TableContainer>
    );
}

export default ResultsTable;
