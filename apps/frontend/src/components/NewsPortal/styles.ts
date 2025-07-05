import { styled } from '@mui/material/styles';
import { Box, Container, Paper, Card, IconButton, Button } from '@mui/material';

// Main portal container with animated background
export const PortalContainer = styled(Box)(({ theme }) => ({
    minHeight: '100vh',
    background: `
        radial-gradient(ellipse at top, #0a0a23 0%, #000000 50%),
        radial-gradient(ellipse at bottom, #1a0033 0%, #000000 50%),
        linear-gradient(135deg, 
            #000000 0%, 
            #0a0a0a 10%, 
            #1a1a2e 20%, 
            #16213e 35%, 
            #0f3460 50%, 
            #16213e 65%, 
            #1a1a2e 80%, 
            #0a0a0a 90%, 
            #000000 100%
        )
    `,
    position: 'relative',
    color: 'white',
    overflow: 'hidden',

    '&::before': {
        content: '""',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: `
            radial-gradient(circle at 20% 20%, rgba(0, 234, 255, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255, 106, 0, 0.06) 0%, transparent 50%)
        `,
        pointerEvents: 'none',
        zIndex: 0,
        animation: 'backgroundPulse 8s ease-in-out infinite',
    },

    '@keyframes backgroundPulse': {
        '0%, 100%': { opacity: 0.6 },
        '50%': { opacity: 1 },
    },

    // Responsive breakpoints
    [theme.breakpoints.down('lg')]: {
        padding: theme.spacing(0, 2),
    },
    [theme.breakpoints.down('md')]: {
        padding: theme.spacing(0, 1),
    },
}));

// Header styles
export const Header = styled(Box)(({ theme }) => ({
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1100,
    background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.98) 0%, rgba(26, 26, 46, 0.95) 30%, rgba(22, 33, 62, 0.92) 100%)',
    backdropFilter: 'blur(20px) saturate(180%)',
    borderBottom: '2px solid transparent',
    borderImage: 'linear-gradient(90deg, #00eaff, #ff6a00, #8a2be2) 1',
    boxShadow: '0 4px 32px rgba(0, 234, 255, 0.3)',
    padding: theme.spacing(1, 0),

    [theme.breakpoints.down('md')]: {
        padding: theme.spacing(0.5, 0),
    },
}));

export const HeaderContent = styled(Container)(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: theme.spacing(2),

    [theme.breakpoints.down('md')]: {
        flexDirection: 'column',
        gap: theme.spacing(1),
    },
}));

// Logo styles
export const Logo = styled(Box)(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(1),

    '& .logo-text': {
        fontSize: '1.8rem',
        fontWeight: 700,
        background: 'linear-gradient(45deg, #00eaff, #ff6a00, #8a2be2, #32cd32)',
        backgroundSize: '300% 300%',
        backgroundClip: 'text',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        animation: 'logoGradient 4s ease-in-out infinite',
        letterSpacing: '2px',
        fontFamily: '"Orbitron", "Roboto", sans-serif',

        [theme.breakpoints.down('md')]: {
            fontSize: '1.4rem',
        },
        [theme.breakpoints.down('sm')]: {
            fontSize: '1.2rem',
        },
    },

    '@keyframes logoGradient': {
        '0%, 100%': { backgroundPosition: '0% 50%' },
        '50%': { backgroundPosition: '100% 50%' },
    },
}));

// Search bar styles
export const SearchBar = styled(Box)(({ theme }) => ({
    flex: 1,
    maxWidth: '600px',

    [theme.breakpoints.down('md')]: {
        maxWidth: '100%',
        width: '100%',
    },
}));

// Categories section
export const CategoriesSection = styled(Box)(({ theme }) => ({
    marginBottom: theme.spacing(2),
    background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.9) 0%, rgba(26, 26, 46, 0.85) 100%)',
    borderRadius: '12px',
    padding: theme.spacing(1.5),
    boxShadow: '0 8px 32px rgba(0, 234, 255, 0.1)',
    border: '1px solid rgba(0, 234, 255, 0.2)',
    backdropFilter: 'blur(10px)',
}));

// Date filter styles
export const DateFilter = styled(Box)(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(2),
    marginBottom: theme.spacing(3),
    padding: theme.spacing(2),
    background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.9) 0%, rgba(26, 26, 46, 0.85) 100%)',
    borderRadius: '12px',
    border: '1px solid rgba(0, 234, 255, 0.2)',

    [theme.breakpoints.down('md')]: {
        flexDirection: 'column',
        alignItems: 'flex-start',
        gap: theme.spacing(1),
    },
}));

export const DateButton = styled(Button)<{ selected: boolean }>(({ theme, selected }) => ({
    borderRadius: '8px',
    padding: theme.spacing(0.5, 1.5),
    fontSize: '0.85rem',
    fontWeight: 600,
    textTransform: 'none',
    minWidth: 'auto',
    backgroundColor: selected ? 'rgba(0, 234, 255, 0.2)' : 'rgba(255, 255, 255, 0.05)',
    color: selected ? '#00eaff' : 'rgba(255, 255, 255, 0.7)',
    border: `1px solid ${selected ? '#00eaff' : 'rgba(255, 255, 255, 0.1)'}`,
    transition: 'all 0.3s ease',

    '&:hover': {
        backgroundColor: 'rgba(0, 234, 255, 0.1)',
        color: '#00eaff',
        borderColor: '#00eaff',
        transform: 'translateY(-1px)',
    },

    [theme.breakpoints.down('sm')]: {
        fontSize: '0.75rem',
        padding: theme.spacing(0.4, 1),
    },
}));

// Carousel styles
export const CarouselContainer = styled(Box)(({ theme }) => ({
    position: 'relative',
    marginBottom: theme.spacing(2),
    background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.9) 0%, rgba(26, 26, 46, 0.85) 100%)',
    borderRadius: '12px',
    padding: theme.spacing(1.5),
    boxShadow: '0 8px 32px rgba(0, 234, 255, 0.1)',
    border: '1px solid rgba(0, 234, 255, 0.2)',
    backdropFilter: 'blur(10px)',
}));

export const CarouselGrid = styled(Box)(({ theme }) => ({
    display: 'flex',
    gap: theme.spacing(1),
    overflowX: 'auto',
    scrollBehavior: 'smooth',
    paddingBottom: theme.spacing(1),

    '&::-webkit-scrollbar': {
        height: '8px',
    },
    '&::-webkit-scrollbar-track': {
        background: '#f1f1f1',
        borderRadius: '4px',
    },
    '&::-webkit-scrollbar-thumb': {
        background: '#c1c1c1',
        borderRadius: '4px',
    },
}));

// News card styles
export const NewsCard = styled(Card)<{ selected?: boolean }>(({ theme, selected }) => ({
    minWidth: '300px',
    maxWidth: '300px',
    cursor: 'pointer',
    background: selected
        ? 'linear-gradient(135deg, rgba(0, 234, 255, 0.2) 0%, rgba(26, 26, 46, 0.9) 50%)'
        : 'linear-gradient(135deg, rgba(13, 13, 13, 0.9) 0%, rgba(26, 26, 46, 0.85) 100%)',
    border: selected ? '2px solid #00eaff' : '1px solid rgba(0, 234, 255, 0.2)',
    borderRadius: '16px',
    backdropFilter: 'blur(20px)',
    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
    boxShadow: selected
        ? '0 12px 40px rgba(0, 234, 255, 0.4)'
        : '0 8px 32px rgba(0, 234, 255, 0.1)',

    '&:hover': {
        transform: 'translateY(-8px) scale(1.03)',
        boxShadow: '0 20px 60px rgba(0, 234, 255, 0.3)',
        border: '2px solid rgba(255, 106, 0, 0.6)',
    },

    [theme.breakpoints.down('md')]: {
        minWidth: '280px',
        maxWidth: '280px',
    },
    [theme.breakpoints.down('sm')]: {
        minWidth: '250px',
        maxWidth: '250px',
    },
}));

// Article detail styles
export const ArticleDetailContainer = styled(Box)(({ theme }) => ({
    maxWidth: '1000px',
    margin: '0 auto',
    padding: theme.spacing(3),
    background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.9) 0%, rgba(26, 26, 46, 0.85) 100%)',
    borderRadius: '12px',
    border: '1px solid rgba(0, 234, 255, 0.2)',
    backdropFilter: 'blur(10px)',

    [theme.breakpoints.down('md')]: {
        padding: theme.spacing(2),
    },
    [theme.breakpoints.down('sm')]: {
        padding: theme.spacing(1.5),
    },
}));

// Audio player styles
export const AudioPlayerContainer = styled(Box)(({ theme }) => ({
    marginBottom: theme.spacing(4),
    padding: theme.spacing(2),
    background: 'rgba(0, 234, 255, 0.05)',
    borderRadius: '8px',
    border: '1px solid rgba(0, 234, 255, 0.2)',
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(2),

    [theme.breakpoints.down('md')]: {
        flexDirection: 'column',
        gap: theme.spacing(1),
    },
}));

// Chat styles
export const ChatContainer = styled(Box)(({ theme }) => ({
    position: 'fixed',
    bottom: theme.spacing(2),
    right: theme.spacing(2),
    zIndex: 1000,
    transition: 'all 0.3s ease',

    '&.minimized': {
        width: '60px',
        height: '60px',
    },

    [theme.breakpoints.down('md')]: {
        bottom: theme.spacing(1),
        right: theme.spacing(1),
    },
}));

export const ChatIcon = styled(IconButton)(({ theme }) => ({
    width: '60px',
    height: '60px',
    background: 'linear-gradient(135deg, #00eaff 0%, #ff6a00 100%)',
    color: 'white',
    boxShadow: '0 4px 20px rgba(0, 234, 255, 0.4)',

    '&:hover': {
        background: 'linear-gradient(135deg, #ff6a00 0%, #00eaff 100%)',
        transform: 'scale(1.1)',
    },
}));

// Footer styles
export const FooterSection = styled(Box)(({ theme }) => ({
    marginTop: theme.spacing(6),
    padding: theme.spacing(4, 0, 2),
    background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.98) 0%, rgba(26, 26, 46, 0.95) 30%)',
    borderTop: '2px solid transparent',
    borderImage: 'linear-gradient(90deg, #00eaff, #ff6a00, #8a2be2) 1',
    backdropFilter: 'blur(20px)',

    [theme.breakpoints.down('md')]: {
        padding: theme.spacing(2, 0, 1),
    },
})); 