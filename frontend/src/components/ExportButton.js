import React from 'react';
import {
    Button,
    Menu,
    MenuItem,
    ListItemIcon,
    ListItemText
} from '@mui/material';
import {
    Download,
    TableChart,
    Code,
    ContentCopy
} from '@mui/icons-material';
import { saveAs } from 'file-saver';

function ExportButton({ data, filename = 'query_results' }) {
    const [anchorEl, setAnchorEl] = React.useState(null);
    const open = Boolean(anchorEl);

    const handleClick = (event) => {
        setAnchorEl(event.currentTarget);
    };

    const handleClose = () => {
        setAnchorEl(null);
    };

    const exportToCSV = () => {
        if (!data || data.length === 0) return;

        const headers = Object.keys(data[0]);
        const csvContent = [
            headers.join(','),
            ...data.map(row =>
                headers.map(header => {
                    const value = row[header];
                    // Escape commas and quotes
                    if (value === null || value === undefined) return '';
                    const stringValue = String(value);
                    if (stringValue.includes(',') || stringValue.includes('"')) {
                        return `"${stringValue.replace(/"/g, '""')}"`;
                    }
                    return stringValue;
                }).join(',')
            )
        ].join('\n');

        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8' });
        saveAs(blob, `${filename}.csv`);
        handleClose();
    };

    const exportToJSON = () => {
        if (!data || data.length === 0) return;

        const jsonContent = JSON.stringify(data, null, 2);
        const blob = new Blob([jsonContent], { type: 'application/json' });
        saveAs(blob, `${filename}.json`);
        handleClose();
    };

    const copyToClipboard = () => {
        if (!data || data.length === 0) return;

        const headers = Object.keys(data[0]);
        const textContent = [
            headers.join('\t'),
            ...data.map(row => headers.map(h => row[h] ?? '').join('\t'))
        ].join('\n');

        navigator.clipboard.writeText(textContent).then(() => {
            console.log('Copied to clipboard');
        });
        handleClose();
    };

    if (!data || data.length === 0) {
        return null;
    }

    return (
        <>
            <Button
                variant="outlined"
                startIcon={<Download />}
                onClick={handleClick}
                size="small"
            >
                Export
            </Button>
            <Menu
                anchorEl={anchorEl}
                open={open}
                onClose={handleClose}
            >
                <MenuItem onClick={exportToCSV}>
                    <ListItemIcon>
                        <TableChart fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>Export as CSV</ListItemText>
                </MenuItem>
                <MenuItem onClick={exportToJSON}>
                    <ListItemIcon>
                        <Code fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>Export as JSON</ListItemText>
                </MenuItem>
                <MenuItem onClick={copyToClipboard}>
                    <ListItemIcon>
                        <ContentCopy fontSize="small" />
                    </ListItemIcon>
                    <ListItemText>Copy to Clipboard</ListItemText>
                </MenuItem>
            </Menu>
        </>
    );
}

export default ExportButton;
