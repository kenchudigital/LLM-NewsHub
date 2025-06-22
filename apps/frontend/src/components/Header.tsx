import React from 'react';
import { AppBar, Toolbar, Typography, Box } from '@mui/material';
import { styled } from '@mui/material/styles';
import { Link as RouterLink } from 'react-router-dom';

const StyledAppBar = styled(AppBar)(({ theme }) => ({
    background: 'linear-gradient(90deg, #ffffff 0%, #f8f9fa 100%)',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
    borderBottom: '2px solid',
    borderImage: 'linear-gradient(90deg, #00eaff 0%, #ff6a00 100%) 1',
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1300,
    width: '100%',
    transform: 'none',
}));

const LogoLink = styled(RouterLink)(({ theme }) => ({
    textDecoration: 'none',
    transition: 'transform 0.3s ease',
    '&:hover': {
        textDecoration: 'none',
        transform: 'scale(1.05)',
    },
}));

const LogoText = styled(Typography)(({ theme }) => ({
    fontWeight: 700,
    fontSize: '1.8rem',
    background: 'linear-gradient(90deg, #00eaff, #ff6a00)',
    backgroundClip: 'text',
    WebkitBackgroundClip: 'text',
    color: 'transparent',
    animation: 'logoShimmer 3s infinite linear',
    '@keyframes logoShimmer': {
        '0%': {
            backgroundPosition: '-200% center',
        },
        '100%': {
            backgroundPosition: '200% center',
        },
    },
}));

const Header: React.FC = () => {
    return (
        <StyledAppBar position="fixed" sx={{ position: 'fixed !important' }}>
            <Toolbar sx={{ minHeight: '70px' }}>
                <Box sx={{ flexGrow: 1, display: 'flex', alignItems: 'center' }}>
                    <LogoLink to="/">
                        <LogoText variant="h6">
                            AI NewsSense
                        </LogoText>
                    </LogoLink>
                </Box>
            </Toolbar>
        </StyledAppBar>
    );
};

export default Header; 