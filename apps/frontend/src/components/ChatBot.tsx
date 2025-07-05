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
} from '@mui/material';
import { Send as SendIcon, Article as ArticleIcon, Memory as MemoryIcon, BarChart as ChartIcon, AutoAwesome } from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import axios from 'axios';
import { ChartData } from './ChartWidget';

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
    background: 'linear-gradient(135deg, rgba(255, 106, 0, 0.8) 0%, rgba(255, 106, 0, 0.6) 100%)',
    color: 'white',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderBottom: '1px solid rgba(255, 106, 0, 0.3)',
    position: 'relative',
    zIndex: 1,
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
        '& fieldset': {
            borderColor: 'rgba(255, 106, 0, 0.3)',
        },
        '&:hover fieldset': {
            borderColor: 'rgba(255, 106, 0, 0.5)',
        },
        '&.Mui-focused fieldset': {
            borderColor: '#ff6a00',
        },
    },
    '& .MuiInputBase-input::placeholder': {
        color: 'rgba(255, 255, 255, 0.5)',
    },
}));

interface Message {
    id: number;
    text: string;
    sender: 'user' | 'bot';
    timestamp: Date;
    context?: string;
    hasChart?: boolean;
}

interface ChatBotProps {
    currentGroupId?: string;
    currentDate?: string;
}

const ChatBot: React.FC<ChatBotProps> = ({ currentGroupId, currentDate }) => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [conversationMemory, setConversationMemory] = useState<string[]>([]);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    // Fix API URL - use config.API_URL (empty for proxy) instead of localhost fallback
    const API_URL = config.API_URL;

    // Auto-scroll to bottom when new messages arrive
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Initialize with welcome message
    useEffect(() => {
        if (messages.length === 0) {
            const welcomeMessage: Message = {
                id: Date.now(),
                text: "Hello! I'm your AI news assistant powered by advanced language models. I can help you understand articles, provide summaries, analyze data, and create visualizations. What would you like to know?",
                sender: 'bot',
                timestamp: new Date(),
            };
            setMessages([welcomeMessage]);
        }
    }, []);

    // Update context when article changes
    useEffect(() => {
        if (currentGroupId && currentDate) {
            const contextMessage: Message = {
                id: Date.now(),
                text: `I'm now analyzing the article you're reading (ID: ${currentGroupId}). I have access to the full article content, sources, and related resources. I can create charts, provide analysis, or answer any questions about this specific article!`,
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
        setInput('');
        setIsLoading(true);

        try {
            const response = await axios.post(`${API_URL}/api/chat`, {
                message: userInput,
                context: {
                    currentGroupId,
                    currentDate,
                    conversationHistory: conversationMemory,
                },
            });

            let botResponseText = response.data.response;
            let chartGenerated = false;

            // Check if the backend returned chart data
            if (response.data.chart_data) {
                const chartData: ChartData = response.data.chart_data;

                // Add chart to the page
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

            setMessages((prev) => [...prev, botMessage]);

            // Add bot response to memory
            setConversationMemory(prev => [...prev.slice(-4), response.data.response]);

        } catch (error) {
            console.error('Error sending message:', error);
            let errorMessage = 'Sorry, I encountered an error. Please try again later.';

            if (axios.isAxiosError(error)) {
                if (error.response?.status === 500) {
                    errorMessage = 'The AI service is currently unavailable. Please check if the API keys are configured properly.';
                } else if (error.response?.data?.detail) {
                    errorMessage = `Error: ${error.response.data.detail}`;
                }
            }

            const errorMsg: Message = {
                id: Date.now() + 1,
                text: errorMessage,
                sender: 'bot',
                timestamp: new Date(),
            };
            setMessages((prev) => [...prev, errorMsg]);
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
        const welcomeMessage: Message = {
            id: Date.now(),
            text: "Conversation cleared! How can I help you with the current article?",
            sender: 'bot',
            timestamp: new Date(),
        };
        setMessages([welcomeMessage]);
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
            position: 'relative'
        }}>
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
                    }}
                    icon={<AutoAwesome fontSize="small" />}
                >
                    🤖 AI connected • Analyzing article data
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
                    '&::-webkit-scrollbar': {
                        width: '6px',
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
                                            }}
                                        >
                                            {message.text}
                                        </Typography>
                                        <Box sx={{ marginTop: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                            <Typography
                                                variant="caption"
                                                sx={{
                                                    color: message.sender === 'user' ? 'rgba(255,255,255,0.7)' : 'rgba(255,255,255,0.6)',
                                                    fontSize: '0.7rem',
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
                                                    }}
                                                />
                                            )}
                                            {message.hasChart && (
                                                <Chip
                                                    icon={<ChartIcon sx={{ fontSize: '0.6rem' }} />}
                                                    label="Chart"
                                                    size="small"
                                                    sx={{
                                                        height: 16,
                                                        fontSize: '0.6rem',
                                                        bgcolor: '#e63946',
                                                        color: 'white',
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
                    <ListItem sx={{ alignSelf: 'flex-start', maxWidth: '85%', p: 0 }}>
                        <MessageBubble
                            elevation={0}
                            sender="bot"
                            sx={{
                                background: 'linear-gradient(135deg, rgba(255, 106, 0, 0.2) 0%, rgba(255, 106, 0, 0.1) 100%)',
                                border: '1px solid rgba(255, 106, 0, 0.3)',
                                animation: 'pulse 2s infinite',
                            }}
                        >
                            <Typography variant="body2" sx={{ fontStyle: 'italic', color: 'rgba(255, 255, 255, 0.9)' }}>
                                AI is analyzing and generating response...
                            </Typography>
                        </MessageBubble>
                    </ListItem>
                )}
                <div ref={messagesEndRef} />
            </List>

            <Divider sx={{ borderColor: 'rgba(255, 106, 0, 0.2)' }} />

            {/* Memory Indicator - Fixed styling */}
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
            <Box sx={{ p: 2, display: 'flex', gap: 1 }}>
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
                        }
                    }}
                >
                    <SendIcon />
                </IconButton>
            </Box>

            {/* Quick Actions */}
            <Box sx={{ px: 2, pb: 2, display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                <QuickActionChip
                    label="Summarize"
                    size="small"
                    onClick={() => sendQuickMessage("Can you summarize this article?")}
                />
                <QuickActionChip
                    label="Key Points"
                    size="small"
                    onClick={() => sendQuickMessage("What are the key points?")}
                />
                {currentGroupId && (
                    <QuickActionChip
                        icon={<ChartIcon sx={{ fontSize: '0.7rem' }} />}
                        label="Chart"
                        size="small"
                        onClick={() => sendQuickMessage("Create a sentiment chart")}
                        sx={{
                            background: 'linear-gradient(45deg, #ff6a00, #00eaff)',
                        }}
                    />
                )}
            </Box>
        </Box>
    );
};

export default ChatBot; 