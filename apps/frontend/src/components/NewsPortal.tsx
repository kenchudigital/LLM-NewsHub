import config from '../config';
import React, { useState, useEffect, useRef } from 'react';
import {
    Box,
    Container,
    Typography,
    Paper,
    Chip,
    IconButton,
    Button,
    Divider,
    Link,
    Card,
    CardContent,
    CardMedia,
    LinearProgress,
    Tooltip,
    Grid,
    Tabs,
    Tab,
    TextField,
    InputAdornment,
    CircularProgress,
    Fab,
    Modal,
    Backdrop,
    FormControl,
    InputLabel,
    Select,
    MenuItem,
    FormControlLabel,
    Switch,
} from '@mui/material';
import {
    PlayArrow,
    Pause,
    VolumeUp,
    Share,
    BookmarkBorder,
    Bookmark,
    ThumbUp,
    ThumbDown,
    Schedule,
    LocationOn,
    TrendingUp,
    Warning,
    Search as SearchIcon,
    ChevronLeft,
    ChevronRight,
    ExpandMore,
    ExpandLess,
    Close,
    Chat,
    SmartToy,
    Remove,
    AutoAwesome,
    AllInclusive,
    CalendarToday as CalendarTodayIcon,
    Schedule as ScheduleIcon,
    VideoLibrary,
    Fullscreen,
    FullscreenExit,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import axios from 'axios';
import ChatBot from './ChatBot';
// import { useNavigate } from 'react-router-dom'; // Not needed anymore

// Styled components with animations
const PortalContainer = styled(Box)(({ theme }) => ({
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
    margin: 0,
    padding: 0,
    position: 'relative',
    color: 'white',
    overflow: 'hidden',

    // Animated background layers
    '&::before': {
        content: '""',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: `
            radial-gradient(circle at 20% 20%, rgba(0, 234, 255, 0.08) 0%, transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(255, 106, 0, 0.06) 0%, transparent 50%),
            radial-gradient(circle at 40% 60%, rgba(138, 43, 226, 0.04) 0%, transparent 40%),
            radial-gradient(circle at 60% 20%, rgba(50, 205, 50, 0.03) 0%, transparent 30%)
        `,
        pointerEvents: 'none',
        zIndex: 0,
        animation: 'backgroundPulse 8s ease-in-out infinite',
    },

    // Grid overlay
    '&::after': {
        content: '""',
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundImage: `
            linear-gradient(rgba(0, 234, 255, 0.02) 1px, transparent 1px),
            linear-gradient(90deg, rgba(0, 234, 255, 0.02) 1px, transparent 1px)
        `,
        backgroundSize: '50px 50px',
        pointerEvents: 'none',
        zIndex: 1,
        animation: 'gridMove 20s linear infinite',
    },

    '@keyframes backgroundPulse': {
        '0%, 100%': { opacity: 0.6 },
        '50%': { opacity: 1 },
    },

    '@keyframes gridMove': {
        '0%': { transform: 'translate(0, 0)' },
        '100%': { transform: 'translate(50px, 50px)' },
    },
}));

const Header = styled(Box)(({ theme }) => ({
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1100,
    background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.98) 0%, rgba(26, 26, 46, 0.95) 30%, rgba(22, 33, 62, 0.92) 100%)',
    backdropFilter: 'blur(20px) saturate(180%)',
    borderBottom: '2px solid transparent',
    borderImage: 'linear-gradient(90deg, #00eaff, #ff6a00, #8a2be2) 1',
    boxShadow: `
        0 4px 32px rgba(0, 234, 255, 0.3),
        inset 0 1px 0 rgba(255, 255, 255, 0.1)
    `,
    padding: '1rem 0',
    animation: 'headerGlow 4s ease-in-out infinite',

    '@keyframes headerGlow': {
        '0%, 100%': {
            boxShadow: '0 4px 32px rgba(0, 234, 255, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.1)'
        },
        '50%': {
            boxShadow: '0 6px 40px rgba(255, 106, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.2)'
        },
    },

    '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'linear-gradient(90deg, transparent, rgba(0, 234, 255, 0.1), transparent)',
        animation: 'scanline 3s linear infinite',
    },

    '@keyframes scanline': {
        '0%': { transform: 'translateX(-100%)' },
        '100%': { transform: 'translateX(100%)' },
    },
}));

const HeaderContent = styled(Container)(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '2rem',
    [theme.breakpoints.down('md')]: {
        flexDirection: 'column',
        gap: '1rem',
    }
}));

const Logo = styled(Box)(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '1rem',
    position: 'relative',
    '& .logo-text': {
        fontSize: '1.8rem',
        fontWeight: 700,
        background: 'linear-gradient(45deg, #00eaff, #ff6a00, #8a2be2, #32cd32)',
        backgroundSize: '300% 300%',
        backgroundClip: 'text',
        WebkitBackgroundClip: 'text',
        WebkitTextFillColor: 'transparent',
        textShadow: '0 0 30px rgba(0, 234, 255, 0.5)',
        animation: 'logoGradient 4s ease-in-out infinite, logoGlow 2s ease-in-out infinite',
        letterSpacing: '2px',
        fontFamily: '"Orbitron", "Roboto", sans-serif',
    },
    '& .logo-icon': {
        animation: 'logoSpin 8s linear infinite',
        filter: 'drop-shadow(0 0 20px #00eaff)',
    },

    '@keyframes logoGradient': {
        '0%, 100%': { backgroundPosition: '0% 50%' },
        '50%': { backgroundPosition: '100% 50%' },
    },

    '@keyframes logoGlow': {
        '0%, 100%': { textShadow: '0 0 30px rgba(0, 234, 255, 0.5)' },
        '50%': { textShadow: '0 0 40px rgba(255, 106, 0, 0.8)' },
    },

    '@keyframes logoSpin': {
        '0%': { transform: 'rotate(0deg)' },
        '100%': { transform: 'rotate(360deg)' },
    },
}));

const SearchBar = styled(Box)(({ theme }) => ({
    flex: 1,
    maxWidth: '600px',
    animation: 'slideIn 0.6s ease-out',
    '@keyframes slideIn': {
        '0%': {
            opacity: 0,
            transform: 'translateX(-20px)',
        },
        '100%': {
            opacity: 1,
            transform: 'translateX(0)',
        },
    },
    [theme.breakpoints.down('md')]: {
        maxWidth: '100%',
        width: '100%',
    }
}));

const CategoriesSection = styled(Box)(({ theme }) => ({
    marginBottom: '2rem',
    background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.9) 0%, rgba(26, 26, 46, 0.85) 100%)',
    borderRadius: '12px',
    padding: '1.5rem',
    boxShadow: '0 8px 32px rgba(0, 234, 255, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
    border: '1px solid rgba(0, 234, 255, 0.2)',
    backdropFilter: 'blur(10px)',
    animation: 'fadeInUp 0.7s ease-out',
    '@keyframes fadeInUp': {
        '0%': {
            opacity: 0,
            transform: 'translateY(20px)',
        },
        '100%': {
            opacity: 1,
            transform: 'translateY(0)',
        },
    },
}));

const CarouselContainer = styled(Box)(({ theme }) => ({
    position: 'relative',
    marginBottom: '2rem',
    background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.9) 0%, rgba(26, 26, 46, 0.85) 100%)',
    borderRadius: '12px',
    padding: '1.5rem',
    boxShadow: '0 8px 32px rgba(0, 234, 255, 0.1), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
    border: '1px solid rgba(0, 234, 255, 0.2)',
    backdropFilter: 'blur(10px)',
    animation: 'fadeInUp 0.8s ease-out',
}));

const CarouselGrid = styled(Box)(({ theme }) => ({
    display: 'flex',
    gap: '1rem',
    overflowX: 'auto',
    scrollBehavior: 'smooth',
    paddingBottom: '1rem',
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

const NewsCard = styled(Card)<{ selected?: boolean }>(({ theme, selected }) => ({
    minWidth: '300px',
    maxWidth: '300px',
    cursor: 'pointer',
    background: selected
        ? 'linear-gradient(135deg, rgba(0, 234, 255, 0.2) 0%, rgba(26, 26, 46, 0.9) 50%, rgba(22, 33, 62, 0.8) 100%)'
        : 'linear-gradient(135deg, rgba(13, 13, 13, 0.9) 0%, rgba(26, 26, 46, 0.85) 100%)',
    border: selected
        ? '2px solid #00eaff'
        : '1px solid rgba(0, 234, 255, 0.2)',
    borderRadius: '16px',
    backdropFilter: 'blur(20px)',
    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
    boxShadow: selected
        ? `0 12px 40px rgba(0, 234, 255, 0.4), 
           inset 0 1px 0 rgba(255, 255, 255, 0.2),
           0 0 60px rgba(0, 234, 255, 0.2)`
        : `0 8px 32px rgba(0, 234, 255, 0.1), 
           inset 0 1px 0 rgba(255, 255, 255, 0.05)`,
    position: 'relative',
    overflow: 'hidden',

    '&:hover': {
        transform: 'translateY(-8px) scale(1.03)',
        boxShadow: `
            0 20px 60px rgba(0, 234, 255, 0.3),
            inset 0 1px 0 rgba(255, 255, 255, 0.2),
            0 0 80px rgba(255, 106, 0, 0.2)
        `,
        border: '2px solid rgba(255, 106, 0, 0.6)',

        '&::before': {
            opacity: 1,
        },
    },

    '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: '-100%',
        width: '100%',
        height: '100%',
        background: 'linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent)',
        transition: 'all 0.6s',
        opacity: 0,
        animation: 'shimmer 2s infinite',
    },

    '& .MuiCardContent-root': {
        background: 'transparent',
        color: '#ffffff',
        position: 'relative',
        zIndex: 1,
    },

    '@keyframes shimmer': {
        '0%': { left: '-100%' },
        '100%': { left: '100%' },
    },
}));

const MainContent = styled(Box)(({ theme }) => ({
    display: 'flex',
    gap: '2rem',
    position: 'relative',
    maxWidth: '100%',
    overflow: 'hidden',
    animation: 'fadeIn 1s ease-out',
    [theme.breakpoints.down('lg')]: {
        flexDirection: 'column',
        gap: '1rem',
    },
}));

const ArticleContainer = styled(Paper)(({ theme }) => ({
    flex: 1,
    padding: '2rem',
    borderRadius: '12px',
    boxShadow: '0 8px 32px rgba(0, 234, 255, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
    background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.9) 0%, rgba(26, 26, 46, 0.85) 100%)',
    border: '1px solid rgba(0, 234, 255, 0.2)',
    backdropFilter: 'blur(10px)',
    color: '#ffffff',

    // Adjusted right margin for larger chatbot (450px + 40px buffer = 490px)
    marginRight: '490px',

    [theme.breakpoints.down('lg')]: {
        marginRight: '440px', // For 400px chatbot + 40px buffer
    },

    [theme.breakpoints.down('md')]: {
        marginRight: '415px', // For 375px chatbot + 40px buffer
    },

    [theme.breakpoints.down('sm')]: {
        marginRight: '0', // Full width on mobile since chatbot overlays
        marginBottom: '80px', // Space for collapsed chatbot
    }
}));

// Styled components for chatbot
const ChatContainer = styled(Box)<{ fullscreen?: boolean }>(({ theme, fullscreen }) => ({
    position: 'fixed',
    bottom: theme.spacing(3),
    right: theme.spacing(3),
    zIndex: fullscreen ? 9998 : 1300, // Lower z-index than ChatBot's fullscreen
    transition: 'all 0.3s ease',

    '&.minimized': {
        width: '60px',
        height: '60px',
    },

    '&:not(.minimized)': {
        width: fullscreen ? 'auto' : '400px',
        height: fullscreen ? 'auto' : '500px',
        background: fullscreen ? 'transparent' : 'rgba(13, 13, 13, 0.95)',
        borderRadius: fullscreen ? 0 : theme.shape.borderRadius * 2,
        border: fullscreen ? 'none' : '1px solid rgba(0, 234, 255, 0.3)',
        backdropFilter: fullscreen ? 'none' : 'blur(10px)',
        display: 'flex',
        flexDirection: 'column',
        overflow: fullscreen ? 'visible' : 'hidden',

        // Tablet responsive
        [theme.breakpoints.down('md')]: {
            width: fullscreen ? 'auto' : '350px',
            height: fullscreen ? 'auto' : '450px',
            right: theme.spacing(2),
            bottom: theme.spacing(2),
        },

        // Mobile responsive - full width
        [theme.breakpoints.down('sm')]: {
            width: fullscreen ? 'auto' : '100vw',
            height: fullscreen ? 'auto' : '80vh',
            maxHeight: fullscreen ? 'none' : '500px',
            right: 0,
            bottom: 0,
            left: 0,
            borderRadius: fullscreen ? 0 : '16px 16px 0 0', // Only round top corners
            transform: 'none',
        },

        // Very small mobile screens
        '@media (max-width: 360px)': {
            width: fullscreen ? 'auto' : '100vw',
            height: fullscreen ? 'auto' : '75vh',
            maxHeight: fullscreen ? 'none' : '400px',
            right: 0,
            bottom: 0,
            left: 0,
            borderRadius: fullscreen ? 0 : '12px 12px 0 0', // Only round top corners
        },
    },
}));

const ChatIcon = styled(Fab)(({ theme }) => ({
    // Desktop size - enlarged from 60px to 80px
    width: '80px',
    height: '80px',
    background: 'linear-gradient(45deg, #00eaff, #ff6a00)',
    color: 'white',
    boxShadow: '0 8px 32px rgba(0, 234, 255, 0.3)',
    transition: 'all 0.3s ease',
    animation: 'chatPulse 3s ease-in-out infinite',
    '&:hover': {
        background: 'linear-gradient(45deg, #00d4e6, #e55a00)',
        transform: 'scale(1.1)',
        boxShadow: '0 12px 40px rgba(0, 234, 255, 0.5)',
        animation: 'none', // Stop pulsing on hover
    },
    '@keyframes chatPulse': {
        '0%, 100%': {
            boxShadow: '0 8px 32px rgba(0, 234, 255, 0.3)',
            transform: 'scale(1)'
        },
        '50%': {
            boxShadow: '0 12px 40px rgba(255, 106, 0, 0.4)',
            transform: 'scale(1.05)'
        },
    },

    // Mobile size - keep original 60px for mobile
    [theme.breakpoints.down('lg')]: {
        width: '60px',
        height: '60px',
    },

    // Small mobile size - even smaller
    [theme.breakpoints.down('sm')]: {
        width: '56px',
        height: '56px',
    },
}));

const ChatToggleButton = styled(IconButton)(({ theme }) => ({
    position: 'absolute',
    top: theme.spacing(1),
    right: theme.spacing(1),
    color: 'rgba(255, 255, 255, 0.7)',
    '&:hover': {
        color: '#00eaff',
        background: 'rgba(0, 234, 255, 0.1)',
    },
}));

const FloatingChatToggle = styled(IconButton)(({ theme }) => ({
    position: 'fixed',
    bottom: '20px',
    right: '20px',
    width: '60px',
    height: '60px',
    background: 'linear-gradient(45deg, #ff6a00, #00eaff)',
    color: 'white',
    zIndex: 1001,
    boxShadow: '0 8px 25px rgba(255, 106, 0, 0.4)',
    animation: 'pulse 2s infinite',
    '&:hover': {
        background: 'linear-gradient(45deg, #00eaff, #ff6a00)',
        transform: 'scale(1.1)',
        boxShadow: '0 12px 35px rgba(0, 234, 255, 0.4)',
    },
    '@keyframes pulse': {
        '0%': { boxShadow: '0 8px 25px rgba(255, 106, 0, 0.4)' },
        '50%': { boxShadow: '0 12px 35px rgba(0, 234, 255, 0.5)' },
        '100%': { boxShadow: '0 8px 25px rgba(255, 106, 0, 0.4)' },
    },
    [theme.breakpoints.up('lg')]: {
        display: 'none',
    }
}));

// Floating particles animation
const ParticleOverlay = styled(Box)(({ theme }) => ({
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    pointerEvents: 'none',
    zIndex: 2,

    '&::before, &::after': {
        content: '""',
        position: 'absolute',
        width: '2px',
        height: '2px',
        background: '#00eaff',
        borderRadius: '50%',
        boxShadow: `
            0 0 6px #00eaff,
            20px 30px 0 #ff6a00,
            40px 70px 0 #8a2be2,
            90px 40px 0 #32cd32,
            130px 80px 0 #00eaff,
            160px 30px 0 #ff6a00,
            200px 60px 0 #8a2be2,
            240px 90px 0 #32cd32,
            280px 20px 0 #00eaff,
            320px 70px 0 #ff6a00,
            360px 40px 0 #8a2be2,
            400px 80px 0 #32cd32
        `,
        animation: 'particles 15s linear infinite',
    },

    '&::after': {
        animationDelay: '-7.5s',
    },

    '@keyframes particles': {
        '0%': { transform: 'translateY(100vh) rotate(0deg)' },
        '100%': { transform: 'translateY(-100vh) rotate(360deg)' },
    },
}));

// Enhanced footer
const FooterSection = styled(Box)(({ theme }) => ({
    marginTop: '6rem',
    padding: '4rem 0 2rem',
    background: `
        linear-gradient(135deg, 
            rgba(13, 13, 13, 0.98) 0%, 
            rgba(26, 26, 46, 0.95) 30%, 
            rgba(22, 33, 62, 0.92) 70%,
            rgba(13, 13, 13, 0.98) 100%
        )
    `,
    borderTop: '2px solid transparent',
    borderImage: 'linear-gradient(90deg, #00eaff, #ff6a00, #8a2be2) 1',
    backdropFilter: 'blur(20px)',
    position: 'relative',

    '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '2px',
        background: 'linear-gradient(90deg, transparent, #00eaff, #ff6a00, #8a2be2, transparent)',
        animation: 'borderGlow 3s ease-in-out infinite',
    },

    '@keyframes borderGlow': {
        '0%, 100%': { opacity: 0.5 },
        '50%': { opacity: 1 },
    },
}));

const AudioBar = styled(Card)(({ theme }) => ({
    marginBottom: '2rem',
    background: 'linear-gradient(90deg, #0f2027 0%, #2c5364 100%)',
    color: 'white',
    borderRadius: '18px',
    overflow: 'hidden',
    boxShadow: '0 0 24px 4px #00eaff55',
    border: '2px solid',
    borderImage: 'linear-gradient(90deg, #00eaff 0%, #ff6a00 100%) 1',
    position: 'relative',
    animation: 'audioBarGlow 2.5s linear infinite',
    '@keyframes audioBarGlow': {
        '0%': { boxShadow: '0 0 24px 4px #00eaff55' },
        '50%': { boxShadow: '0 0 48px 8px #ff6a0055' },
        '100%': { boxShadow: '0 0 24px 4px #00eaff55' },
    },
}));

const AudioControls = styled(Box)(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    padding: '1.2rem',
    gap: '1.5rem',
    background: 'rgba(0, 234, 255, 0.05)',
    borderRadius: '16px',
    boxShadow: '0 2px 12px 0 #00eaff22',
}));

const PlayPauseButton = styled(IconButton, {
    shouldForwardProp: (prop) => prop !== 'isplaying',
})<{ isplaying: boolean }>(({ isplaying }) => ({
    color: 'white',
    background: isplaying ? 'linear-gradient(90deg, #ff6a00 0%, #00eaff 100%)' : 'rgba(255,255,255,0.1)',
    boxShadow: isplaying ? '0 0 0 6px #ff6a0033' : 'none',
    animation: isplaying ? 'pulsePlay 1.2s infinite' : 'none',
    '&:hover': {
        background: 'linear-gradient(90deg, #00eaff 0%, #ff6a00 100%)',
        transform: 'scale(1.15)',
    },
    '@keyframes pulsePlay': {
        '0%': { boxShadow: '0 0 0 0 #ff6a0033' },
        '70%': { boxShadow: '0 0 0 12px #00eaff22' },
        '100%': { boxShadow: '0 0 0 0 #ff6a0033' },
    },
}));

const ProgressContainer = styled(Box)(({ theme }) => ({
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    gap: '0.7rem',
    background: 'rgba(44, 83, 100, 0.15)',
    borderRadius: '8px',
    padding: '0.3rem 0.7rem',
}));

const FloatingChatWidget = styled(Box)<{ expanded: boolean }>(({ theme, expanded }) => ({
    position: 'fixed',
    bottom: '20px',
    right: '20px',
    zIndex: 1000,
    transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',

    // When collapsed - just an icon
    ...(!expanded && {
        width: '56px',
        height: '56px',
        borderRadius: '50%',
        background: 'linear-gradient(135deg, #ff6a00 0%, #00eaff 100%)',
        boxShadow: '0 8px 32px rgba(255, 106, 0, 0.4)',
        cursor: 'pointer',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        animation: 'chatPulse 3s ease-in-out infinite',

        '&:hover': {
            transform: 'scale(1.1)',
            boxShadow: '0 12px 40px rgba(0, 234, 255, 0.5)',
        },

        '@keyframes chatPulse': {
            '0%, 100%': { boxShadow: '0 8px 32px rgba(255, 106, 0, 0.4)' },
            '50%': { boxShadow: '0 12px 40px rgba(0, 234, 255, 0.3)' },
        }
    }),

    // When expanded - 25% larger width
    ...(expanded && {
        width: '450px', // Increased from 360px (25% larger)
        height: '580px',
        borderRadius: '20px',
        background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.98) 0%, rgba(26, 26, 46, 0.95) 50%, rgba(22, 33, 62, 0.92) 100%)',
        border: '1px solid rgba(255, 106, 0, 0.3)',
        backdropFilter: 'blur(20px)',
        boxShadow: '0 24px 64px rgba(0, 0, 0, 0.8), 0 8px 32px rgba(255, 106, 0, 0.2)',
        overflow: 'hidden',

        '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'radial-gradient(circle at 20% 20%, rgba(255, 106, 0, 0.08) 0%, transparent 50%)',
            pointerEvents: 'none',
        }
    }),

    // Responsive design with 25% larger widths
    [theme.breakpoints.down('lg')]: {
        right: '15px',
        bottom: '15px',

        ...(expanded && {
            width: '400px', // Increased from 320px (25% larger)
            height: '520px',
        })
    },

    [theme.breakpoints.down('md')]: {
        ...(expanded && {
            width: '375px', // Increased from 300px (25% larger)
            height: '480px',
        })
    },

    [theme.breakpoints.down('sm')]: {
        ...(expanded && {
            width: 'calc(100vw - 20px)',
            height: '70vh',
            right: '10px',
            left: '10px',
            bottom: '10px',
        })
    }
}));

const ChatWidgetHeader = styled(Box)(({ theme }) => ({
    background: 'linear-gradient(135deg, rgba(255, 106, 0, 0.9) 0%, rgba(0, 234, 255, 0.7) 100%)',
    padding: '16px 20px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderRadius: '20px 20px 0 0',
    position: 'relative',

    '&::after': {
        content: '""',
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: '1px',
        background: 'linear-gradient(90deg, transparent 0%, rgba(255, 255, 255, 0.3) 50%, transparent 100%)',
    }
}));

const OnlineIndicator = styled(Box)(({ theme }) => ({
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    background: '#4caf50',
    marginLeft: '8px',
    animation: 'onlinePulse 2s ease-in-out infinite',

    '@keyframes onlinePulse': {
        '0%, 100%': { opacity: 1, transform: 'scale(1)' },
        '50%': { opacity: 0.7, transform: 'scale(1.2)' },
    }
}));

const CloseButton = styled(IconButton)(({ theme }) => ({
    color: 'white',
    width: '32px',
    height: '32px',
    transition: 'all 0.3s ease',

    '&:hover': {
        background: 'rgba(255, 255, 255, 0.1)',
        transform: 'rotate(90deg)',
    }
}));

// Date filter styled components
const DateFilter = styled(Box)(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    gap: theme.spacing(2),
    padding: theme.spacing(2),
    background: 'rgba(13, 13, 13, 0.6)',
    borderRadius: theme.shape.borderRadius,
    marginBottom: theme.spacing(2),
    position: 'relative',
    [theme.breakpoints.down('sm')]: {
        flexDirection: 'column',
        alignItems: 'flex-start',
        gap: theme.spacing(1),
    },
}));

const DateFilterContainer = styled(Box)(({ theme }) => ({
    display: 'flex',
    gap: theme.spacing(1),
    overflowX: 'auto',
    scrollBehavior: 'smooth',
    maxWidth: 'calc(5 * 140px + 4 * 8px)', // Show max 5 items
    '&::-webkit-scrollbar': {
        height: '4px',
    },
    '&::-webkit-scrollbar-track': {
        background: 'rgba(255, 255, 255, 0.1)',
        borderRadius: '2px',
    },
    '&::-webkit-scrollbar-thumb': {
        background: 'rgba(0, 234, 255, 0.3)',
        borderRadius: '2px',
    },
    '&::-webkit-scrollbar-thumb:hover': {
        background: 'rgba(0, 234, 255, 0.5)',
    },
    [theme.breakpoints.down('sm')]: {
        maxWidth: 'calc(4 * 160px + 3 * 8px)', // Show max 4 items on mobile with wider buttons
    },
}));

const DateButton = styled(Button)<{ selected?: boolean }>(({ theme, selected }) => ({
    background: selected ? 'rgba(0, 234, 255, 0.1)' : 'rgba(13, 13, 13, 0.6)',
    color: selected ? '#00eaff' : 'rgba(255, 255, 255, 0.7)',
    border: `1px solid ${selected ? '#00eaff' : 'rgba(0, 234, 255, 0.2)'}`,
    borderRadius: theme.shape.borderRadius,
    padding: theme.spacing(1, 2),
    textTransform: 'none',
    '&:hover': {
        background: selected ? 'rgba(0, 234, 255, 0.15)' : 'rgba(0, 234, 255, 0.05)',
        borderColor: '#00eaff',
    },
}));

// Available dates for filtering
const AVAILABLE_DATES = [
    '2025-06-14',
];

interface NewsArticle {
    id: number;
    group_id: string;
    headline: string;
    category: string;
    content: string;
    summary: string;
    date: string;
    image_url?: string;
}

interface ArticleData {
    id?: number;
    group_id?: string;
    date?: string;
    category: string;
    headline: string;
    subheadline: string;
    lead: string;
    body: Array<{
        section: string;
        content: string;
        sources: string[];
        sentisement_from_the_content: string;
        sentisement_from_the_posts_or_comments: string;
        fake_news_probability: number;
        date: string;
        Publisher_region_diversity: string[];
        Publishers: string[];
    }>;
    conclusion: string;
    timeline: Record<string, string>;
}

const NewsPortal: React.FC = () => {
    console.log('NewsPortal component loaded');

    // const navigate = useNavigate(); // Not needed anymore
    // States
    const [articles, setArticles] = useState<NewsArticle[]>([]);
    const [selectedArticle, setSelectedArticle] = useState<ArticleData | null>(null);
    const [selectedDate, setSelectedDate] = useState<string>('');
    const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
    const [category, setCategory] = useState('all');
    const [search, setSearch] = useState('');
    const [fuzzySearch, setFuzzySearch] = useState(false); // Add fuzzy search state
    const [loading, setLoading] = useState(false);
    // Remove categories state since we'll use fixed categories
    const [isChatMinimized, setIsChatMinimized] = useState(true);
    const [isChatFullscreen, setIsChatFullscreen] = useState(false);
    const [selectedSectionIndex, setSelectedSectionIndex] = useState<number>(0);
    const [availableDates, setAvailableDates] = useState<string[]>([]);
    const [isVideoModalOpen, setIsVideoModalOpen] = useState(false);

    // Audio states
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [audioError, setAudioError] = useState(false);
    const [isBookmarked, setIsBookmarked] = useState(false);
    const [audioUnlocked, setAudioUnlocked] = useState(false);
    const [isProcessingAudio, setIsProcessingAudio] = useState(false);

    // 在 NewsPortal 组件中添加新的状态
    const [summaryDate, setSummaryDate] = useState<string>('');

    const audioRef = useRef<HTMLAudioElement>(null);
    const videoRef = useRef<HTMLVideoElement>(null);
    const carouselRef = useRef<HTMLDivElement>(null);
    const dateFilterRef = useRef<HTMLDivElement>(null);

    // State definitions should be at the top of the component
    const [canScrollLeft, setCanScrollLeft] = useState(false);
    const [canScrollRight, setCanScrollRight] = useState(false);

    // Add isMobile state
    const [isMobile, setIsMobile] = useState(window.innerWidth <= 600);

    // Prevent double-triggering on mobile
    const lastActionTime = useRef<number>(0);
    const touchStartTime = useRef<number>(0);

    const handleResize = () => setIsMobile(window.innerWidth <= 600);

    useEffect(() => {
        const checkMobile = () => {
            const userAgent = navigator.userAgent || navigator.vendor || (window as any).opera;
            const mobile = /android|blackberry|iemobile|ipad|iphone|ipod|opera mini|webos/i.test(userAgent.toLowerCase());
            setIsMobile(mobile);
        };

        checkMobile();
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    useEffect(() => {
        console.log('selectedGroupId changed:', selectedGroupId);
    }, [selectedGroupId]);

    // Update the NewsPortal.tsx to add debugging
    // Find line 897 and replace it with:

    console.log('=== API URL DEBUG ===');
    console.log('process.env.REACT_APP_API_URL:', process.env.REACT_APP_API_URL);
    console.log('config.API_URL:', config.API_URL);
    console.log('typeof process.env.REACT_APP_API_URL:', typeof process.env.REACT_APP_API_URL);
    console.log('All REACT_APP env vars:', Object.keys(process.env).filter(key => key.startsWith('REACT_APP')));

    // Fix API URL - provide fallback for development
    const API_URL = config.API_URL;
    const STATIC_URL = config.STATIC_URL;
    console.log('Final API_URL being used:', API_URL);
    console.log('=== END DEBUG ===');


    // Fixed categories - no longer need to fetch from API
    const fixedCategories = {
        social: 'Social',
        tech: 'Technology',
        entertainment: 'Entertainment'
    };

    // Fetch articles on component mount and when filters change
    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                await Promise.all([
                    fetchArticles(),
                    fetchDates(),
                    fetchConfig()  // 添加配置获取
                ]);
            } catch (error) {
                console.error('Error fetching data:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, [category, search, selectedDate, fuzzySearch]); // Add fuzzySearch to dependencies

    // Auto-select first article when articles load (but only if no date is manually selected)
    useEffect(() => {
        console.log('Auto-selection useEffect triggered:', {
            articlesLength: articles.length,
            selectedGroupId,
            selectedArticle: selectedArticle ? 'exists' : 'null',
            selectedDate,
            condition: articles.length > 0 && !selectedGroupId && !selectedArticle && !selectedDate
        });

        // Only auto-select if no date is manually selected and no article is already selected
        if (articles.length > 0 && !selectedGroupId && !selectedArticle && !selectedDate) {
            handleArticleSelect(articles[0]);
        } else {
            console.log('Auto-selection skipped:', {
                reason: articles.length === 0 ? 'no articles' :
                    selectedGroupId ? 'group already selected' :
                        selectedArticle ? 'article already selected' :
                            selectedDate ? 'date manually selected' : 'unknown'
            });
        }
    }, [articles, selectedGroupId, selectedArticle, selectedDate]);

    const fetchArticles = async () => {
        try {
            console.log('Fetching articles with params:', {
                category: category !== 'all' ? category : undefined,
                search: search || undefined,
                date: selectedDate || undefined,
                fuzzy: fuzzySearch
            });

            const response = await axios.get(`${API_URL}/api/news`, {
                params: {
                    category: category !== 'all' ? category : undefined,
                    search: search || undefined,
                    date: selectedDate || undefined,
                    fuzzy: fuzzySearch // Add fuzzy parameter
                }
            });

            console.log('Raw response data:', response.data);
            console.log('Response data type:', typeof response.data);
            console.log('Is array?', Array.isArray(response.data));

            // Check if response.data has a 'news' property or is directly an array
            let articlesData;
            if (response.data && response.data.news) {
                console.log('Using response.data.news');
                articlesData = response.data.news;
            } else if (Array.isArray(response.data)) {
                console.log('Using response.data directly (array)');
                articlesData = response.data;
            } else {
                console.log('Unexpected response format:', response.data);
                articlesData = [];
            }

            console.log('Final articles data:', articlesData);
            console.log('Articles count:', articlesData.length);

            setArticles(articlesData);
        } catch (error) {
            console.error('Error fetching articles:', error);
            setArticles([]);
        }
    };

    // Remove fetchCategories function since we're using fixed categories

    const fetchDates = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/news/dates`); // Changed from /api/dates
            setAvailableDates(response.data.dates || []);
        } catch (error) {
            console.error('Error fetching dates:', error);
            setAvailableDates(['2025-06-14']); // fallback
        }
    };

    const fetchArticleDetail = async (groupId: string, date: string) => {
        try {
            console.log('Fetching article detail for:', { groupId, date });
            setLoading(true);

            const url = `${API_URL}/api/news/articles/${date}/${groupId}`;
            console.log('Request URL:', url);

            const response = await axios.get(url);
            console.log('Article detail response:', response.data);
            console.log('Article detail response type:', typeof response.data);

            setSelectedArticle(response.data);
            console.log('selectedArticle state updated');
        } catch (error: any) {
            console.error('Error fetching article detail:', error);
            console.error('Error details:', {
                message: error?.message || 'Unknown error',
                status: error?.response?.status,
                statusText: error?.response?.statusText,
                data: error?.response?.data
            });
        } finally {
            setLoading(false);
            console.log('Loading set to false');
        }
    };

    const handleArticleSelect = (article: NewsArticle) => {
        console.log('Article selected:', article);
        console.log('Setting selectedGroupId to:', article.group_id);
        console.log('Setting selectedDate to:', article.date);

        setSelectedGroupId(article.group_id);
        // Don't override selectedDate if it's already set by user
        if (!selectedDate) {
            setSelectedDate(article.date);
        }

        // Fetch article detail instead of navigating
        console.log('Calling fetchArticleDetail...');
        fetchArticleDetail(article.group_id, article.date);

        // Reset audio state
        setIsPlaying(false);
        setCurrentTime(0);
        setAudioError(false);
        setAudioUnlocked(false); // Reset audio unlock state for new article

        // Check audio availability with range request (mobile-friendly)
        const audioUrl = `${STATIC_URL}/audio/${article.date}/${article.group_id}.mp3`;
        fetch(audioUrl, {
            method: 'GET',
            headers: {
                'Range': 'bytes=0-1'  // Request only the first 2 bytes
            }
        })
            .then(response => {
                // Accept both 206 (Partial Content) and 200 (OK) as success
                if (response.ok || response.status === 206) {
                    setAudioError(false);
                } else {
                    setAudioError(true);
                }
            })
            .catch(error => {
                console.warn('NewsPortal: Audio availability check failed:', error);
            });
    };

    const handleCategoryChange = (event: React.SyntheticEvent, newValue: string) => {
        setCategory(newValue);
    };

    const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSearch(event.target.value);
    };

    const handleSearchKeyPress = (event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === 'Enter') {
            fetchArticles();
        }
    };

    const handleSearchSubmit = () => {
        fetchArticles();
    };

    // Mobile audio unlock function
    const unlockAudio = async () => {
        if (!audioRef.current || audioUnlocked) return;

        try {
            console.log('🔓 NewsPortal: Attempting to unlock mobile audio...');

            // Create a short silent audio to unlock the audio context
            const audio = audioRef.current;

            // Method 1: Try to unlock the HTML5 audio element
            const originalVolume = audio.volume;
            audio.volume = 0.01; // Very low volume for unlock
            audio.muted = false; // Ensure not muted

            // Try to play and immediately pause to unlock audio
            const playPromise = audio.play();
            if (playPromise !== undefined) {
                try {
                    await playPromise;
                    audio.pause();
                    audio.currentTime = 0;
                    audio.volume = originalVolume;
                    setAudioUnlocked(true);
                    console.log('NewsPortal: HTML5 Audio unlocked successfully');
                    return;
                } catch (playError) {
                    console.warn('NewsPortal: HTML5 audio unlock failed:', playError);
                }
            }

            // Method 2: Try AudioContext unlock (for iOS Web Audio API issues)
            try {
                const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
                if (AudioContextClass) {
                    const audioContext = new AudioContextClass();

                    // Check if AudioContext is suspended (common on iOS)
                    if (audioContext.state === 'suspended') {
                        console.log('NewsPortal: AudioContext is suspended, attempting to resume...');
                        await audioContext.resume();
                        console.log('NewsPortal: AudioContext resumed successfully');
                    }

                    // Create a short beep to unlock the audio pipeline
                    const oscillator = audioContext.createOscillator();
                    const gainNode = audioContext.createGain();

                    oscillator.connect(gainNode);
                    gainNode.connect(audioContext.destination);

                    // Set to very low volume and high frequency (barely audible)
                    gainNode.gain.setValueAtTime(0.001, audioContext.currentTime);
                    oscillator.frequency.setValueAtTime(20000, audioContext.currentTime); // 20kHz

                    oscillator.start();
                    oscillator.stop(audioContext.currentTime + 0.01); // 10ms beep

                    // Clean up
                    setTimeout(() => {
                        oscillator.disconnect();
                        gainNode.disconnect();
                        audioContext.close();
                    }, 100);

                    setAudioUnlocked(true);
                    console.log('NewsPortal: AudioContext unlock completed');
                    return;
                }
            } catch (contextError) {
                console.warn('NewsPortal: AudioContext unlock failed:', contextError);
            }

            // Method 3: Fallback
            try {
                if ('webkitAudioContext' in window) {
                    const context = new (window as any).webkitAudioContext();
                    if (context.state === 'suspended') {
                        await context.resume();
                    }
                    context.close();
                }

                setAudioUnlocked(true);
                console.log('NewsPortal: Fallback audio unlock completed');
            } catch (fallbackError) {
                console.warn('NewsPortal: Fallback audio unlock failed:', fallbackError);
            }

        } catch (error) {
            console.error('NewsPortal: All audio unlock methods failed:', error);
        }
    };

    // Audio controls
    const handlePlayPause = async (event?: React.MouseEvent | React.TouchEvent) => {
        // Prevent double-triggering on mobile devices
        const now = Date.now();
        if (now - lastActionTime.current < 300) { // 300ms debounce
            console.log('NewsPortal: Action ignored - too soon after last action');
            return;
        }
        lastActionTime.current = now;

        if (!audioRef.current || audioError || !selectedGroupId || isProcessingAudio) return;

        setIsProcessingAudio(true);
        console.log('NewsPortal: Play/Pause triggered. Mobile:', isMobile, 'Unlocked:', audioUnlocked);

        try {
            // On mobile, first interaction needs to unlock audio
            if (isMobile && !audioUnlocked) {
                console.log('NewsPortal: Mobile unlock required...');
                await unlockAudio();

                // If unlock failed, don't proceed
                if (!audioUnlocked) {
                    console.error('NewsPortal: Audio unlock failed, cannot proceed with playback');
                    setIsProcessingAudio(false);
                    return;
                }
            }

            // Small delay for mobile to ensure audio context is ready
            if (isMobile && !isPlaying) {
                await new Promise(resolve => setTimeout(resolve, 100));
            }

            if (isPlaying) {
                audioRef.current.pause();
                setIsPlaying(false);
                console.log('NewsPortal: Audio paused');
            } else {
                console.log('NewsPortal: Attempting to play audio...');

                // On iOS, ensure the audio element is ready
                if (isMobile) {
                    // Load the audio if it's not already loaded
                    if (audioRef.current.readyState < 2) {
                        console.log('NewsPortal: Loading audio data...');
                        audioRef.current.load();

                        // Wait for enough data to play
                        await new Promise((resolve, reject) => {
                            const timeout = setTimeout(() => {
                                reject(new Error('Audio load timeout'));
                            }, 5000);

                            const onCanPlay = () => {
                                clearTimeout(timeout);
                                audioRef.current?.removeEventListener('canplay', onCanPlay);
                                audioRef.current?.removeEventListener('error', onError);
                                resolve(undefined);
                            };

                            const onError = (e: any) => {
                                clearTimeout(timeout);
                                audioRef.current?.removeEventListener('canplay', onCanPlay);
                                audioRef.current?.removeEventListener('error', onError);
                                reject(e);
                            };

                            audioRef.current?.addEventListener('canplay', onCanPlay);
                            audioRef.current?.addEventListener('error', onError);
                        });
                    }

                    // Set appropriate attributes for iOS
                    audioRef.current.preload = 'auto';
                    audioRef.current.setAttribute('webkit-playsinline', 'true');
                    audioRef.current.setAttribute('playsinline', 'true');
                }

                // Handle play promise properly (required for mobile)
                const playPromise = audioRef.current.play();
                if (playPromise !== undefined) {
                    playPromise
                        .then(() => {
                            setIsPlaying(true);
                            console.log('NewsPortal: Audio playing successfully');
                        })
                        .catch((error) => {
                            console.error('NewsPortal: Audio play failed:', error);

                            // Try to diagnose the issue
                            if (error.name === 'NotAllowedError') {
                                console.error('NewsPortal: User gesture required or autoplay policy blocked');
                                setAudioUnlocked(false); // Reset unlock state
                            } else if (error.name === 'NotSupportedError') {
                                console.error('NewsPortal: Audio format not supported');
                            } else if (error.name === 'AbortError') {
                                console.error('NewsPortal: Play operation was aborted');
                            }

                            setAudioError(true);
                            setIsPlaying(false);
                        });
                } else {
                    setIsPlaying(true);
                    console.log('NewsPortal: Audio playing (no promise)');
                }
            }
        } catch (error) {
            console.error('NewsPortal: Audio playback error:', error);
            setAudioError(true);
            setIsPlaying(false);
        } finally {
            // Reset processing state after a delay to prevent rapid clicking
            setTimeout(() => {
                setIsProcessingAudio(false);
            }, 200);
        }
    };

    const handleTimeUpdate = () => {
        if (audioRef.current) {
            setCurrentTime(audioRef.current.currentTime);
        }
    };

    const handleLoadedMetadata = () => {
        if (audioRef.current) {
            setDuration(audioRef.current.duration);
        }
    };

    const formatTime = (time: number) => {
        const minutes = Math.floor(time / 60);
        const seconds = Math.floor(time % 60);
        return `${minutes}:${seconds.toString().padStart(2, '0')}`;
    };

    // Carousel navigation
    const scrollCarousel = (direction: 'left' | 'right') => {
        if (carouselRef.current) {
            const scrollAmount = 320; // card width + gap
            carouselRef.current.scrollBy({
                left: direction === 'left' ? -scrollAmount : scrollAmount,
                behavior: 'smooth',
            });
        }
    };

    const scrollDateFilter = (direction: 'left' | 'right') => {
        if (dateFilterRef.current) {
            const scrollAmount = 150; // approximate button width + gap
            dateFilterRef.current.scrollBy({
                left: direction === 'left' ? -scrollAmount : scrollAmount,
                behavior: 'smooth',
            });
        }
    };

    // Source link rendering with improved styling
    const renderContentWithSources = (content: string, sources: string[]) => {
        if (!sources || sources.length === 0) {
            return content;
        }

        let processedContent = content;

        // Handle different source patterns
        sources.forEach((source, index) => {
            const patterns = [
                `[${index + 1}]`,
                `[SOURCE_${index + 1}]`,
                `\\[${index + 1}\\]`,
                `\\[SOURCE_${index + 1}\\]`
            ];

            patterns.forEach(pattern => {
                const regex = new RegExp(pattern.replace(/[\[\]]/g, '\\$&'), 'g');
                processedContent = processedContent.replace(
                    regex,
                    `<a href="${source}" target="_blank" rel="noopener noreferrer" style="color: #00eaff; text-decoration: none; font-weight: 600; padding: 4px 8px; background: linear-gradient(45deg, rgba(0, 234, 255, 0.1), rgba(255, 106, 0, 0.05)); border: 1px solid rgba(0, 234, 255, 0.3); border-radius: 6px; transition: all 0.3s ease; display: inline-block; margin: 0 2px;" onmouseover="this.style.backgroundColor='rgba(0, 234, 255, 0.2)'; this.style.color='white'; this.style.transform='translateY(-1px)'; this.style.boxShadow='0 4px 12px rgba(0, 234, 255, 0.3)'" onmouseout="this.style.backgroundColor='transparent'; this.style.color='#00eaff'; this.style.transform='translateY(0)'; this.style.boxShadow='none'">[${index + 1}]</a>`
                );
            });
        });

        return processedContent;
    };

    const renderSourcesList = (sources: string[]) => {
        if (!sources || sources.length === 0) {
            return null;
        }

        const truncateUrl = (url: string, maxLength: number = 60) => {
            if (url.length <= maxLength) return url;
            return url.substring(0, maxLength) + '...';
        };

        return (
            <Box sx={{ mt: 2, pt: 2, borderTop: '1px solid rgba(0, 234, 255, 0.2)' }}>
                <Typography variant="subtitle2" sx={{ color: '#00eaff', mb: 1, fontWeight: 600 }}>
                    Sources:
                </Typography>
                {sources.map((source, index) => (
                    <Typography
                        key={index}
                        variant="body2"
                        sx={{
                            color: 'rgba(255, 255, 255, 0.8)',
                            mb: 0.5,
                            fontSize: '0.85rem',
                            wordBreak: 'break-all',
                            overflow: 'hidden',
                            display: 'flex',
                            alignItems: 'flex-start',
                            gap: 0.5,
                        }}
                    >
                        <span style={{
                            color: '#00eaff',
                            fontWeight: 600,
                            flexShrink: 0,
                        }}>
                            [{index + 1}]
                        </span>
                        <a
                            href={source}
                            target="_blank"
                            rel="noopener noreferrer"
                            title={source}
                            style={{
                                color: 'rgba(255, 255, 255, 0.8)',
                                textDecoration: 'none',
                                overflow: 'hidden',
                                textOverflow: 'ellipsis',
                                whiteSpace: 'nowrap',
                                minWidth: 0,
                                flex: 1,
                            }}
                            onMouseOver={(e) => (e.target as HTMLAnchorElement).style.color = '#00eaff'}
                            onMouseOut={(e) => (e.target as HTMLAnchorElement).style.color = 'rgba(255, 255, 255, 0.8)'}
                        >
                            <Box
                                component="span"
                                sx={{
                                    display: 'inline-block',
                                    maxWidth: '100%',
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis',
                                    whiteSpace: 'nowrap',
                                    '@media (max-width: 600px)': {
                                        maxWidth: '200px',
                                    },
                                    '@media (max-width: 400px)': {
                                        maxWidth: '150px',
                                    },
                                }}
                            >
                                {source}
                            </Box>
                        </a>
                    </Typography>
                ))}
            </Box>
        );
    };

    // Fix categories extraction - get unique values from the categories object
    const uniqueCategories = Array.from(new Set(Object.values(fixedCategories))).filter(Boolean);

    const handleDateChange = (date: string) => {

        setSelectedDate(date);
        setSearch('');
        setCategory('all');
        setSelectedGroupId(null);
        setSelectedArticle(null);

    };

    const toggleChat = () => {
        setIsChatMinimized(!isChatMinimized);
    };

    const handleChatFullscreenChange = (isFullscreen: boolean) => {
        setIsChatFullscreen(isFullscreen);
    };

    // Add a useEffect to monitor selectedArticle changes
    useEffect(() => {
        if (selectedArticle) {
            console.log('selectedArticle details:', {
                headline: selectedArticle.headline,
                group_id: selectedArticle.group_id,
                date: selectedArticle.date,
                bodyLength: selectedArticle.body?.length
            });
        }
    }, [selectedArticle]);

    // Add a useEffect to monitor selectedGroupId changes
    useEffect(() => {
        console.log('selectedGroupId changed:', selectedGroupId);
    }, [selectedGroupId]);

    // Mobile touch event handlers for NewsPortal
    const handleTouchStart = (event: React.TouchEvent) => {
        touchStartTime.current = Date.now();
        console.log('👆 NewsPortal: Touch start');
    };

    const handleTouchEnd = (event: React.TouchEvent) => {
        const touchDuration = Date.now() - touchStartTime.current;
        console.log('👆 NewsPortal: Touch end, duration:', touchDuration);

        // Only handle touch end if it's a proper tap (not a long press or swipe)
        if (touchDuration < 1000 && touchDuration > 50) {
            event.preventDefault(); // Prevent click event from firing
            handlePlayPause(event);
        }
    };

    const handleClick = (event: React.MouseEvent) => {
        // Only handle click if not on mobile or if no recent touch
        if (!isMobile || Date.now() - touchStartTime.current > 500) {
            handlePlayPause(event);
        }
    };

    // Add fuzzy search toggle handler
    const handleFuzzySearchToggle = (event: React.ChangeEvent<HTMLInputElement>) => {
        setFuzzySearch(event.target.checked);
    };

    // 新增：获取配置信息
    const fetchConfig = async () => {
        try {
            const response = await axios.get(`${API_URL}/api/config/summary-date`);
            setSummaryDate(response.data.date);
            console.log('Summary date loaded:', response.data.date);
        } catch (error) {
            console.error('Error fetching config:', error);
            setSummaryDate('2025-07-12'); // fallback
        }
    };

    return (
        <Box sx={{ minHeight: '100vh', background: 'inherit' }}>
            {/* Header */}
            <Header>
                <HeaderContent maxWidth={false}>
                    <Logo>
                        <SmartToy
                            className="logo-icon"
                            sx={{ fontSize: '2.5rem', color: '#00eaff' }}
                        />
                        <Typography className="logo-text">
                            AI News Sense
                        </Typography>
                    </Logo>
                    <SearchBar>
                        <TextField
                            fullWidth
                            variant="outlined"
                            placeholder="Search news..."
                            value={search}
                            onChange={handleSearchChange}
                            onKeyPress={handleSearchKeyPress}
                            InputProps={{
                                startAdornment: (
                                    <InputAdornment position="start">
                                        <IconButton
                                            size="small"
                                            onClick={handleSearchSubmit}
                                            sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
                                        >
                                            <SearchIcon />
                                        </IconButton>
                                    </InputAdornment>
                                ),
                                endAdornment: (
                                    <InputAdornment position="end">
                                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                            {/* Fuzzy Search Toggle */}
                                            <Tooltip title="Enable fuzzy search to find results with typos and similar words">
                                                <FormControlLabel
                                                    control={
                                                        <Switch
                                                            checked={fuzzySearch}
                                                            onChange={handleFuzzySearchToggle}
                                                            size="small"
                                                            sx={{
                                                                '& .MuiSwitch-switchBase.Mui-checked': {
                                                                    color: '#00eaff',
                                                                },
                                                                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                                                                    backgroundColor: '#00eaff',
                                                                },
                                                                '& .MuiSwitch-track': {
                                                                    backgroundColor: 'rgba(255, 255, 255, 0.2)',
                                                                }
                                                            }}
                                                        />
                                                    }
                                                    label={
                                                        <Typography
                                                            variant="caption"
                                                            sx={{
                                                                color: fuzzySearch ? '#00eaff' : 'rgba(255, 255, 255, 0.7)',
                                                                fontSize: '0.75rem',
                                                                fontWeight: fuzzySearch ? 600 : 400,
                                                                transition: 'all 0.3s ease',
                                                                '@media (max-width: 768px)': {
                                                                    display: 'none'
                                                                }
                                                            }}
                                                        >
                                                            Fuzzy
                                                        </Typography>
                                                    }
                                                    sx={{
                                                        margin: 0,
                                                        '& .MuiFormControlLabel-label': {
                                                            paddingLeft: '4px'
                                                        }
                                                    }}
                                                />
                                            </Tooltip>

                                            {/* Clear Search Button */}
                                            {search && (
                                                <IconButton
                                                    size="small"
                                                    onClick={() => {
                                                        setSearch('');
                                                        setTimeout(() => fetchArticles(), 100);
                                                    }}
                                                    sx={{ color: 'rgba(255, 255, 255, 0.7)' }}
                                                >
                                                    <Close fontSize="small" />
                                                </IconButton>
                                            )}
                                        </Box>
                                    </InputAdornment>
                                ),
                                sx: {
                                    background: 'rgba(0, 234, 255, 0.1)',
                                    borderRadius: '12px',
                                    '& fieldset': {
                                        borderColor: 'rgba(0, 234, 255, 0.2)',
                                    },
                                    '&:hover fieldset': {
                                        borderColor: 'rgba(0, 234, 255, 0.3)',
                                    },
                                    '&.Mui-focused fieldset': {
                                        borderColor: '#00eaff',
                                    },
                                    '& input': {
                                        color: 'white',
                                        '&::placeholder': {
                                            color: 'rgba(255, 255, 255, 0.5)',
                                            opacity: 1,
                                        },
                                    },
                                },
                            }}
                        />
                    </SearchBar>
                    {/* Video Modal Button */}
                    <Tooltip title="Watch Summary Video">
                        <IconButton
                            onClick={() => setIsVideoModalOpen(true)}
                            sx={{
                                color: '#00eaff',
                                background: 'rgba(0, 234, 255, 0.1)',
                                borderRadius: '12px',
                                padding: '12px',
                                '&:hover': {
                                    background: 'rgba(0, 234, 255, 0.2)',
                                    transform: 'scale(1.05)',
                                },
                                transition: 'all 0.3s ease',
                                '@media (max-width: 768px)': {
                                    padding: '8px',
                                },
                            }}
                        >
                            <VideoLibrary sx={{ fontSize: '1.5rem' }} />
                        </IconButton>
                    </Tooltip>
                </HeaderContent>
            </Header>

            {/* Add Search Status Indicator */}
            {search && (
                <Container maxWidth={false} sx={{ pt: 2, pb: 1 }}>
                    <Box sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1,
                        background: 'rgba(0, 234, 255, 0.05)',
                        border: '1px solid rgba(0, 234, 255, 0.2)',
                        borderRadius: '8px',
                        padding: '8px 12px',
                        maxWidth: '1000px',
                        margin: '0 auto'
                    }}>
                        <SearchIcon sx={{ color: '#00eaff', fontSize: '1rem' }} />
                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                            {fuzzySearch ? 'Fuzzy search' : 'Exact search'} for:
                            <span style={{ color: '#00eaff', fontWeight: 600, marginLeft: '4px' }}>
                                "{search}"
                            </span>
                        </Typography>
                        {fuzzySearch && (
                            <Chip
                                label="AI Enhanced"
                                size="small"
                                sx={{
                                    background: 'linear-gradient(45deg, #00eaff, #ff6a00)',
                                    color: 'white',
                                    fontSize: '0.7rem',
                                    height: '20px',
                                    '& .MuiChip-label': {
                                        padding: '0 8px'
                                    }
                                }}
                            />
                        )}
                        <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)', ml: 'auto' }}>
                            {articles.length} results
                        </Typography>
                    </Box>
                </Container>
            )}

            <Container maxWidth={false} sx={{
                py: 4,
                mt: '90px',
                '@media (max-width: 600px)': {
                    mt: '220px',
                    pt: 1,
                }
            }}>
                {/* Date Filter */}
                <Container maxWidth={false} sx={{ maxWidth: '1000px', margin: '0 auto', mb: 3 }}>
                    <DateFilter>
                        <Typography variant="subtitle1" sx={{ color: '#00eaff', fontWeight: 600, whiteSpace: 'nowrap' }}>
                            <CalendarTodayIcon fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
                            Filter by Date:
                        </Typography>
                        {isMobile ? (
                            <FormControl fullWidth size="small">
                                <InputLabel id="date-select-label">Select Date</InputLabel>
                                <Select
                                    labelId="date-select-label"
                                    value={selectedDate || ''}
                                    label="Select Date"
                                    onChange={e => handleDateChange(e.target.value)}
                                >
                                    {availableDates.map(date => (
                                        <MenuItem key={date} value={date}>
                                            {new Date(date).toLocaleDateString()}
                                        </MenuItem>
                                    ))}
                                </Select>
                            </FormControl>
                        ) : (
                            <Box sx={{ position: 'relative', flex: 1 }}>
                                <DateFilterContainer ref={dateFilterRef}>
                                    {availableDates.map((date) => (
                                        <DateButton
                                            key={date}
                                            selected={selectedDate === date}
                                            onClick={() => handleDateChange(date)}
                                        >
                                            {new Date(date).toLocaleDateString()}
                                        </DateButton>
                                    ))}
                                </DateFilterContainer>
                                {availableDates.length > 1 && (
                                    <>
                                        <IconButton
                                            onClick={() => scrollDateFilter('left')}
                                            sx={{
                                                position: 'absolute',
                                                left: -20,
                                                top: '50%',
                                                transform: 'translateY(-50%)',
                                                zIndex: 2,
                                                background: 'rgba(0, 234, 255, 0.1)',
                                                '&:hover': {
                                                    background: 'rgba(0, 234, 255, 0.2)',
                                                },
                                            }}
                                        >
                                            <ChevronLeft sx={{ color: '#00eaff' }} />
                                        </IconButton>
                                        <IconButton
                                            onClick={() => scrollDateFilter('right')}
                                            sx={{
                                                position: 'absolute',
                                                right: -20,
                                                top: '50%',
                                                transform: 'translateY(-50%)',
                                                zIndex: 2,
                                                background: 'rgba(0, 234, 255, 0.1)',
                                                '&:hover': {
                                                    background: 'rgba(0, 234, 255, 0.2)',
                                                },
                                            }}
                                        >
                                            <ChevronRight sx={{ color: '#00eaff' }} />
                                        </IconButton>
                                    </>
                                )}
                            </Box>
                        )}
                    </DateFilter>
                </Container>

                {/* Categories Section */}
                <Container maxWidth={false} sx={{ maxWidth: '1000px', margin: '0 auto', mb: 3 }}>
                    <CategoriesSection>
                        <Tabs
                            value={category}
                            onChange={handleCategoryChange}
                            variant="scrollable"
                            scrollButtons="auto"
                            sx={{
                                '& .MuiTabs-indicator': {
                                    backgroundColor: '#00eaff',
                                },
                                '& .MuiTab-root': {
                                    color: 'rgba(255, 255, 255, 0.7)',
                                    '&.Mui-selected': {
                                        color: '#00eaff',
                                    },
                                    transition: 'color 0.3s ease',
                                    '&:hover': {
                                        color: 'rgba(255, 255, 255, 0.7)', // Remove hover effect
                                        transform: 'none', // Remove transform effect
                                    },
                                },
                            }}
                        >
                            <Tab label="All" value="all" />
                            {Object.entries(fixedCategories).map(([key, value]) => (
                                <Tab key={key} label={value} value={key} />
                            ))}
                        </Tabs>
                    </CategoriesSection>
                </Container>

                {/* Carousel Section */}
                <Container maxWidth={false} sx={{ maxWidth: '1000px', margin: '0 auto', mb: 3 }}>
                    <CarouselContainer>
                        <Box sx={{ position: 'relative' }}>
                            <IconButton
                                onClick={() => scrollCarousel('left')}
                                sx={{
                                    position: 'absolute',
                                    left: -20,
                                    top: '50%',
                                    transform: 'translateY(-50%)',
                                    zIndex: 2,
                                    background: 'rgba(0, 234, 255, 0.1)',
                                    '&:hover': {
                                        background: 'rgba(0, 234, 255, 0.2)',
                                    },
                                }}
                            >
                                <ChevronLeft sx={{ color: '#00eaff' }} />
                            </IconButton>
                            <CarouselGrid ref={carouselRef}>
                                {articles.map((article) => (
                                    <NewsCard
                                        key={article.id}
                                        selected={selectedGroupId === article.group_id}
                                        onClick={() => handleArticleSelect(article)}
                                    >
                                        <CardMedia
                                            component="img"
                                            height="140"
                                            image={`${STATIC_URL}/images/${article.date}/${article.group_id}.jpg`}
                                            alt={article.headline}
                                            onError={(e) => {
                                                (e.target as HTMLImageElement).src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjE0MCIgdmlld0JveD0iMCAwIDMwMCAxNDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMTQwIiBmaWxsPSJyZ2JhKDEzLCAxMywgMTMsIDAuOCkiLz4KPHN2ZyB4PSI1MCUiIHk9IjUwJSIgd2lkdGg9IjQ4IiBoZWlnaHQ9IjQ4IiB2aWV3Qm94PSIwIDAgMjQgMjQiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzAwZWFmZiIgc3Ryb2tlLXdpZHRoPSIyIiB0cmFuc2Zvcm09InRyYW5zbGF0ZSgtMjQsIC0yNCkiPgo8cGF0aCBkPSJtMjEgMTktNS00LTE1IDEzdi0yaDEzeiIvPgo8Y2lyY2xlIGN4PSI5IiBjeT0iOSIgcj0iMiIvPgo8L3N2Zz4KPHRleHQgeD0iNTAlIiB5PSI3MCUiIGZpbGw9IiMwMGVhZmYiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxMiIgdGV4dC1hbmNob3I9Im1pZGRsZSI+SW1hZ2UgTm90IEZvdW5kPC90ZXh0Pgo8L3N2Zz4=';
                                            }}
                                            sx={{
                                                height: 140,
                                                objectFit: 'cover',
                                                borderBottom: '1px solid rgba(0, 234, 255, 0.2)',
                                            }}
                                        />
                                        <CardContent>
                                            <Typography
                                                gutterBottom
                                                variant="h6"
                                                component="h2"
                                                sx={{
                                                    fontSize: '1rem',
                                                    fontWeight: 600,
                                                    color: '#ffffff',
                                                    overflow: 'hidden',
                                                    textOverflow: 'ellipsis',
                                                    display: '-webkit-box',
                                                    WebkitLineClamp: 2,
                                                    WebkitBoxOrient: 'vertical',
                                                    mt: 2 // Add margin top to make space for AI label
                                                }}
                                            >
                                                {article.headline}
                                            </Typography>
                                            <Typography
                                                variant="body2"
                                                sx={{
                                                    color: 'rgba(255, 255, 255, 0.7)',
                                                    overflow: 'hidden',
                                                    textOverflow: 'ellipsis',
                                                    display: '-webkit-box',
                                                    WebkitLineClamp: 2,
                                                    WebkitBoxOrient: 'vertical',
                                                }}
                                            >
                                                {article.summary}
                                            </Typography>
                                        </CardContent>
                                    </NewsCard>
                                ))}
                            </CarouselGrid>
                            <IconButton
                                onClick={() => scrollCarousel('right')}
                                sx={{
                                    position: 'absolute',
                                    right: -20,
                                    top: '50%',
                                    transform: 'translateY(-50%)',
                                    zIndex: 2,
                                    background: 'rgba(0, 234, 255, 0.1)',
                                    '&:hover': {
                                        background: 'rgba(0, 234, 255, 0.2)',
                                    },
                                }}
                            >
                                <ChevronRight sx={{ color: '#00eaff' }} />
                            </IconButton>
                        </Box>
                    </CarouselContainer>
                </Container>

                {/* Main Content */}
                <MainContent>
                    {selectedArticle ? (
                        <Container maxWidth={false} sx={{ maxWidth: '1000px', margin: '0 auto' }}>
                            {/* Audio Player Bar */}
                            {selectedGroupId && selectedDate && (
                                <Box sx={{
                                    mb: 4,
                                    p: 2,
                                    background: 'rgba(0, 234, 255, 0.05)',
                                    borderRadius: 2,
                                    border: '1px solid rgba(0, 234, 255, 0.2)',
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 2,
                                    '@media (max-width: 768px)': {
                                        flexWrap: 'wrap',
                                        gap: 1,
                                        p: 1.5,
                                    },
                                }}>
                                    <audio
                                        ref={audioRef}
                                        src={`${API_URL}/static/audio/${selectedDate}/${selectedGroupId}.mp3`}
                                        onTimeUpdate={handleTimeUpdate}
                                        onLoadedMetadata={handleLoadedMetadata}
                                        onError={(e) => {
                                            console.error('Audio error:', e);
                                            setAudioError(true);
                                        }}
                                        onCanPlay={() => setAudioError(false)}
                                        onPlay={() => setIsPlaying(true)}
                                        onPause={() => setIsPlaying(false)}
                                        onEnded={() => { setIsPlaying(false); setCurrentTime(0); }}
                                        preload={isMobile ? "none" : "metadata"}
                                        playsInline
                                        crossOrigin="anonymous"
                                    />

                                    <IconButton
                                        onClick={handleClick}
                                        onTouchStart={handleTouchStart}
                                        onTouchEnd={handleTouchEnd}
                                        disabled={audioError || isProcessingAudio}
                                        title={
                                            isProcessingAudio ? "Processing..." :
                                                isMobile && !audioUnlocked ? "Tap to enable audio" :
                                                    isPlaying ? "Pause" : "Play"
                                        }
                                        sx={{
                                            color: audioError ? 'rgba(255, 255, 255, 0.3)' : '#00eaff',
                                            touchAction: 'manipulation', // Prevents double-tap zoom on iOS
                                            WebkitTouchCallout: 'none',
                                            WebkitUserSelect: 'none',
                                            userSelect: 'none',
                                            opacity: isProcessingAudio ? 0.7 : 1,
                                            transition: 'opacity 0.2s ease',
                                            '&:hover': {
                                                backgroundColor: audioError ? 'transparent' : 'rgba(0, 234, 255, 0.1)',
                                            },
                                        }}
                                    >
                                        {isProcessingAudio ? <VolumeUp /> : (isPlaying ? <Pause /> : <PlayArrow />)}
                                    </IconButton>

                                    <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', gap: 2 }}>
                                        <Typography variant="body2" sx={{ color: '#00eaff', minWidth: '40px' }}>
                                            {formatTime(currentTime)}
                                        </Typography>

                                        <Box sx={{ flex: 1, height: 4, backgroundColor: 'rgba(255, 255, 255, 0.1)', borderRadius: 2 }}>
                                            <Box
                                                sx={{
                                                    height: '100%',
                                                    backgroundColor: '#00eaff',
                                                    borderRadius: 2,
                                                    width: duration > 0 ? `${(currentTime / duration) * 100}%` : '0%',
                                                    transition: 'width 0.1s ease',
                                                }}
                                            />
                                        </Box>

                                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)', minWidth: '40px' }}>
                                            {formatTime(duration)}
                                        </Typography>
                                    </Box>

                                    <IconButton sx={{ color: isBookmarked ? '#ff6a00' : 'rgba(255, 255, 255, 0.5)' }}>
                                        <BookmarkBorder />
                                    </IconButton>

                                    {audioError && (
                                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.5)', fontStyle: 'italic' }}>
                                            Audio not available
                                        </Typography>
                                    )}
                                    {isMobile && !audioUnlocked && !audioError && !isProcessingAudio && (
                                        <Typography variant="body2" sx={{ color: '#00eaff', fontStyle: 'italic' }}>
                                            Tap play to enable audio
                                        </Typography>
                                    )}
                                    {isProcessingAudio && (
                                        <Typography variant="body2" sx={{ color: '#ff6a00', fontStyle: 'italic' }}>
                                            Processing audio...
                                        </Typography>
                                    )}
                                </Box>
                            )}

                            <Box sx={{
                                display: 'flex',
                                gap: 3,
                                '@media (max-width: 768px)': {
                                    flexDirection: 'column',
                                    gap: 2,
                                },
                            }}>
                                {/* Article Content - Full Width */}
                                <Box sx={{
                                    flex: 1,
                                    '@media (max-width: 768px)': {
                                        width: '100%',
                                    },
                                }}>
                                    {/* AI Generated Label for Article Detail */}

                                    <Typography variant="h3" sx={{
                                        color: '#00eaff',
                                        mb: 2,
                                        fontWeight: 700,
                                        '@media (max-width: 768px)': {
                                            fontSize: '1.8rem',
                                        },
                                        '@media (max-width: 480px)': {
                                            fontSize: '1.5rem',
                                        },
                                    }}>
                                        {selectedArticle.headline}
                                    </Typography>
                                    <Box sx={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: 1,
                                        mb: 2,
                                        p: 1,
                                        background: 'rgba(0, 234, 255, 0.05)',
                                        borderRadius: 1,
                                        border: '1px solid rgba(0, 234, 255, 0.2)',
                                        width: 'fit-content'
                                    }}>
                                        <SmartToy sx={{
                                            fontSize: '1rem',
                                            color: '#00eaff'
                                        }} />
                                        <Typography
                                            variant="body2"
                                            sx={{
                                                color: '#00eaff',
                                                fontWeight: 600,
                                            }}
                                        >
                                            AI Generated Content
                                        </Typography>
                                    </Box>
                                    <Typography variant="h5" sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 3, fontStyle: 'italic' }}>
                                        {selectedArticle.subheadline}
                                    </Typography>
                                    <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.9)', mb: 4, fontSize: '1.1rem', lineHeight: 1.7 }}>
                                        {selectedArticle.lead}
                                    </Typography>

                                    {/* Article Body Sections with Individual Analysis */}
                                    {selectedArticle.body.map((section, index) => (
                                        <Box key={index} sx={{ mb: 6 }}>
                                            {/* Section Title */}
                                            <Typography variant="h5" sx={{ color: '#00eaff', mb: 3, fontWeight: 600 }}>
                                                {section.section}
                                            </Typography>

                                            {/* Section Content and Analysis - Responsive Layout */}
                                            <Box sx={{
                                                display: 'flex',
                                                gap: 3,
                                                alignItems: 'flex-start',
                                                '@media (max-width: 768px)': {
                                                    flexDirection: 'column',
                                                    gap: 2,
                                                },
                                            }}>
                                                {/* Section Content */}
                                                <Box sx={{
                                                    width: '600px',
                                                    minWidth: '600px',
                                                    maxWidth: '600px',
                                                    '@media (max-width: 1000px)': {
                                                        width: '100%',
                                                        minWidth: 0,
                                                        maxWidth: '100%',
                                                    },
                                                }}>
                                                    <Box sx={{
                                                        p: 3,
                                                        background: 'rgba(0, 234, 255, 0.05)',
                                                        borderRadius: 2,
                                                        border: '1px solid rgba(0, 234, 255, 0.1)',
                                                        minHeight: '200px',
                                                        '@media (max-width: 768px)': {
                                                            p: 2,
                                                            minHeight: 'auto',
                                                        },
                                                    }}>
                                                        <Typography
                                                            variant="body1"
                                                            sx={{
                                                                color: 'rgba(255, 255, 255, 0.9)',
                                                                lineHeight: 1.7,
                                                                mb: 2,
                                                                '@media (max-width: 768px)': {
                                                                    fontSize: '0.95rem',
                                                                },
                                                            }}
                                                            dangerouslySetInnerHTML={{
                                                                __html: renderContentWithSources(section.content, section.sources)
                                                            }}
                                                        />
                                                        {renderSourcesList(section.sources)}
                                                    </Box>
                                                </Box>

                                                {/* Individual Analysis Box - Moves to bottom on mobile */}
                                                <Box sx={{
                                                    width: '350px',
                                                    minWidth: '350px',
                                                    maxWidth: '350px',
                                                    '@media (max-width: 1000px)': {
                                                        width: '100%',
                                                        minWidth: 0,
                                                        maxWidth: '100%',
                                                    },
                                                }}>
                                                    <Box sx={{
                                                        p: 2.5,
                                                        background: 'rgba(13, 13, 13, 0.9)',
                                                        borderRadius: 2,
                                                        border: '1px solid rgba(0, 234, 255, 0.3)',
                                                        boxShadow: '0 4px 20px rgba(0, 234, 255, 0.1)',
                                                        backdropFilter: 'blur(10px)',
                                                        minHeight: '200px',
                                                        '@media (max-width: 768px)': {
                                                            p: 2,
                                                            minHeight: 'auto',
                                                            marginTop: 2,
                                                        },
                                                    }}>

                                                        {/* Sentiment Score */}
                                                        <Box sx={{ mb: 2.5 }}>
                                                            <Typography variant="subtitle2" sx={{ color: '#00eaff', mb: 1, fontSize: '0.9rem' }}>
                                                                Sentiment Score
                                                            </Typography>
                                                            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 1 }}>
                                                                {section.sentisement_from_the_content || 'N/A'}
                                                            </Typography>
                                                            <Box sx={{
                                                                height: 6,
                                                                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                                                borderRadius: 3,
                                                                overflow: 'hidden'
                                                            }}>
                                                                <Box sx={{
                                                                    height: '100%',
                                                                    backgroundColor: parseFloat(section.sentisement_from_the_content || '0') >= 0 ? '#4caf50' : '#f44336',
                                                                    width: `${Math.abs(parseFloat(section.sentisement_from_the_content || '0')) * 100}%`,
                                                                    borderRadius: 3,
                                                                    transition: 'width 0.5s ease'
                                                                }} />
                                                            </Box>
                                                        </Box>

                                                        {/* Reliability Score */}
                                                        <Box sx={{ mb: 2.5 }}>
                                                            <Typography variant="subtitle2" sx={{ color: '#00eaff', mb: 1, fontSize: '0.9rem' }}>
                                                                Reliability Score
                                                            </Typography>
                                                            <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 1 }}>
                                                                {(1 - (section.fake_news_probability || 0)).toFixed(2)} ({((1 - (section.fake_news_probability || 0)) * 100).toFixed(0)}%)
                                                            </Typography>
                                                            <Box sx={{
                                                                height: 6,
                                                                backgroundColor: 'rgba(255, 255, 255, 0.1)',
                                                                borderRadius: 3,
                                                                overflow: 'hidden'
                                                            }}>
                                                                <Box sx={{
                                                                    height: '100%',
                                                                    backgroundColor: '#00eaff',
                                                                    width: `${(1 - (section.fake_news_probability || 0)) * 100}%`,
                                                                    borderRadius: 3,
                                                                    transition: 'width 0.5s ease'
                                                                }} />
                                                            </Box>
                                                        </Box>

                                                        {/* Publishers */}
                                                        <Box sx={{ mb: 2.5 }}>
                                                            <Typography variant="subtitle2" sx={{ color: '#00eaff', mb: 1, fontSize: '0.9rem' }}>
                                                                Publishers
                                                            </Typography>
                                                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                                                {section.Publishers?.map((publisher, idx) => (
                                                                    <Chip
                                                                        key={idx}
                                                                        label={publisher}
                                                                        size="small"
                                                                        sx={{
                                                                            backgroundColor: 'rgba(0, 234, 255, 0.1)',
                                                                            color: '#00eaff',
                                                                            border: '1px solid rgba(0, 234, 255, 0.3)',
                                                                            fontSize: '0.75rem',
                                                                            height: '24px'
                                                                        }}
                                                                    />
                                                                )) || (
                                                                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>
                                                                            N/A
                                                                        </Typography>
                                                                    )}
                                                            </Box>
                                                        </Box>

                                                        {/* Source Regions */}
                                                        <Box sx={{ mb: 2 }}>
                                                            <Typography variant="subtitle2" sx={{ color: '#00eaff', mb: 1, fontSize: '0.9rem' }}>
                                                                Source Regions
                                                            </Typography>
                                                            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                                                                {section.Publisher_region_diversity?.map((region, idx) => (
                                                                    <Chip
                                                                        key={idx}
                                                                        label={region.toUpperCase()}
                                                                        size="small"
                                                                        sx={{
                                                                            backgroundColor: 'rgba(255, 106, 0, 0.1)',
                                                                            color: '#ff6a00',
                                                                            border: '1px solid rgba(255, 106, 0, 0.3)',
                                                                            fontSize: '0.75rem',
                                                                            height: '24px'
                                                                        }}
                                                                    />
                                                                )) || (
                                                                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.85rem' }}>
                                                                            N/A
                                                                        </Typography>
                                                                    )}
                                                            </Box>
                                                        </Box>

                                                        {/* Publication Date */}
                                                        <Box sx={{ mt: 'auto', pt: 1, borderTop: '1px solid rgba(0, 234, 255, 0.1)' }}>
                                                            <Typography variant="caption" sx={{ color: 'rgba(255, 255, 255, 0.6)', fontSize: '0.75rem' }}>
                                                                Published: {section.date || 'Unknown'}
                                                            </Typography>
                                                        </Box>
                                                    </Box>
                                                </Box>
                                            </Box>
                                        </Box>
                                    ))}

                                    {/* Conclusion */}
                                    <Box sx={{ mt: 6, p: 4, background: 'rgba(255, 106, 0, 0.05)', borderRadius: 2, border: '1px solid rgba(255, 106, 0, 0.2)' }}>
                                        <Typography variant="h6" sx={{ color: '#ff6a00', mb: 2, fontWeight: 600 }}>
                                            Conclusion
                                        </Typography>
                                        <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.9)', lineHeight: 1.7 }}>
                                            {selectedArticle.conclusion}
                                        </Typography>
                                    </Box>

                                    {/* Timeline Section */}
                                    {selectedArticle.timeline && Object.keys(selectedArticle.timeline).length > 0 && (
                                        <Box sx={{ mt: 6, p: 4, background: 'rgba(138, 43, 226, 0.05)', borderRadius: 2, border: '1px solid rgba(138, 43, 226, 0.2)' }}>
                                            <Typography variant="h6" sx={{ color: '#8a2be2', mb: 3, fontWeight: 600 }}>
                                                Timeline
                                            </Typography>
                                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                                                {Object.entries(selectedArticle.timeline).map(([time, event], index) => (
                                                    <Box key={index} sx={{
                                                        p: 3,
                                                        background: 'rgba(138, 43, 226, 0.1)',
                                                        borderRadius: 2,
                                                        border: '1px solid rgba(138, 43, 226, 0.2)',
                                                        borderLeft: '4px solid #8a2be2'
                                                    }}>
                                                        <Typography variant="subtitle2" sx={{ color: '#8a2be2', mb: 1, fontWeight: 600 }}>
                                                            {new Date(time).toLocaleString()}
                                                        </Typography>
                                                        <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.9)', lineHeight: 1.6 }}>
                                                            {event}
                                                        </Typography>
                                                    </Box>
                                                ))}
                                            </Box>
                                        </Box>
                                    )}
                                </Box>
                            </Box>
                        </Container>
                    ) : (
                        <Container maxWidth={false} sx={{ maxWidth: '1000px', margin: '0 auto' }}>
                            <Box sx={{ textAlign: 'center', py: 8 }}>
                                <Typography variant="h4" sx={{ color: '#00eaff', mb: 2 }}>
                                    Select an article to read
                                </Typography>
                                <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                                    Choose any article from the carousel above to view its full content
                                </Typography>
                            </Box>
                        </Container>
                    )}
                </MainContent>
            </Container>

            {/* Chat Bot */}
            <ChatContainer
                className={isChatMinimized ? 'minimized' : ''}
                fullscreen={isChatFullscreen}
            >
                {isChatMinimized ? (
                    <ChatIcon onClick={toggleChat}>
                        <SmartToy sx={{
                            fontSize: { xs: '24px', sm: '24px', md: '28px', lg: '32px' }
                        }} />
                    </ChatIcon>
                ) : (
                    <Box sx={{
                        width: isChatFullscreen ? 'auto' : '400px',
                        height: isChatFullscreen ? 'auto' : '500px',
                        display: 'flex',
                        flexDirection: 'column',
                        position: 'relative',
                        overflow: isChatFullscreen ? 'visible' : 'hidden',
                        // Mobile responsive
                        '@media (max-width: 768px)': {
                            width: isChatFullscreen ? 'auto' : '100%',
                            height: isChatFullscreen ? 'auto' : '100%',
                        },
                    }}>
                        <Box sx={{
                            p: 2,
                            borderBottom: '1px solid rgba(0, 234, 255, 0.2)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            background: 'rgba(0, 234, 255, 0.05)',
                            flexShrink: 0, // Prevent header from shrinking
                            minHeight: '60px', // Ensure minimum height
                            // Mobile responsive
                            '@media (max-width: 768px)': {
                                p: 1.5,
                                minHeight: '56px',
                            },
                            '@media (max-width: 480px)': {
                                p: 1,
                                minHeight: '52px',
                            },
                        }}>
                            <Box sx={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: 1,
                                minWidth: 0, // Allow text to shrink
                                flex: 1,
                            }}>
                                <SmartToy sx={{
                                    color: '#00eaff',
                                    fontSize: '24px',
                                    flexShrink: 0,
                                    // Mobile responsive
                                    '@media (max-width: 480px)': {
                                        fontSize: '20px',
                                    },
                                }} />
                                <Typography variant="h6" sx={{
                                    color: '#00eaff',
                                    fontWeight: 600,
                                    overflow: 'hidden',
                                    textOverflow: 'ellipsis',
                                    whiteSpace: 'nowrap',
                                    // Mobile responsive
                                    '@media (max-width: 480px)': {
                                        fontSize: '1rem',
                                    },
                                    '@media (max-width: 360px)': {
                                        fontSize: '0.9rem',
                                    },
                                }}>
                                    AI Assistant
                                </Typography>
                            </Box>
                            <ChatToggleButton
                                onClick={toggleChat}
                                size="small"
                                sx={{
                                    flexShrink: 0,
                                    // Mobile responsive
                                    '@media (max-width: 480px)': {
                                        width: '32px',
                                        height: '32px',
                                    },
                                }}
                            >
                                <Remove sx={{
                                    '@media (max-width: 480px)': {
                                        fontSize: '1rem',
                                    },
                                }} />
                            </ChatToggleButton>
                        </Box>
                        <Box sx={{
                            flex: 1,
                            overflow: 'hidden',
                            minHeight: 0, // Important for flex child with overflow
                        }}>
                            <ChatBot
                                currentGroupId={selectedGroupId || ''}
                                currentDate={selectedDate}
                                onFullscreenChange={handleChatFullscreenChange}
                            />
                        </Box>
                    </Box>
                )}
            </ChatContainer>

            {/* Particle Overlay */}
            <ParticleOverlay />

            {/* Enhanced Footer */}
            <FooterSection>
                <Container maxWidth={false} sx={{ maxWidth: '1000px', margin: '0 auto' }}>
                    <Box sx={{ textAlign: 'center', mb: 4 }}>
                        <Typography variant="h4" sx={{
                            color: '#00eaff',
                            mb: 2,
                            fontWeight: 700,
                            background: 'linear-gradient(45deg, #00eaff, #ff6a00)',
                            backgroundClip: 'text',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            animation: 'logoGradient 4s ease-in-out infinite',
                        }}>
                            AI News Sense
                        </Typography>
                        <Typography variant="subtitle1" sx={{
                            color: 'rgba(255, 255, 255, 0.8)',
                            mb: 3,
                            fontFamily: '"Orbitron", monospace',
                            letterSpacing: '1px'
                        }}>
                            Next-Generation Intelligence • Real-Time Analysis • Future Today
                        </Typography>

                        <Typography className="footer-text" variant="body2" sx={{
                            color: 'rgba(255, 255, 255, 0.6)',
                            fontSize: '0.9rem',
                            fontWeight: 300,
                            letterSpacing: '1px',
                            fontFamily: '"Orbitron", monospace',
                            background: 'linear-gradient(45deg, #00eaff, #ff6a00, #8a2be2)',
                            backgroundClip: 'text',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            animation: 'logoGradient 6s ease-in-out infinite',
                            '&::before': {
                                content: '"// "',
                                color: 'rgba(0, 234, 255, 0.5)',
                            },
                        }}>
                            Made by HKU msp24053 • Built for the Future • &copy; 2025 AI News Sense
                        </Typography>
                    </Box>
                </Container>
            </FooterSection>

            {/* Video Modal */}
            <Modal
                open={isVideoModalOpen}
                onClose={() => setIsVideoModalOpen(false)}
                closeAfterTransition
                BackdropComponent={Backdrop}
                BackdropProps={{
                    timeout: 500,
                    sx: {
                        backgroundColor: 'rgba(0, 0, 0, 0.9)',
                        backdropFilter: 'blur(10px)',
                    },
                }}
            >
                <Box
                    sx={{
                        position: 'absolute',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        width: '90vw',
                        maxWidth: '1200px',
                        height: '90vh',
                        maxHeight: '800px',
                        background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.95) 0%, rgba(26, 26, 46, 0.95) 100%)',
                        borderRadius: '16px',
                        border: '2px solid rgba(0, 234, 255, 0.3)',
                        boxShadow: '0 20px 60px rgba(0, 234, 255, 0.2)',
                        backdropFilter: 'blur(20px)',
                        display: 'flex',
                        flexDirection: 'column',
                        overflow: 'hidden',
                        '@media (max-width: 768px)': {
                            width: '95vw',
                            height: '95vh',
                        },
                    }}
                >
                    {/* Modal Header with Config Date */}
                    <Box
                        sx={{
                            p: 2,
                            borderBottom: '1px solid rgba(0, 234, 255, 0.2)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            background: 'rgba(0, 234, 255, 0.05)',
                        }}
                    >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <VideoLibrary sx={{ color: '#00eaff', fontSize: '24px' }} />
                            <Typography variant="h6" sx={{ color: '#00eaff', fontWeight: 600 }}>
                                AI News Summary Video{summaryDate ? ` - ${new Date(summaryDate).toLocaleDateString()}` : ''}
                            </Typography>
                        </Box>
                        <IconButton
                            onClick={() => setIsVideoModalOpen(false)}
                            sx={{
                                color: 'rgba(255, 255, 255, 0.7)',
                                '&:hover': {
                                    color: '#00eaff',
                                    backgroundColor: 'rgba(0, 234, 255, 0.1)',
                                },
                            }}
                        >
                            <Close />
                        </IconButton>
                    </Box>

                    {/* Video Player using Config Date */}
                    <Box
                        sx={{
                            flex: 1,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            p: 2,
                            background: 'rgba(0, 0, 0, 0.3)',
                        }}
                    >
                        <video
                            ref={videoRef}
                            controls
                            autoPlay
                            style={{
                                width: '100%',
                                height: '100%',
                                borderRadius: '8px',
                                objectFit: 'contain',
                            }}
                            onError={(e) => {
                                console.error('Video error:', e);
                            }}
                        >
                            <source
                                src={summaryDate
                                    ? `${STATIC_URL}/summary-video/${summaryDate}/summary.mp4`
                                    : `${STATIC_URL}/summary-video/summary.mp4`
                                }
                                type="video/mp4"
                            />
                            Your browser does not support the video tag.
                        </video>
                    </Box>


                </Box>
            </Modal>
        </Box>
    );
};

export default NewsPortal;                             