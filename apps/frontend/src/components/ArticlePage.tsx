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
    LinearProgress,
    Tooltip,
    Grid,
    Avatar,
    Collapse,
    Fade,
    Zoom,
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
    Business,
    ExpandMore,
    ExpandLess,
    Info,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { useParams } from 'react-router-dom';
import axios from 'axios';

// Add version constant at the top
const APP_VERSION = '1.0.0';

// Styled components following the demo design
const ArticleContainer = styled(Paper)(({ theme }) => ({
    maxWidth: '1600px',
    margin: '2rem auto',
    padding: '2rem',
    borderRadius: '12px',
    boxShadow: '0 5px 15px rgba(0, 0, 0, 0.1)',
    background: 'white',
    width: '100%',
}));

const AudioBar = styled(Paper)(({ theme }) => ({
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
    transition: 'background 0.3s',
    '&:hover': {
        background: 'rgba(255, 106, 0, 0.08)',
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
    boxShadow: '0 1px 6px 0 #00eaff33',
}));

const PlayPauseButton = styled(IconButton, {
    shouldForwardProp: (prop) => prop !== 'isplaying',
})<{ isplaying: boolean }>(({ isplaying }) => ({
    color: 'white',
    background: isplaying ? 'linear-gradient(90deg, #ff6a00 0%, #00eaff 100%)' : 'rgba(255,255,255,0.1)',
    boxShadow: isplaying ? '0 0 0 6px #ff6a0033' : 'none',
    animation: isplaying ? 'pulsePlay 1.2s infinite' : 'none',
    transition: 'background 0.3s, box-shadow 0.3s, transform 0.2s',
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

const ArticleTitle = styled(Typography)(({ theme }) => ({
    fontSize: '2.5rem',
    fontWeight: 700,
    color: '#1d3557',
    marginBottom: '1rem',
    lineHeight: 1.3,
    [theme.breakpoints.down('md')]: {
        fontSize: '2rem',
    },
}));

const LeadParagraph = styled(Typography)(({ theme }) => ({
    fontSize: '1.25rem',
    fontWeight: 500,
    color: '#333',
    marginBottom: '2rem',
    lineHeight: 1.6,
    padding: '1.5rem',
    background: '#f8f9fa',
    borderLeft: '4px solid #e63946',
    borderRadius: '0 8px 8px 0',
}));

const SectionTitle = styled(Typography)(({ theme }) => ({
    fontSize: '1.5rem',
    fontWeight: 600,
    color: '#1d3557',
    marginTop: '2rem',
    marginBottom: '1rem',
}));

const BodyContent = styled(Box)(({ theme }) => ({
    fontSize: '1.1rem',
    lineHeight: 1.8,
    color: '#444',
    '& p': {
        marginBottom: '1.5rem',
    },
}));

const SourceLink = styled(Link)(({ theme }) => ({
    color: '#e63946',
    textDecoration: 'none',
    fontWeight: 500,
    cursor: 'pointer',
    padding: '2px 6px',
    borderRadius: '4px',
    border: '1px solid transparent',
    transition: 'all 0.3s ease',
    display: 'inline-block',
    '&:hover': {
        textDecoration: 'none',
        backgroundColor: '#e63946',
        color: 'white',
        borderColor: '#e63946',
        transform: 'translateY(-1px)',
        boxShadow: '0 2px 8px rgba(230, 57, 70, 0.3)',
    },
    '&::before': {
        content: '"["',
        fontWeight: 'bold',
    },
    '&::after': {
        content: '"]"',
        fontWeight: 'bold',
    },
}));


const MetaToggle = styled(IconButton)(({ theme }) => ({
    position: 'absolute',
    right: '8px',
    top: '8px',
    color: 'rgba(0, 234, 255, 0.8)',
    padding: '4px',
    transition: 'all 0.3s ease',
    '&:hover': {
        color: '#00eaff',
        transform: 'scale(1.1)',
    }
}));

const MetaInfo = styled(Paper)(({ theme }) => ({
    position: 'relative',
    marginBottom: '2rem',
    padding: '0.5rem',
    background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.95) 0%, rgba(26, 26, 46, 0.9) 100%)',
    borderRadius: '12px',
    border: '1px solid rgba(0, 234, 255, 0.2)',
    boxShadow: '0 4px 20px rgba(0, 234, 255, 0.1)',
    overflow: 'hidden',
    transition: 'all 0.3s ease',
    maxWidth: '100%', // Add this
    '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '2px',
        background: 'linear-gradient(90deg, transparent, rgba(0, 234, 255, 0.5), transparent)',
    }
}));

const MetaContent = styled(Box, {
    shouldForwardProp: (prop) => prop !== 'expanded',
})<{ expanded: boolean }>(({ theme, expanded }) => ({
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    gap: '0.75rem',
    padding: '0.5rem',
    transition: 'all 0.3s ease',
    overflowX: 'auto',
    whiteSpace: 'nowrap',
    width: '100%',
    maxWidth: '100%',
    minHeight: expanded ? 'auto' : '0',
    '&::-webkit-scrollbar': {
        height: '4px',
    },
    '&::-webkit-scrollbar-track': {
        background: 'rgba(0, 234, 255, 0.1)',
        borderRadius: '2px',
    },
    '&::-webkit-scrollbar-thumb': {
        background: 'rgba(0, 234, 255, 0.3)',
        borderRadius: '2px',
        '&:hover': {
            background: 'rgba(0, 234, 255, 0.5)',
        },
    },
    '& > *': {
        flexShrink: 0,
        flex: '0 0 auto', // Ensure items don't grow
    }
}));

const MetaItem = styled(Box)(({ theme }) => ({
    display: 'inline-flex',
    alignItems: 'center',
    gap: '0.5rem',
    padding: '0.5rem 1rem',
    background: 'rgba(0, 234, 255, 0.1)',
    borderRadius: '20px',
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: '0.9rem',
    border: '1px solid rgba(0, 234, 255, 0.2)',
    transition: 'all 0.3s ease',
    '&:hover': {
        background: 'rgba(0, 234, 255, 0.15)',
        borderColor: 'rgba(0, 234, 255, 0.3)',
    },
    '& svg': {
        color: '#00eaff',
    }
}));

const SentimentIndicator = styled(Box)<{ sentiment: number }>(({ theme, sentiment }) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    padding: '0.5rem 1rem',
    borderRadius: '20px',
    fontSize: '0.9rem',
    fontWeight: 500,
    background: sentiment > 0 ? '#d4edda' : sentiment < -0.5 ? '#f8d7da' : '#fff3cd',
    color: sentiment > 0 ? '#155724' : sentiment < -0.5 ? '#721c24' : '#856404',
}));

const FakeNewsIndicator = styled(Box)<{ probability: number }>(({ theme, probability }) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '0.5rem',
    padding: '0.5rem 1rem',
    borderRadius: '20px',
    fontSize: '0.9rem',
    fontWeight: 500,
    background: probability > 0.7 ? '#f8d7da' : probability > 0.4 ? '#fff3cd' : '#d4edda',
    color: probability > 0.7 ? '#721c24' : probability > 0.4 ? '#856404' : '#155724',
}));

const SectionContainer = styled(Box)(({ theme }) => ({
    display: 'flex',
    gap: '2rem',
    marginBottom: '2rem',
    position: 'relative',
    width: '100%',
    [theme.breakpoints.down('lg')]: {
        flexDirection: 'column',
        '& > *:last-child': {
            width: '100%',
            position: 'static',
        }
    }
}));

const SectionContent = styled(Box)(({ theme }) => ({
    flex: 1,
    minWidth: 0,
    maxWidth: 'calc(100% - 300px)',
    [theme.breakpoints.down('lg')]: {
        maxWidth: '100%',
    }
}));

const SectionSidebar = styled(Box)(({ theme }) => ({
    width: '280px',
    flexShrink: 0,
    padding: '1rem',
    background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.95) 0%, rgba(26, 26, 46, 0.9) 100%)',
    borderRadius: '12px',
    border: '1px solid rgba(0, 234, 255, 0.2)',
    boxShadow: '0 4px 20px rgba(0, 234, 255, 0.1)',
    height: 'fit-content',
    position: 'sticky',
    top: '100px',
    zIndex: 2,
    [theme.breakpoints.down('lg')]: {
        width: '100%',
        position: 'static',
        marginTop: '1rem',
    }
}));

const SidebarItem = styled(Box)(({ theme }) => ({
    display: 'flex',
    alignItems: 'center',
    gap: '0.75rem',
    padding: '0.75rem',
    marginBottom: '0.75rem',
    background: 'rgba(0, 234, 255, 0.1)',
    borderRadius: '8px',
    color: 'rgba(255, 255, 255, 0.9)',
    fontSize: '0.9rem',
    border: '1px solid rgba(0, 234, 255, 0.2)',
    '&:last-child': {
        marginBottom: 0,
    },
    '& svg': {
        color: '#00eaff',
    }
}));

// Update ArticleHeader styled component
const ArticleHeader = styled(Box)(({ theme }) => ({
    display: 'flex',
    gap: '2rem',
    marginBottom: '2rem',
    position: 'relative',
    width: '100%',
    [theme.breakpoints.down('lg')]: {
        flexDirection: 'column',
    }
}));

const ArticleMainContent = styled(Box)(({ theme }) => ({
    flex: 1,
    minWidth: 0,
    maxWidth: 'calc(100% - 340px)',
    [theme.breakpoints.down('lg')]: {
        maxWidth: '100%',
    }
}));

// Update ArticleSidebar styled component
const ArticleSidebar = styled(Box)(({ theme }) => ({
    width: '320px',
    flexShrink: 0,
    padding: '1.5rem',
    background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.95) 0%, rgba(26, 26, 46, 0.9) 100%)',
    borderRadius: '12px',
    border: '1px solid rgba(0, 234, 255, 0.2)',
    boxShadow: '0 4px 20px rgba(0, 234, 255, 0.1)',
    height: 'fit-content',
    position: 'sticky',
    top: '100px',
    zIndex: 2,
    [theme.breakpoints.down('lg')]: {
        width: '100%',
        position: 'static',
        marginTop: '1rem',
    }
}));

// Add VersionDisplay styled component
const VersionDisplay = styled(Box)(({ theme }) => ({
    position: 'absolute',
    top: '-30px',
    right: '0',
    fontSize: '0.8rem',
    color: 'rgba(255, 255, 255, 0.6)',
    padding: '4px 8px',
    background: 'rgba(0, 234, 255, 0.1)',
    borderRadius: '4px',
    border: '1px solid rgba(0, 234, 255, 0.2)',
}));

interface ArticleData {
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
    cover_image_prompt: string;
    summary_speech: string;
}

const ArticlePage: React.FC = () => {

    const { groupId, date } = useParams<{ groupId: string; date: string }>();
    const [article, setArticle] = useState<ArticleData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [isBookmarked, setIsBookmarked] = useState(false);
    const [sourceRefs, setSourceRefs] = useState<Record<string, number>>({});
    const audioRef = useRef<HTMLAudioElement>(null);
    const [audioAvailable, setAudioAvailable] = useState(true);
    const [audioError, setAudioError] = useState(false);
    const [expandedMeta, setExpandedMeta] = useState(false);
    const [audioUnlocked, setAudioUnlocked] = useState(false);
    const [isMobile, setIsMobile] = useState(false);
    const [isProcessingAudio, setIsProcessingAudio] = useState(false);
    const API_URL = config.API_URL || 'http://localhost:8000';
    const STATIC_URL = `${API_URL}/static`;

    // Prevent double-triggering on mobile
    const lastActionTime = useRef<number>(0);
    const touchStartTime = useRef<number>(0);

    // Detect mobile device
    useEffect(() => {
        const checkMobile = () => {
            const userAgent = navigator.userAgent || navigator.vendor || (window as any).opera;
            const mobile = /android|blackberry|iemobile|ipad|iphone|ipod|opera mini|webos/i.test(userAgent.toLowerCase());
            setIsMobile(mobile);
        };

        checkMobile();
        window.addEventListener('resize', checkMobile);
        return () => window.removeEventListener('resize', checkMobile);
    }, []);

    useEffect(() => {
        if (groupId && date) {
            fetchArticle();

            // Always show audio bar, but check availability for functionality
            setAudioAvailable(true); // Always show the bar

            // Check audio availability with range request (mobile-friendly)
            const audioUrl = `${STATIC_URL}/audio/${date}/${groupId}.mp3`;

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
                    // Don't set audio error here - let the audio element handle it
                    // This prevents false negatives on mobile networks
                });
        }
    }, [groupId, date]);

    const fetchArticle = async () => {
        try {
            setLoading(true);
            const response = await axios.get(
                `${API_URL}/api/news/articles/${date}/${groupId}`
            );
            setArticle(response.data);

            // Create source reference mapping
            const refs: Record<string, number> = {};
            let refCount = 1;
            response.data.body.forEach((section: any) => {
                section.sources.forEach((source: string) => {
                    if (!refs[source]) {
                        refs[source] = refCount++;
                    }
                });
            });
            setSourceRefs(refs);
        } catch (err) {
            setError('Failed to load article');
            console.error('Error fetching article:', err);
        } finally {
            setLoading(false);
        }
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
                    console.warn('HTML5 audio unlock failed:', playError);
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
                    oscillator.frequency.setValueAtTime(20000, audioContext.currentTime); // 20kHz - above most hearing ranges

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
                console.warn('AudioContext unlock failed:', contextError);
            }

            // Method 3: iOS-specific unlock using media session
            try {
                if ('mediaSession' in navigator) {
                    (navigator as any).mediaSession.setActionHandler('play', () => {
                        // Media session play handler
                    });
                }
            } catch (sessionError) {
                console.warn('Media session setup failed:', sessionError);
            }

            // Method 4: Fallback - try to create a user-initiated audio buffer
            try {
                const arrayBuffer = new ArrayBuffer(44100 * 0.1 * 2); // 0.1 second of silence
                const audioBuffer = new Float32Array(arrayBuffer);

                // Try to decode and play silence
                if ('webkitAudioContext' in window) {
                    const context = new (window as any).webkitAudioContext();
                    if (context.state === 'suspended') {
                        await context.resume();
                    }
                    context.close();
                }

                setAudioUnlocked(true);
            } catch (fallbackError) {
                console.warn('Fallback audio unlock failed:', fallbackError);
            }

        } catch (error) {
            console.error('Audio unlock methods failed:', error);
            // Don't set audioUnlocked to true if everything failed
        }
    };

    const handlePlayPause = async (event?: React.MouseEvent | React.TouchEvent) => {
        // Prevent double-triggering on mobile devices
        const now = Date.now();
        if (now - lastActionTime.current < 300) { // 300ms debounce
            return;
        }
        lastActionTime.current = now;

        if (!audioRef.current || audioError || isProcessingAudio) return;

        setIsProcessingAudio(true);

        try {
            // On mobile, first interaction needs to unlock audio
            if (isMobile && !audioUnlocked) {
                await unlockAudio();

                // If unlock failed, don't proceed
                if (!audioUnlocked) {
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
                            console.error('Audio play failed:', error);

                            // Try to diagnose the issue
                            if (error.name === 'NotAllowedError') {
                                setAudioUnlocked(false); // Reset unlock state
                            }

                            setAudioError(true);
                            setIsPlaying(false);
                        });
                } else {
                    setIsPlaying(true);
                }
            }
        } catch (error) {
            console.error('Audio playback error:', error);
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

    const renderContentWithSources = (content: string, sources: string[]) => {
        let processedContent = content;

        // Replace [SOURCE_X] markers with clickable source reference links
        sources.forEach((source, index) => {
            const sourceMarker = `[SOURCE_${index + 1}]`;
            const globalRefNumber = sourceRefs[source] || index + 1;

            // Replace source markers with clickable reference links
            processedContent = processedContent.replace(
                new RegExp(sourceMarker.replace(/[[\]]/g, '\\$&'), 'g'),
                `<a href="${source}" target="_blank" rel="noopener noreferrer" 
                    style="color: #00eaff; text-decoration: none; font-weight: 600; 
                    padding: 2px 6px; margin: 0 2px; border-radius: 4px; 
                    background: rgba(0, 234, 255, 0.1); border: 1px solid rgba(0, 234, 255, 0.2);
                    transition: all 0.3s ease; display: inline-block;"
                    onmouseover="this.style.backgroundColor='rgba(0, 234, 255, 0.2)'; 
                    this.style.color='white'; this.style.transform='translateY(-1px)'; 
                    this.style.boxShadow='0 2px 8px rgba(0, 234, 255, 0.3)'"
                    onmouseout="this.style.backgroundColor='rgba(0, 234, 255, 0.1)'; 
                    this.style.color='#00eaff'; this.style.transform='translateY(0)'; 
                    this.style.boxShadow='none'"
                    title="Click to open source">[${globalRefNumber}]</a>`
            );
        });

        return processedContent;
    };

    const calculateRegionDiversityScore = (regions: string[]): string => {
        const uniqueRegions = new Set(regions);
        const diversityCount = uniqueRegions.size;

        if (diversityCount >= 4) return 'High';
        if (diversityCount >= 2) return 'Medium';
        return 'Low';
    };

    const handleSourceClick = (source: string) => {
        window.open(source, '_blank', 'noopener,noreferrer');
    };

    const handleAudioError = (event: any) => {
        console.error(`Audio Error Handler: Audio failed to load for article ${groupId} on ${date}`);
        console.error(`Expected path: /static/audio/${date}/${groupId}.mp3`);
        console.error(`Full URL: ${API_URL}/static/audio/${date}/${groupId}.mp3`);

        // Log detailed error information
        if (event?.target) {
            console.error('Audio Error Details:', {
                readyState: event.target.readyState,
                networkState: event.target.networkState,
                error: event.target.error
            });
        }

        setAudioError(true);
        setIsPlaying(false);
        // Keep audioAvailable true so bar stays visible
    };

    const handleAudioLoaded = () => {
        setAudioError(false);
        setAudioAvailable(true);
    };

    // Handle audio events specific to mobile
    const handleCanPlayThrough = () => {
        if (isMobile && !audioUnlocked) {
            // Audio ready but waiting for user interaction on mobile
        }
    };

    const handleAudioPlay = () => {
        setIsPlaying(true);
    };

    const handleAudioPause = () => {
        setIsPlaying(false);
    };

    const handleAudioEnded = () => {
        setIsPlaying(false);
        setCurrentTime(0);
    };

    const toggleMeta = () => {
        setExpandedMeta(!expandedMeta);
    };

    // Mobile touch event handlers
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

    if (loading) {
        return (
            <Container maxWidth="lg" sx={{ py: 4, mt: '90px' }}>
                <LinearProgress />
                <Typography variant="h6" sx={{ mt: 2, textAlign: 'center' }}>
                    Loading article...
                </Typography>
            </Container>
        );
    }

    if (error || !article) {
        return (
            <Container maxWidth="lg" sx={{ py: 4, mt: '90px' }}>
                <Typography variant="h6" color="error" sx={{ textAlign: 'center' }}>
                    {error || 'Article not found'}
                </Typography>
            </Container>
        );
    }

    return (
        <Container maxWidth={false} sx={{ py: 4, mt: '90px', px: { xs: 2, sm: 3, md: 4 } }}>
            <ArticleContainer>
                {/* Audio Bar - Always show */}
                <AudioBar className="audio-bar">
                    <AudioControls>
                        <PlayPauseButton
                            onClick={handleClick}
                            onTouchStart={handleTouchStart}
                            onTouchEnd={handleTouchEnd}
                            disabled={audioError || isProcessingAudio}
                            isplaying={isPlaying}
                            title={
                                isProcessingAudio ? "Processing..." :
                                    isMobile && !audioUnlocked ? "Tap to enable audio" :
                                        isPlaying ? "Pause" : "Play"
                            }
                            sx={{
                                touchAction: 'manipulation', // Prevents double-tap zoom on iOS
                                WebkitTouchCallout: 'none',
                                WebkitUserSelect: 'none',
                                userSelect: 'none',
                                opacity: isProcessingAudio ? 0.7 : 1,
                                transition: 'opacity 0.2s ease',
                            }}
                        >
                            {isProcessingAudio ? <VolumeUp /> : (isPlaying ? <Pause /> : <PlayArrow />)}
                        </PlayPauseButton>
                        <VolumeUp sx={{ color: audioError ? 'rgba(255,255,255,0.5)' : '#00eaff', transition: 'color 0.3s' }} />
                        <ProgressContainer>
                            <Typography variant="caption" sx={{ color: '#00eaff', minWidth: '40px', fontWeight: 700 }}>
                                {audioError ? '--:--' : formatTime(currentTime)}
                            </Typography>
                            <LinearProgress
                                variant="determinate"
                                value={audioError ? 0 : (duration ? (currentTime / duration) * 100 : 0)}
                                sx={{
                                    flex: 1,
                                    height: 8,
                                    borderRadius: 4,
                                    bgcolor: 'rgba(0,234,255,0.15)',
                                    '& .MuiLinearProgress-bar': {
                                        bgcolor: audioError ? '#ccc' : 'linear-gradient(90deg, #00eaff 0%, #ff6a00 100%)',
                                        transition: 'background 0.3s',
                                    },
                                }}
                            />
                            <Typography variant="caption" sx={{ color: '#ff6a00', minWidth: '40px', fontWeight: 700 }}>
                                {audioError ? '--:--' : formatTime(duration)}
                            </Typography>
                        </ProgressContainer>
                        {audioError && (
                            <Typography variant="caption" sx={{ color: '#ff6a00', fontSize: '0.8rem', fontWeight: 500 }}>
                                Audio file not found
                            </Typography>
                        )}
                        {isMobile && !audioUnlocked && !audioError && !isProcessingAudio && (
                            <Typography variant="caption" sx={{ color: '#00eaff', fontSize: '0.8rem', fontWeight: 500 }}>
                                Tap play to enable audio
                            </Typography>
                        )}
                        {isProcessingAudio && (
                            <Typography variant="caption" sx={{ color: '#ff6a00', fontSize: '0.8rem', fontWeight: 500 }}>
                                Processing audio...
                            </Typography>
                        )}
                        <Tooltip title="Share">
                            <IconButton sx={{ color: '#ff6a00', transition: 'color 0.3s', '&:hover': { color: '#00eaff' } }}>
                                <Share />
                            </IconButton>
                        </Tooltip>
                        <Tooltip title={isBookmarked ? 'Remove bookmark' : 'Bookmark'}>
                            <IconButton
                                onClick={() => setIsBookmarked(!isBookmarked)}
                                sx={{ color: isBookmarked ? '#ff6a00' : '#00eaff', transition: 'color 0.3s', '&:hover': { color: '#ff6a00' } }}
                            >
                                {isBookmarked ? <Bookmark /> : <BookmarkBorder />}
                            </IconButton>
                        </Tooltip>
                    </AudioControls>
                    <audio
                        ref={audioRef}
                        src={`${STATIC_URL}/audio/${date}/${groupId}.mp3`}
                        onTimeUpdate={handleTimeUpdate}
                        onLoadedMetadata={handleLoadedMetadata}
                        onEnded={handleAudioEnded}
                        onError={handleAudioError}
                        onCanPlay={handleAudioLoaded}
                        onCanPlayThrough={handleCanPlayThrough}
                        onPlay={handleAudioPlay}
                        onPause={handleAudioPause}
                        preload={isMobile ? "none" : "metadata"}
                        playsInline
                        crossOrigin="anonymous"
                    />
                </AudioBar>

                {/* Article Header with Sidebar */}
                <ArticleHeader>
                    <VersionDisplay>v{APP_VERSION}</VersionDisplay>
                    <ArticleMainContent>
                        {/* Category and Title */}
                        <Box sx={{ mb: 3 }}>
                            <Chip
                                label={article.category.toUpperCase()}
                                sx={{
                                    bgcolor: '#e63946',
                                    color: 'white',
                                    fontWeight: 600,
                                    mb: 2,
                                }}
                            />
                            <ArticleTitle variant="h1">{article.headline}</ArticleTitle>
                            {article.subheadline && (
                                <Typography
                                    variant="h5"
                                    sx={{
                                        color: '#666',
                                        fontWeight: 400,
                                        mb: 2,
                                        fontStyle: 'italic',
                                    }}
                                >
                                    {article.subheadline}
                                </Typography>
                            )}
                        </Box>

                        {/* Leading Paragraph */}
                        <LeadParagraph>{article.lead}</LeadParagraph>
                    </ArticleMainContent>

                    {/* Metadata Sidebar */}
                    <ArticleSidebar>
                        <Typography variant="h6" sx={{ color: '#00eaff', mb: 2, fontWeight: 600, display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Info fontSize="small" />
                            Intelligent News Analysis
                        </Typography>
                        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                            <SidebarItem>
                                <Schedule fontSize="small" />
                                <span>{new Date(date || article.body[0]?.date || '').toLocaleDateString()}</span>
                            </SidebarItem>
                            <SidebarItem>
                                <LocationOn fontSize="small" />
                                <span>Regions: {article.body[0]?.Publisher_region_diversity?.join(', ') || 'N/A'}</span>
                            </SidebarItem>
                            <SidebarItem>
                                <Business fontSize="small" />
                                <span>Publishers: {article.body[0]?.Publishers?.join(', ') || 'N/A'}</span>
                            </SidebarItem>
                            <SidebarItem>
                                <ThumbUp fontSize="small" />
                                <span>Sentiment: {
                                    (() => {
                                        const sentiment = parseFloat(article.body[0]?.sentisement_from_the_content || '0');
                                        return sentiment > 0.3 ? 'Positive' : sentiment < -0.3 ? 'Negative' : 'Neutral';
                                    })()
                                }</span>
                            </SidebarItem>
                            <SidebarItem>
                                <Warning fontSize="small" />
                                <span>Reliability: {
                                    (() => {
                                        const probability = parseFloat(String(article.body[0]?.fake_news_probability || '0'));
                                        return probability > 0.7 ? 'Low' : probability > 0.4 ? 'Medium' : 'High';
                                    })()
                                }</span>
                            </SidebarItem>
                            <SidebarItem>
                                <Link fontSize="small" />
                                <span>Sources: {article.body[0]?.sources?.length || 0}</span>
                            </SidebarItem>
                        </Box>
                    </ArticleSidebar>
                </ArticleHeader>

                {/* Cover Image */}
                <Box sx={{ mb: 3 }}>
                    <img
                        src={`${STATIC_URL}/images/${date}/${groupId}.jpg`}
                        alt={article.headline}
                        style={{
                            width: '100%',
                            maxHeight: '500px',
                            objectFit: 'cover',
                            borderRadius: '8px',
                        }}
                        onError={(e) => {
                            (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80';
                        }}
                    />
                </Box>

                {/* Article Body */}
                {article.body.map((section, index) => (
                    <SectionContainer key={index}>
                        <SectionContent>
                            <SectionTitle variant="h3">{section.section}</SectionTitle>
                            <BodyContent>
                                <div
                                    dangerouslySetInnerHTML={{
                                        __html: renderContentWithSources(section.content, section.sources),
                                    }}
                                />
                            </BodyContent>
                            {/* Sources at the end of each section */}
                            {section.sources && section.sources.length > 0 && (
                                <Box sx={{ mt: 2, mb: 2 }}>
                                    <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#666' }}>
                                        Sources:
                                    </Typography>
                                    <Box sx={{ pl: 1 }}>
                                        {section.sources.map((source, idx) => (
                                            <Box key={idx} sx={{ mb: 0.5 }}>
                                                <Tooltip
                                                    title={`Click to open: ${source}`}
                                                    placement="top"
                                                    arrow
                                                >
                                                    <Box
                                                        component="a"
                                                        href={source}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        onClick={(e) => {
                                                            e.preventDefault();
                                                            window.open(source, '_blank', 'noopener,noreferrer');
                                                        }}
                                                        sx={{
                                                            color: '#00eaff',
                                                            textDecoration: 'none',
                                                            padding: '2px 6px',
                                                            borderRadius: '4px',
                                                            background: 'rgba(0, 234, 255, 0.1)',
                                                            border: '1px solid rgba(0, 234, 255, 0.2)',
                                                            transition: 'all 0.3s ease',
                                                            display: 'inline-block',
                                                            cursor: 'pointer',
                                                            '&:hover': {
                                                                background: 'rgba(0, 234, 255, 0.2)',
                                                                color: 'white',
                                                                transform: 'translateY(-1px)',
                                                                boxShadow: '0 2px 8px rgba(0, 234, 255, 0.3)',
                                                                textDecoration: 'none',
                                                            },
                                                        }}
                                                    >
                                                        [{idx + 1}] {source}
                                                    </Box>
                                                </Tooltip>
                                            </Box>
                                        ))}
                                    </Box>
                                </Box>
                            )}
                        </SectionContent>
                    </SectionContainer>
                ))}

                {/* Conclusion */}
                <Divider sx={{ my: 3 }} />
                <SectionTitle variant="h3">Conclusion</SectionTitle>
                <BodyContent>
                    <Typography paragraph>{article.conclusion}</Typography>
                </BodyContent>

                {/* Timeline */}
                {(() => {
                    return Object.keys(article.timeline || {}).length > 0;
                })() && (
                        <>
                            <Divider sx={{ my: 3 }} />
                            <SectionTitle variant="h3">Timeline</SectionTitle>
                            <Grid container spacing={2}>
                                {Object.entries(article.timeline).map(([time, event], index) => (
                                    <Grid item xs={12} key={index}>
                                        <Card variant="outlined" sx={{ p: 2 }}>
                                            <Typography variant="subtitle2" color="primary" gutterBottom>
                                                {new Date(time).toLocaleString()}
                                            </Typography>
                                            <Typography variant="body2">{event}</Typography>
                                        </Card>
                                    </Grid>
                                ))}
                            </Grid>
                        </>
                    )}

                {/* Sources */}
                <Divider sx={{ my: 3 }} />
                <SectionTitle variant="h3">Sources</SectionTitle>
                <Box sx={{ pl: 2 }}>
                    {Object.entries(sourceRefs).map(([source, refNumber]) => (
                        <Typography key={source} variant="body2" sx={{ mb: 1 }}>
                            <Tooltip
                                title={`Click to open: ${source}`}
                                placement="top"
                                arrow
                            >
                                <SourceLink onClick={() => handleSourceClick(source)}>
                                    {refNumber}
                                </SourceLink>
                            </Tooltip>{' '}
                            <Tooltip
                                title={`Click to open: ${source}`}
                                placement="top"
                                arrow
                            >
                                <span
                                    style={{
                                        cursor: 'pointer',
                                        color: '#666',
                                        transition: 'color 0.2s ease'
                                    }}
                                    onMouseEnter={(e) => {
                                        (e.target as HTMLElement).style.color = '#e63946';
                                    }}
                                    onMouseLeave={(e) => {
                                        (e.target as HTMLElement).style.color = '#666';
                                    }}
                                    onClick={() => handleSourceClick(source)}
                                >
                                    {source}
                                </span>
                            </Tooltip>
                        </Typography>
                    ))}
                </Box>

                {/* Video (if available) */}
                <Box sx={{ mt: 3 }}>
                    <video
                        controls
                        style={{
                            width: '100%',
                            borderRadius: '8px',
                            display: 'none',
                        }}
                        onLoadStart={(e) => {
                            (e.target as HTMLVideoElement).style.display = 'block';
                        }}
                        onError={(e) => {
                            (e.target as HTMLVideoElement).style.display = 'none';
                        }}
                    >
                        <source
                            src={`${STATIC_URL}/video/${date}/${groupId}.mp4`}
                            type="video/mp4"
                        />
                        Your browser does not support the video tag.
                    </video>
                </Box>
            </ArticleContainer>
        </Container>
    );
};

export default ArticlePage;