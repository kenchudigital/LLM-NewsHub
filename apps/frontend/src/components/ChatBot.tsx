import config from '../config';
import React, { useState, useEffect, useRef } from 'react';
import {
    Box,
    Paper,
    Typography,
    TextField,
    IconButton,
    List,
    ListItem,
    ListItemText,
    Divider,
    Chip,
    Alert,
    Menu,
    MenuItem,
    ListItemIcon,
    Select,
    FormControl,
    InputLabel,
} from '@mui/material';
import {
    Send as SendIcon,
    Article as ArticleIcon,
    Memory as MemoryIcon,
    BarChart as ChartIcon,
    AutoAwesome,
    Settings as SettingsIcon,
    Delete as DeleteIcon,
    Psychology as PsychologyIcon,
    AccountTree as KnowledgeIcon,
    Cloud as CloudIcon,
    AutoFixHigh as GeminiIcon,
    Search as PerplexityIcon,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import axios from 'axios';
import { ChartData } from './ChartWidget';

// Available AI models - matching the LLM service
const AVAILABLE_MODELS = [
    {
        id: 'gpt-4o-mini',
        name: 'GPT-4o Mini',
        displayName: 'GPT-4o Mini',
        provider: 'OpenAI',
        icon: PsychologyIcon
    },
    {
        id: 'qwen-turbo',
        name: 'Qwen Turbo',
        displayName: 'Qwen Turbo',
        provider: 'Alibaba',
        icon: CloudIcon
    },
    {
        id: 'gemini-1.5-flash',
        name: 'Gemini 1.5 Flash',
        displayName: 'Gemini 1.5 Flash',
        provider: 'Gemini',
        icon: GeminiIcon
    },
    {
        id: 'llama-3.1-sonar-small-128k-online',
        name: 'llama 3.1 Sonar',
        displayName: 'lama 3.1 Sonar',
        provider: 'Perplexity',
        icon: PerplexityIcon
    },
    {
        id: 'knowledge-graph',
        name: 'Knowledge Graph',
        displayName: 'Knowledge Graph',
        provider: 'Knowledge',
        icon: KnowledgeIcon
    },
];

const DEFAULT_MODEL = AVAILABLE_MODELS[0];

// Styled components for high-tech theme
const ChatContainer = styled(Paper)(({ theme }) => ({
    height: '100%',
    display: 'flex',
    flexDirection: 'column',
    maxHeight: '600px',
    background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.95) 0%, rgba(26, 26, 46, 0.9) 50%, rgba(22, 33, 62, 0.85) 100%)',
    border: '1px solid rgba(255, 106, 0, 0.3)',
    borderRadius: '12px',
    backdropFilter: 'blur(10px)',
    boxShadow: '0 8px 32px rgba(255, 106, 0, 0.15), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
    overflow: 'hidden',
    position: 'relative',

    // Mobile responsive adjustments
    [theme.breakpoints.down('sm')]: {
        maxHeight: '400px',
        borderRadius: '8px',
    },

    '@media (max-width: 360px)': {
        maxHeight: '350px',
        borderRadius: '6px',
    },

    '&::before': {
        content: '""',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'radial-gradient(circle at 20% 20%, rgba(255, 106, 0, 0.05) 0%, transparent 50%)',
        pointerEvents: 'none',
        zIndex: 0,
    },
}));

const ChatHeader = styled(Box)(({ theme }) => ({
    padding: '1rem',
    background: 'linear-gradient(135deg, rgba(0, 0, 0, 0.9) 0%, rgba(26, 26, 26, 0.8) 100%)',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderBottom: '1px solid rgba(255, 106, 0, 0.3)',
    position: 'relative',
    zIndex: 1,

    // Mobile responsive adjustments
    [theme.breakpoints.down('sm')]: {
        padding: '0.75rem',
    },

    '@media (max-width: 360px)': {
        padding: '0.5rem',
    },
}));

const MessageBubble = styled(Paper)<{ sender: 'user' | 'bot' }>(({ theme, sender }) => ({
    padding: '12px 16px',
    borderRadius: '16px',
    width: '100%',
    position: 'relative',
    background: sender === 'user'
        ? 'linear-gradient(135deg, rgba(0, 234, 255, 0.8) 0%, rgba(0, 234, 255, 0.6) 100%)'
        : 'linear-gradient(135deg, rgba(255, 106, 0, 0.1) 0%, rgba(255, 106, 0, 0.05) 100%)',
    border: sender === 'user'
        ? '1px solid rgba(0, 234, 255, 0.4)'
        : '1px solid rgba(255, 106, 0, 0.2)',
    color: sender === 'user' ? 'white' : 'rgba(255, 255, 255, 0.9)',
    backdropFilter: 'blur(10px)',
    boxShadow: sender === 'user'
        ? '0 4px 16px rgba(0, 234, 255, 0.2)'
        : '0 4px 16px rgba(255, 106, 0, 0.1)',

    // Mobile responsive adjustments
    [theme.breakpoints.down('sm')]: {
        padding: '10px 14px',
        borderRadius: '12px',
    },

    '@media (max-width: 360px)': {
        padding: '8px 12px',
        borderRadius: '10px',
    },
}));

interface QuickActionChipProps {
    variant?: 'chart' | 'action';
}

const QuickActionChip = styled(Chip)<QuickActionChipProps>(({ theme, variant }) => ({
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    background: variant === 'chart'
        ? 'linear-gradient(45deg, #ff6a00, #00eaff)'
        : 'linear-gradient(45deg, rgba(255, 106, 0, 0.2), rgba(0, 234, 255, 0.2))',
    color: 'white',
    border: variant === 'chart'
        ? '1px solid rgba(255, 106, 0, 0.5)'
        : '1px solid rgba(0, 234, 255, 0.3)',
    '&:hover': {
        transform: 'translateY(-2px)',
        boxShadow: variant === 'chart'
            ? '0 6px 20px rgba(255, 106, 0, 0.4)'
            : '0 6px 20px rgba(0, 234, 255, 0.3)',
    },
}));

const StyledTextField = styled(TextField)(({ theme }) => ({
    '& .MuiOutlinedInput-root': {
        background: 'rgba(13, 13, 13, 0.6)',
        color: 'rgba(255, 255, 255, 0.9)',
        borderRadius: '12px',
        minWidth: 0, // Allow flex shrinking
        width: '100%',
        '& fieldset': {
            borderColor: 'rgba(255, 106, 0, 0.3)',
        },
        '&:hover fieldset': {
            borderColor: 'rgba(255, 106, 0, 0.5)',
        },
        '&.Mui-focused fieldset': {
            borderColor: '#ff6a00',
        },
        // Mobile responsive adjustments
        '@media (max-width: 600px)': {
            borderRadius: '8px',
        },
        '@media (max-width: 360px)': {
            borderRadius: '6px',
        },
    },
    '& .MuiInputBase-input': {
        minWidth: 0, // Allow text to wrap properly
        '&::placeholder': {
            color: 'rgba(255, 255, 255, 0.5)',
        },
    },
}));

const StyledMenu = styled(Menu)(({ theme }) => ({
    '& .MuiPaper-root': {
        background: 'linear-gradient(135deg, rgba(13, 13, 13, 0.95) 0%, rgba(26, 26, 46, 0.9) 100%)',
        border: '1px solid rgba(255, 106, 0, 0.3)',
        borderRadius: '8px',
        backdropFilter: 'blur(10px)',
        boxShadow: '0 8px 32px rgba(255, 106, 0, 0.15)',
        color: 'rgba(255, 255, 255, 0.9)',
        minWidth: '200px',
    },
    '& .MuiMenuItem-root': {
        '&:hover': {
            background: 'rgba(255, 106, 0, 0.1)',
        },
    },
}));

interface Message {
    id: number;
    text: string;
    sender: 'user' | 'bot';
    timestamp: Date;
    context?: string;
    hasChart?: boolean;
    hasAnalysis?: boolean;
}

interface ChatBotProps {
    currentGroupId?: string;
    currentDate?: string;
}

interface PendingRequest {
    id: string;
    userMessage: Message;
    timestamp: Date;
    context: any;
    model: string;
}

const ChatBot: React.FC<ChatBotProps> = ({ currentGroupId, currentDate }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [conversationMemory, setConversationMemory] = useState<string[]>([]);
    const [selectedModel, setSelectedModel] = useState(DEFAULT_MODEL);
    const [userIP, setUserIP] = useState<string>('');
    const [settingsAnchorEl, setSettingsAnchorEl] = useState<null | HTMLElement>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const backgroundProcessingInterval = useRef<NodeJS.Timeout | null>(null);

    // Fix API URL - use config.API_URL (empty for proxy) instead of localhost fallback
    const API_URL = config.API_URL;

    // Get user IP address
    const getUserIP = async () => {
        try {
            const response = await axios.get('https://api.ipify.org?format=json');
            return response.data.ip;
        } catch (error) {
            console.error('Error getting IP:', error);
            return 'localhost';
        }
    };

    // LocalStorage utility functions
    const getStorageKey = (key: string) => `chatbot_${userIP}_${key}`;

    const saveConversation = (messages: Message[]) => {
        if (userIP) {
            localStorage.setItem(getStorageKey('conversation'), JSON.stringify(messages));
        }
    };

    const loadConversation = (): Message[] => {
        if (userIP) {
            const saved = localStorage.getItem(getStorageKey('conversation'));
            if (saved) {
                try {
                    const parsed = JSON.parse(saved);
                    return parsed.map((msg: any) => ({
                        ...msg,
                        timestamp: new Date(msg.timestamp),
                    }));
                } catch (error) {
                    console.error('Error parsing saved conversation:', error);
                }
            }
        }
        return [];
    };

    const saveSelectedModel = (model: typeof DEFAULT_MODEL) => {
        if (userIP) {
            localStorage.setItem(getStorageKey('selectedModel'), JSON.stringify(model));
        }
    };

    const loadSelectedModel = (): typeof DEFAULT_MODEL => {
        if (userIP) {
            const saved = localStorage.getItem(getStorageKey('selectedModel'));
            if (saved) {
                try {
                    return JSON.parse(saved);
                } catch (error) {
                    console.error('Error parsing saved model:', error);
                }
            }
        }
        return DEFAULT_MODEL;
    };

    // Background processing functions
    const savePendingRequest = (request: PendingRequest) => {
        if (userIP) {
            const existingRequests = loadPendingRequests();
            const updatedRequests = [...existingRequests, request];
            localStorage.setItem(getStorageKey('pendingRequests'), JSON.stringify(updatedRequests));
        }
    };

    const loadPendingRequests = (): PendingRequest[] => {
        if (userIP) {
            const saved = localStorage.getItem(getStorageKey('pendingRequests'));
            if (saved) {
                try {
                    const parsed = JSON.parse(saved);
                    return parsed.map((req: any) => ({
                        ...req,
                        timestamp: new Date(req.timestamp),
                        userMessage: {
                            ...req.userMessage,
                            timestamp: new Date(req.userMessage.timestamp),
                        },
                    }));
                } catch (error) {
                    console.error('Error parsing pending requests:', error);
                }
            }
        }
        return [];
    };

    const removePendingRequest = (requestId: string) => {
        if (userIP) {
            const existingRequests = loadPendingRequests();
            const updatedRequests = existingRequests.filter(req => req.id !== requestId);
            localStorage.setItem(getStorageKey('pendingRequests'), JSON.stringify(updatedRequests));
        }
    };

    const clearOldPendingRequests = () => {
        if (userIP) {
            const existingRequests = loadPendingRequests();
            const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
            const validRequests = existingRequests.filter(req => new Date(req.timestamp) > oneHourAgo);
            localStorage.setItem(getStorageKey('pendingRequests'), JSON.stringify(validRequests));
        }
    };

    const processPendingRequest = async (request: PendingRequest) => {
        try {
            const response = await axios.post(`${API_URL}/api/chat`, {
                message: request.userMessage.text,
                model: request.model,
                context: request.context,
            });

            let botResponseText = response.data.response;
            let chartGenerated = false;

            // Check if the backend returned chart data
            if (response.data.chart_data) {
                const chartData: ChartData = response.data.chart_data;
                // Add chart to the page if component is still mounted
                if ((window as any).addChart) {
                    (window as any).addChart(chartData);
                    chartGenerated = true;
                }
            }

            const botMessage: Message = {
                id: Date.now() + 1,
                text: botResponseText,
                sender: 'bot',
                timestamp: new Date(),
                hasChart: chartGenerated,
            };

            // Update conversation in localStorage
            const currentConversation = loadConversation();
            const updatedConversation = [...currentConversation, botMessage];
            saveConversation(updatedConversation);

            // Update messages state if component is still mounted
            setMessages(prev => [...prev, botMessage]);

            // Update conversation memory
            setConversationMemory(prev => [...prev.slice(-4), response.data.response]);

            // Remove from pending requests
            removePendingRequest(request.id);

            return true;
        } catch (error) {
            console.error('Error processing background request:', error);

            // Create error message
            const errorMessage: Message = {
                id: Date.now() + 1,
                text: 'Sorry, I encountered an error while processing your request in the background. Please try again.',
                sender: 'bot',
                timestamp: new Date(),
            };

            // Update conversation in localStorage
            const currentConversation = loadConversation();
            const updatedConversation = [...currentConversation, errorMessage];
            saveConversation(updatedConversation);

            // Update messages state if component is still mounted
            setMessages(prev => [...prev, errorMessage]);

            // Remove from pending requests
            removePendingRequest(request.id);

            return false;
        }
    };

    const checkAndProcessPendingRequests = async () => {
        const pendingRequests = loadPendingRequests();

        for (const request of pendingRequests) {
            await processPendingRequest(request);
        }
    };

    // Initialize IP and load data
    useEffect(() => {
        const initializeChat = async () => {
            const ip = await getUserIP();
            setUserIP(ip);
        };
        initializeChat();
    }, []);

    // Load conversation and model when IP is available
    useEffect(() => {
        if (userIP) {
            const savedConversation = loadConversation();
            const savedModel = loadSelectedModel();

            if (savedConversation.length > 0) {
                setMessages(savedConversation);
                setConversationMemory(savedConversation
                    .filter(msg => msg.sender === 'user')
                    .slice(-5)
                    .map(msg => msg.text)
                );
            } else {
                // Initialize with welcome message if no saved conversation
                const welcomeMessage: Message = {
                    id: Date.now(),
                    text: "Hello! I'm your AI news assistant !",
                    sender: 'bot',
                    timestamp: new Date(),
                };
                setMessages([welcomeMessage]);
            }

            setSelectedModel(savedModel);
        }
    }, [userIP]);

    // Save conversation whenever messages change
    useEffect(() => {
        if (userIP && messages.length > 0) {
            saveConversation(messages);
        }
    }, [messages, userIP]);

    // Save model whenever it changes
    useEffect(() => {
        if (userIP && selectedModel) {
            saveSelectedModel(selectedModel);
        }
    }, [selectedModel, userIP]);

    // Background processing setup
    useEffect(() => {
        if (userIP) {
            // Clear old pending requests (older than 1 hour)
            clearOldPendingRequests();

            // Check for pending requests on mount
            checkAndProcessPendingRequests();

            // Set up interval to check for pending requests every 5 seconds
            backgroundProcessingInterval.current = setInterval(() => {
                checkAndProcessPendingRequests();
            }, 5000);
        }

        return () => {
            if (backgroundProcessingInterval.current) {
                clearInterval(backgroundProcessingInterval.current);
            }
        };
    }, [userIP]);

    // Auto-scroll to bottom when new messages arrive
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Update context when article changes
    useEffect(() => {
        if (currentGroupId && currentDate) {
            const contextMessage: Message = {
                id: Date.now(),
                text: `keep article: (ID: ${currentGroupId}) in LLM CONTEXT now`,
                sender: 'bot',
                timestamp: new Date(),
                context: `Article Context: ${currentGroupId} from ${currentDate}`,
            };
            setMessages(prev => [...prev, contextMessage]);
        }
    }, [currentGroupId, currentDate]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMessage: Message = {
            id: Date.now(),
            text: input.trim(),
            sender: 'user',
            timestamp: new Date(),
        };

        setMessages((prev) => [...prev, userMessage]);

        // Add to conversation memory
        setConversationMemory(prev => [...prev.slice(-4), input.trim()]);

        const userInput = input.trim();
        const requestId = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

        // Create pending request
        const pendingRequest: PendingRequest = {
            id: requestId,
            userMessage,
            timestamp: new Date(),
            context: {
                currentGroupId,
                currentDate,
                conversationHistory: conversationMemory,
            },
            model: selectedModel.id,
        };

        // Save pending request for background processing
        savePendingRequest(pendingRequest);

        setInput('');
        setIsLoading(true);

        try {
            const response = await axios.post(`${API_URL}/api/chat`, {
                message: userInput,
                model: selectedModel.id,
                context: {
                    currentGroupId,
                    currentDate,
                    conversationHistory: conversationMemory,
                },
            });

            let botResponseText = response.data.response;
            let chartGenerated = false;
            let analysisGenerated = false;

            // Check if the backend returned chart data
            if (response.data.chart_data) {
                const chartData: ChartData = response.data.chart_data;

                // Add chart to the page
                if ((window as any).addChart) {
                    (window as any).addChart(chartData);
                    chartGenerated = true;
                }
            }

            // Check if this is a 5W1H analysis response
            const analysisKeywords = ['Who:', 'What:', 'When:', 'Where:', 'Why:', 'How:', '5W1H'];
            analysisGenerated = analysisKeywords.some(keyword =>
                botResponseText.includes(keyword)
            );

            const botMessage: Message = {
                id: Date.now() + 1,
                text: botResponseText,
                sender: 'bot',
                timestamp: new Date(),
                hasChart: chartGenerated,
                hasAnalysis: analysisGenerated,
            };

            setMessages((prev) => [...prev, botMessage]);

            // Add bot response to memory
            setConversationMemory(prev => [...prev.slice(-4), response.data.response]);

            // Remove from pending requests since we got the response
            removePendingRequest(requestId);

        } catch (error) {
            console.error('Error sending message:', error);
            let errorMessage = 'Sorry, I encountered an error. The request will continue processing in the background.';

            if (axios.isAxiosError(error)) {
                if (error.response?.status === 500) {
                    errorMessage = 'The AI service is currently unavailable. The request will continue processing in the background.';
                } else if (error.response?.data?.detail) {
                    errorMessage = `Error: ${error.response.data.detail}. The request will continue processing in the background.`;
                }
            }

            const errorMsg: Message = {
                id: Date.now() + 1,
                text: errorMessage,
                sender: 'bot',
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMsg]);

            // Don't remove from pending requests - let background processing handle it
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (event: React.KeyboardEvent) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            handleSend();
        }
    };

    const clearConversation = () => {
        setMessages([]);
        setConversationMemory([]);

        // Clear from localStorage
        if (userIP) {
            localStorage.removeItem(getStorageKey('conversation'));
        }

        const welcomeMessage: Message = {
            id: Date.now(),
            text: "Conversation cleared! How can I help you with the current article?",
            sender: 'bot',
            timestamp: new Date(),
        };
        setMessages([welcomeMessage]);
        setSettingsAnchorEl(null);
    };

    const handleSettingsClick = (event: React.MouseEvent<HTMLElement>) => {
        setSettingsAnchorEl(event.currentTarget);
    };

    const handleSettingsClose = () => {
        setSettingsAnchorEl(null);
    };

    const handleModelChange = (model: typeof DEFAULT_MODEL) => {
        setSelectedModel(model);
        setSettingsAnchorEl(null);
    };

    const getModelIcon = (model: typeof DEFAULT_MODEL) => {
        const IconComponent = model.icon;
        return <IconComponent sx={{ color: 'rgba(255, 255, 255, 0.9)' }} />;
    };

    const sendAnalysisRequest = () => {
        const analysisPrompt = "Analyze using 5W1H: Who, What, When, Where, Why, How";
        setInput(analysisPrompt);
        setTimeout(() => {
            handleSend();
        }, 100);
    };

    const sendQuickMessage = (message: string) => {
        setInput(message);
        // Auto-send after a short delay to show the message in input first
        setTimeout(() => {
            if (input === message) { // Only send if input hasn't changed
                handleSend();
            }
        }, 100);
    };

    return (
        <Box sx={{
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            position: 'relative',
            width: '100%',
            minWidth: 0,
            overflow: 'hidden',
        }}>
            {/* Chat Header with Model Display and Settings */}
            <ChatHeader>
                <Typography variant="h6" sx={{
                    fontWeight: 'bold',
                    fontSize: '1.1rem',
                    '@media (max-width: 600px)': {
                        fontSize: '1rem',
                    },
                    '@media (max-width: 360px)': {
                        fontSize: '0.9rem',
                    },
                }}>
                    Model: {selectedModel.displayName}
                </Typography>
                <IconButton
                    onClick={handleSettingsClick}
                    sx={{
                        color: 'white',
                        '&:hover': {
                            background: 'rgba(255, 255, 255, 0.1)',
                        },
                        '@media (max-width: 600px)': {
                            width: '36px',
                            height: '36px',
                        },
                        '@media (max-width: 360px)': {
                            width: '32px',
                            height: '32px',
                        },
                    }}
                >
                    <SettingsIcon sx={{
                        '@media (max-width: 600px)': {
                            fontSize: '1.1rem',
                        },
                        '@media (max-width: 360px)': {
                            fontSize: '1rem',
                        },
                    }} />
                </IconButton>
            </ChatHeader>

            {/* Settings Menu */}
            <StyledMenu
                anchorEl={settingsAnchorEl}
                open={Boolean(settingsAnchorEl)}
                onClose={handleSettingsClose}
                transformOrigin={{ horizontal: 'right', vertical: 'top' }}
                anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
                <Typography variant="subtitle2" sx={{ px: 2, py: 1, opacity: 0.7 }}>
                    AI Model
                </Typography>
                {AVAILABLE_MODELS.map((model) => (
                    <MenuItem
                        key={model.id}
                        onClick={() => handleModelChange(model)}
                        selected={selectedModel.id === model.id}
                        sx={{
                            '&.Mui-selected': {
                                background: 'rgba(255, 106, 0, 0.2)',
                                '&:hover': {
                                    background: 'rgba(255, 106, 0, 0.3)',
                                },
                            },
                        }}
                    >
                        <ListItemIcon>
                            {getModelIcon(model)}
                        </ListItemIcon>
                        <ListItemText
                            primary={model.name}
                            secondary={model.provider}
                            secondaryTypographyProps={{
                                sx: {
                                    color: 'rgba(255, 255, 255, 0.6)',
                                    fontSize: '0.75rem'
                                }
                            }}
                        />
                    </MenuItem>
                ))}
                <Divider sx={{ borderColor: 'rgba(255, 106, 0, 0.2)', my: 1 }} />
                <MenuItem onClick={clearConversation}>
                    <ListItemIcon>
                        <DeleteIcon sx={{ color: 'rgba(255, 255, 255, 0.9)' }} />
                    </ListItemIcon>
                    <ListItemText primary="Clear Conversation" />
                </MenuItem>
            </StyledMenu>

            {/* Context Indicator */}
            {currentGroupId && (
                <Alert
                    severity="success"
                    sx={{
                        m: 1,
                        fontSize: '0.75rem',
                        background: 'linear-gradient(45deg, rgba(0, 234, 255, 0.1), rgba(255, 106, 0, 0.1))',
                        color: 'rgba(255, 255, 255, 0.9)',
                        border: '1px solid rgba(0, 234, 255, 0.3)',
                        borderRadius: '8px',
                        '& .MuiAlert-icon': {
                            color: '#00eaff',
                        },
                        '@media (max-width: 600px)': {
                            m: 0.75,
                            fontSize: '0.7rem',
                            borderRadius: '6px',
                            '& .MuiAlert-icon': {
                                fontSize: '1rem',
                            },
                        },
                        '@media (max-width: 360px)': {
                            m: 0.5,
                            fontSize: '0.65rem',
                            borderRadius: '4px',
                            '& .MuiAlert-icon': {
                                fontSize: '0.9rem',
                            },
                        },
                    }}
                    icon={<AutoAwesome fontSize="small" />}
                >
                    AI connected • Analyzing article data
                </Alert>
            )}

            {/* Messages List */}
            <List
                sx={{
                    flex: 1,
                    overflow: 'auto',
                    p: 1,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 1,
                    '@media (max-width: 600px)': {
                        p: 0.75,
                        gap: 0.75,
                    },
                    '@media (max-width: 360px)': {
                        p: 0.5,
                        gap: 0.5,
                    },
                    '&::-webkit-scrollbar': {
                        width: '6px',
                        '@media (max-width: 600px)': {
                            width: '4px',
                        },
                    },
                    '&::-webkit-scrollbar-track': {
                        background: 'rgba(255, 106, 0, 0.1)',
                        borderRadius: '3px',
                    },
                    '&::-webkit-scrollbar-thumb': {
                        background: 'rgba(255, 106, 0, 0.3)',
                        borderRadius: '3px',
                        '&:hover': {
                            background: 'rgba(255, 106, 0, 0.5)',
                        }
                    },
                }}
            >
                {messages.map((message) => (
                    <ListItem
                        key={message.id}
                        sx={{
                            alignSelf: message.sender === 'user' ? 'flex-end' : 'flex-start',
                            maxWidth: '85%',
                            p: 0,
                            '@media (max-width: 600px)': {
                                maxWidth: '90%',
                            },
                            '@media (max-width: 360px)': {
                                maxWidth: '95%',
                            },
                        }}
                    >
                        <MessageBubble
                            elevation={0}
                            sender={message.sender}
                            sx={{
                                border: message.hasChart ? '2px solid #ff6a00' : undefined,
                                boxShadow: message.hasChart ? '0 0 16px rgba(255, 106, 0, 0.4)' : undefined,
                            }}
                        >
                            <ListItemText
                                primary={
                                    <Box>
                                        <Typography
                                            sx={{
                                                fontSize: '0.9rem',
                                                lineHeight: 1.4,
                                                whiteSpace: 'pre-line',
                                                color: message.sender === 'user' ? 'white' : 'rgba(255, 255, 255, 0.9)',
                                                '@media (max-width: 600px)': {
                                                    fontSize: '0.85rem',
                                                    lineHeight: 1.3,
                                                },
                                                '@media (max-width: 360px)': {
                                                    fontSize: '0.8rem',
                                                    lineHeight: 1.2,
                                                },
                                            }}
                                        >
                                            {message.text}
                                        </Typography>
                                        <Box sx={{
                                            marginTop: '8px',
                                            display: 'flex',
                                            justifyContent: 'space-between',
                                            alignItems: 'center',
                                            '@media (max-width: 600px)': {
                                                marginTop: '6px',
                                                flexWrap: 'wrap',
                                                gap: '4px',
                                            },
                                        }}>
                                            <Typography
                                                variant="caption"
                                                sx={{
                                                    color: message.sender === 'user' ? 'rgba(255,255,255,0.7)' : 'rgba(255,255,255,0.6)',
                                                    fontSize: '0.7rem',
                                                    '@media (max-width: 600px)': {
                                                        fontSize: '0.65rem',
                                                    },
                                                    '@media (max-width: 360px)': {
                                                        fontSize: '0.6rem',
                                                    },
                                                }}
                                            >
                                                {message.timestamp.toLocaleTimeString()}
                                            </Typography>
                                            {message.context && (
                                                <Chip
                                                    label="Context"
                                                    size="small"
                                                    sx={{
                                                        height: 16,
                                                        fontSize: '0.6rem',
                                                        bgcolor: message.sender === 'user' ? 'rgba(255,255,255,0.2)' : 'rgba(255, 106, 0, 0.3)',
                                                        color: 'white',
                                                        '@media (max-width: 600px)': {
                                                            height: 14,
                                                            fontSize: '0.55rem',
                                                        },
                                                        '@media (max-width: 360px)': {
                                                            height: 12,
                                                            fontSize: '0.5rem',
                                                        },
                                                    }}
                                                />
                                            )}
                                            {message.hasChart && (
                                                <Chip
                                                    icon={<ChartIcon sx={{
                                                        fontSize: '0.6rem',
                                                        '@media (max-width: 600px)': {
                                                            fontSize: '0.55rem',
                                                        },
                                                        '@media (max-width: 360px)': {
                                                            fontSize: '0.5rem',
                                                        },
                                                    }} />}
                                                    label="Chart"
                                                    size="small"
                                                    sx={{
                                                        height: 16,
                                                        fontSize: '0.6rem',
                                                        bgcolor: '#e63946',
                                                        color: 'white',
                                                        '@media (max-width: 600px)': {
                                                            height: 14,
                                                            fontSize: '0.55rem',
                                                        },
                                                        '@media (max-width: 360px)': {
                                                            height: 12,
                                                            fontSize: '0.5rem',
                                                        },
                                                    }}
                                                />
                                            )}
                                            {message.hasAnalysis && (
                                                <Chip
                                                    icon={<ChartIcon sx={{
                                                        fontSize: '0.6rem',
                                                        '@media (max-width: 600px)': {
                                                            fontSize: '0.55rem',
                                                        },
                                                        '@media (max-width: 360px)': {
                                                            fontSize: '0.5rem',
                                                        },
                                                    }} />}
                                                    label="Analyzed"
                                                    size="small"
                                                    sx={{
                                                        height: 16,
                                                        fontSize: '0.6rem',
                                                        bgcolor: '#00b4d8',
                                                        color: 'white',
                                                        '@media (max-width: 600px)': {
                                                            height: 14,
                                                            fontSize: '0.55rem',
                                                        },
                                                        '@media (max-width: 360px)': {
                                                            height: 12,
                                                            fontSize: '0.5rem',
                                                        },
                                                    }}
                                                />
                                            )}
                                        </Box>
                                    </Box>
                                }
                            />
                        </MessageBubble>
                    </ListItem>
                ))}
                {isLoading && (
                    <ListItem sx={{
                        alignSelf: 'flex-start',
                        maxWidth: '85%',
                        p: 0,
                        '@media (max-width: 600px)': {
                            maxWidth: '90%',
                        },
                        '@media (max-width: 360px)': {
                            maxWidth: '95%',
                        },
                    }}>
                        <MessageBubble
                            elevation={0}
                            sender="bot"
                            sx={{
                                background: 'linear-gradient(135deg, rgba(255, 106, 0, 0.2) 0%, rgba(255, 106, 0, 0.1) 100%)',
                                border: '1px solid rgba(255, 106, 0, 0.3)',
                                animation: 'pulse 2s infinite',
                            }}
                        >
                            <Typography variant="body2" sx={{
                                fontStyle: 'italic',
                                color: 'rgba(255, 255, 255, 0.9)',
                                '@media (max-width: 600px)': {
                                    fontSize: '0.85rem',
                                },
                                '@media (max-width: 360px)': {
                                    fontSize: '0.8rem',
                                },
                            }}>
                                AI is analyzing and generating response...
                            </Typography>
                        </MessageBubble>
                    </ListItem>
                )}
                <div ref={messagesEndRef} />
            </List>

            <Divider sx={{ borderColor: 'rgba(255, 106, 0, 0.2)' }} />

            {/* Memory Indicator */}
            {conversationMemory.length > 0 && (
                <Box sx={{
                    px: 2,
                    py: 1,
                    background: 'linear-gradient(135deg, rgba(255, 106, 0, 0.05) 0%, rgba(0, 234, 255, 0.02) 100%)',
                    borderTop: '1px solid rgba(255, 106, 0, 0.1)'
                }}>
                    <Typography variant="caption" sx={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: 0.5,
                        color: 'rgba(255, 255, 255, 0.7)',
                        fontSize: '0.7rem'
                    }}>
                        <MemoryIcon fontSize="small" sx={{ color: '#ff6a00' }} />
                        Memory: {conversationMemory.length} messages
                    </Typography>
                </Box>
            )}

            {/* Input Area */}
            <Box sx={{
                p: 2,
                display: 'flex',
                gap: 1,
                '@media (max-width: 600px)': {
                    p: 1.5,
                    gap: 0.75,
                },
                '@media (max-width: 360px)': {
                    p: 1,
                    gap: 0.5,
                },
            }}>
                <StyledTextField
                    fullWidth
                    variant="outlined"
                    placeholder={currentGroupId ? "Ask about this article..." : "Ask about the news..."}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={handleKeyPress}
                    disabled={isLoading}
                    size="small"
                    multiline
                    maxRows={3}
                    sx={{
                        '@media (max-width: 600px)': {
                            '& .MuiOutlinedInput-root': {
                                fontSize: '0.9rem',
                            },
                            '& .MuiInputBase-input::placeholder': {
                                fontSize: '0.85rem',
                            },
                        },
                        '@media (max-width: 360px)': {
                            '& .MuiOutlinedInput-root': {
                                fontSize: '0.85rem',
                            },
                            '& .MuiInputBase-input::placeholder': {
                                fontSize: '0.8rem',
                            },
                        },
                    }}
                />
                <IconButton
                    onClick={handleSend}
                    disabled={isLoading || !input.trim()}
                    sx={{
                        alignSelf: 'flex-end',
                        background: 'linear-gradient(45deg, #ff6a00, #00eaff)',
                        color: 'white',
                        width: '40px',
                        height: '40px',
                        '&:hover': {
                            background: 'linear-gradient(45deg, #00eaff, #ff6a00)',
                            transform: 'scale(1.05)',
                        },
                        '&:disabled': {
                            background: 'rgba(255, 106, 0, 0.2)',
                            color: 'rgba(255, 255, 255, 0.3)',
                        },
                        '@media (max-width: 600px)': {
                            width: '36px',
                            height: '36px',
                        },
                        '@media (max-width: 360px)': {
                            width: '32px',
                            height: '32px',
                        },
                    }}
                >
                    <SendIcon sx={{
                        '@media (max-width: 600px)': {
                            fontSize: '1.1rem',
                        },
                        '@media (max-width: 360px)': {
                            fontSize: '1rem',
                        },
                    }} />
                </IconButton>
            </Box>

            {/* Quick Actions */}
            <Box sx={{
                px: 2,
                pb: 2,
                display: 'flex',
                gap: 0.5,
                flexWrap: 'wrap',
                '@media (max-width: 600px)': {
                    px: 1.5,
                    pb: 1.5,
                    gap: 0.4,
                },
                '@media (max-width: 360px)': {
                    px: 1,
                    pb: 1,
                    gap: 0.3,
                },
            }}>
                <QuickActionChip
                    label="Summarize"
                    size="small"
                    onClick={() => sendQuickMessage("Can you summarize this article?")}
                    sx={{
                        '@media (max-width: 600px)': {
                            fontSize: '0.7rem',
                            height: '28px',
                        },
                        '@media (max-width: 360px)': {
                            fontSize: '0.65rem',
                            height: '26px',
                        },
                    }}
                />
                <QuickActionChip
                    label="Key Points"
                    size="small"
                    onClick={() => sendQuickMessage("What are the key points?")}
                    sx={{
                        '@media (max-width: 600px)': {
                            fontSize: '0.7rem',
                            height: '28px',
                        },
                        '@media (max-width: 360px)': {
                            fontSize: '0.65rem',
                            height: '26px',
                        },
                    }}
                />
                <QuickActionChip
                    icon={<ChartIcon sx={{
                        fontSize: '0.7rem',
                        '@media (max-width: 600px)': {
                            fontSize: '0.6rem',
                        },
                        '@media (max-width: 360px)': {
                            fontSize: '0.55rem',
                        },
                    }} />}
                    label="5W1H"
                    size="small"
                    onClick={() => sendAnalysisRequest()}
                    sx={{
                        background: 'linear-gradient(45deg, #00b4d8, #0077b6)',
                        '@media (max-width: 600px)': {
                            fontSize: '0.7rem',
                            height: '28px',
                        },
                        '@media (max-width: 360px)': {
                            fontSize: '0.65rem',
                            height: '26px',
                        },
                    }}
                />
            </Box>
        </Box>
    );
};

export default ChatBot; 