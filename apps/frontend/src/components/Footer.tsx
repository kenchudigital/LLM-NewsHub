import React from 'react';
import { Box, Typography } from '@mui/material';

const Footer: React.FC = () => {
    return (
        <Box
            component="footer"
            sx={{
                py: 2,
                px: 2,
                mt: 'auto',
                backgroundColor: (theme) => theme.palette.grey[900],
                color: 'white',
                textAlign: 'center',
                boxShadow: '0 -4px 6px rgba(0, 0, 0, 0.1)',
            }}
        >
            <Typography
                variant="body2"
                sx={{
                    fontWeight: 500,
                    letterSpacing: '0.5px',
                    background: 'linear-gradient(90deg, #00eaff, #ff6a00)',
                    backgroundClip: 'text',
                    WebkitBackgroundClip: 'text',
                    color: 'transparent',
                    animation: 'shimmer 2s infinite linear',
                    '@keyframes shimmer': {
                        '0%': {
                            backgroundPosition: '-200% center',
                        },
                        '100%': {
                            backgroundPosition: '200% center',
                        },
                    },
                }}
            >
                made by HKU msp24053
            </Typography>
        </Box>
    );
};

export default Footer; 