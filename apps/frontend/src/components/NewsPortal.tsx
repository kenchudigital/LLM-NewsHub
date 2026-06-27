import config from '../config';
import React, { useState, useEffect, useRef, useCallback } from 'react';
import type { NewsArticle, ArticleData } from './NewsPortal/types';
import {
    Box,
    Container,
    Typography,
    Chip,
    IconButton,
    Button,
    Card,
    CardContent,
    CardMedia,
    Tooltip,
    Tabs,
    Tab,
    TextField,
    InputAdornment,
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
    BookmarkBorder,
    Search as SearchIcon,
    ChevronLeft,
    ChevronRight,
    Close,
    SmartToy,
    Remove,
    CalendarToday as CalendarTodayIcon,
    VideoLibrary,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import axios from 'axios';
import ChatBot from './ChatBot';
// import { useNavigate } from 'react-router-dom'; // Not needed anymore

// Styled components with animations
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

const NewsPortal: React.FC = () => {
    // const navigate = useNavigate(); // Not needed anymore
    // States
    const [articles, setArticles] = useState<NewsArticle[]>([]);
    const [selectedArticle, setSelectedArticle] = useState<ArticleData | null>(null);
    const [selectedDate, setSelectedDate] = useState<string>('');
    const [selectedGroupId, setSelectedGroupId] = useState<string | null>(null);
    const [category, setCategory] = useState('all');
    const [search, setSearch] = useState('');
    const [fuzzySearch, setFuzzySearch] = useState(false);
    const [isChatMinimized, setIsChatMinimized] = useState(true);
    const [isChatFullscreen, setIsChatFullscreen] = useState(false);
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

    const [summaryDate, setSummaryDate] = useState<string>('');

    const audioRef = useRef<HTMLAudioElement>(null);
    const videoRef = useRef<HTMLVideoElement>(null);
    const carouselRef = useRef<HTMLDivElement>(null);
    const dateFilterRef = useRef<HTMLDivElement>(null);

    const [isMobile, setIsMobile] = useState(window.innerWidth <= 600);

    // Prevent double-triggering on mobile
    const lastActionTime = useRef<number>(0);
    const touchStartTime = useRef<number>(0);

    useEffect(() => {
        const handleResize = () => setIsMobile(window.innerWidth <= 600);
        const checkMobile = () => {
            const userAgent = navigator.userAgent || navigator.vendor || (window as any).opera;
            const mobile = /android|blackberry|iemobile|ipad|iphone|ipod|opera mini|webos/i.test(userAgent.toLowerCase());
            setIsMobile(mobile);
        };

        checkMobile();
        window.addEventListener('resize', handleResize);
        return () => window.removeEventListener('resize', handleResize);
    }, []);

    const API_URL = config.API_URL;
    const STATIC_URL = config.STATIC_URL;

    const fixedCategories = {
        social: 'Social',
        tech: 'Technology',
        entertainment: 'Entertainment'
    };

    const fetchConfig = useCallback(async () => {
        try {
            const response = await axios.get(`${API_URL}/api/config/summary-date`);
            setSummaryDate(response.data.date);
        } catch (error) {
            console.error('Error fetching config:', error);
            setSummaryDate('2025-07-12');
        }
    }, [API_URL]);

    const fetchDates = useCallback(async () => {
        try {
            const response = await axios.get(`${API_URL}/api/news/dates`);
            setAvailableDates(response.data.dates || []);
        } catch (error) {
            console.error('Error fetching dates:', error);
            setAvailableDates(['2025-06-14']);
        }
    }, [API_URL]);

    const fetchArticles = useCallback(async () => {
        try {
            const response = await axios.get(`${API_URL}/api/news`, {
                params: {
                    category: category !== 'all' ? category : undefined,
                    search: search || undefined,
                    date: selectedDate || undefined,
                    fuzzy: fuzzySearch
                }
            });

            let articlesData;
            if (response.data && response.data.news) {
                articlesData = response.data.news;
            } else if (Array.isArray(response.data)) {
                articlesData = response.data;
            } else {
                articlesData = [];
            }

            setArticles(articlesData);
        } catch (error) {
            console.error('Error fetching articles:', error);
            setArticles([]);
        }
    }, [API_URL, category, search, selectedDate, fuzzySearch]);

    const fetchArticleDetail = useCallback(async (groupId: string, date: string) => {
        try {
            const url = `${API_URL}/api/news/articles/${date}/${groupId}`;
            const response = await axios.get(url);
            setSelectedArticle(response.data);
        } catch (error: any) {
            console.error('Error fetching article detail:', error);
            console.error('Error details:', {
                message: error?.message || 'Unknown error',
                status: error?.response?.status,
                statusText: error?.response?.statusText,
                data: error?.response?.data
            });
        }
    }, [API_URL]);

    const handleArticleSelect = useCallback((article: NewsArticle) => {
        setSelectedGroupId(article.group_id);
        if (!selectedDate) {
            setSelectedDate(article.date);
        }

        fetchArticleDetail(article.group_id, article.date);

        setIsPlaying(false);
        setCurrentTime(0);
        setAudioError(false);
        setAudioUnlocked(false);

        const audioUrl = `${STATIC_URL}/audio/${article.date}/${article.group_id}.mp3`;
        fetch(audioUrl, {
            method: 'GET',
            headers: {
                'Range': 'bytes=0-1'
            }
        })
            .then(response => {
                if (response.ok || response.status === 206) {
                    setAudioError(false);
                } else {
                    setAudioError(true);
                }
            })
            .catch(error => {
                console.warn('NewsPortal: Audio availability check failed:', error);
            });
    }, [selectedDate, fetchArticleDetail, STATIC_URL]);

    useEffect(() => {
        const fetchData = async () => {
            try {
                await Promise.all([
                    fetchArticles(),
                    fetchDates(),
                    fetchConfig()
                ]);
            } catch (error) {
                console.error('Error fetching data:', error);
            }
        };
        fetchData();
    }, [fetchArticles, fetchDates, fetchConfig]);

    useEffect(() => {
        if (articles.length > 0 && !selectedGroupId && !selectedArticle && !selectedDate) {
            handleArticleSelect(articles[0]);
        }
    }, [articles, selectedGroupId, selectedArticle, selectedDate, handleArticleSelect]);

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
                        await audioContext.resume();
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
            return;
        }
        lastActionTime.current = now;

        if (!audioRef.current || audioError || !selectedGroupId || isProcessingAudio) return;

        setIsProcessingAudio(true);

        try {
            // On mobile, first interaction needs to unlock audio
            if (isMobile && !audioUnlocked) {
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
            } else {
                // On iOS, ensure the audio element is ready
                if (isMobile) {
                    // Load the audio if it's not already loaded
                    if (audioRef.current.readyState < 2) {
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
                const regex = new RegExp(pattern.replace(/[[\]]/g, '\\$&'), 'g');
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

    // Mobile touch event handlers for NewsPortal
    const handleTouchStart = (event: React.TouchEvent) => {
        touchStartTime.current = Date.now();
    };

    const handleTouchEnd = (event: React.TouchEvent) => {
        const touchDuration = Date.now() - touchStartTime.current;

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

                                    <IconButton
                                        onClick={() => setIsBookmarked(!isBookmarked)}
                                        sx={{ color: isBookmarked ? '#ff6a00' : 'rgba(255, 255, 255, 0.5)' }}
                                    >
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
                            Made by the LLM-NewsHub Project Team • Built for the Future • &copy; 2025 AI News Sense
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