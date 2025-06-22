import React, { useState, useEffect } from 'react';
import {
    Box,
    Card,
    CardContent,
    CardMedia,
    Typography,
    Grid,
    Tabs,
    Tab,
    TextField,
    InputAdornment,
    IconButton,
    Pagination,
    Paper,
    Chip,
    Divider,
    LinearProgress,
} from '@mui/material';
import { Search as SearchIcon, Schedule, LocationOn, TrendingUp, Warning, ThumbUp, ThumbDown } from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import ChartWidget, { ChartData } from './ChartWidget';

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

interface ArticleDetail {
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

// Styled components
const ArticleDetailContainer = styled(Paper)(({ theme }) => ({
    marginTop: '2rem',
    padding: '2rem',
    borderRadius: '12px',
    boxShadow: '0 5px 15px rgba(0, 0, 0, 0.1)',
}));

const SectionTitle = styled(Typography)(({ theme }) => ({
    fontSize: '1.5rem',
    fontWeight: 600,
    color: '#1d3557',
    marginTop: '2rem',
    marginBottom: '1rem',
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

interface NewsWithDetailProps {
    onArticleSelect: (groupId: string, date: string) => void;
    onChartAdd: (chartData: ChartData) => void;
}

const NewsSection: React.FC<NewsWithDetailProps> = ({ onArticleSelect, onChartAdd }) => {
    const [articles, setArticles] = useState<NewsArticle[]>([]);
    const [selectedArticle, setSelectedArticle] = useState<ArticleDetail | null>(null);
    const [selectedGroupId, setSelectedGroupId] = useState<string>('');
    const [category, setCategory] = useState('all');
    const [search, setSearch] = useState('');
    const [page, setPage] = useState(1);
    const [loading, setLoading] = useState(false);
    const [charts, setCharts] = useState<ChartData[]>([]);
    const articlesPerPage = 3;
    const navigate = useNavigate();
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    const STATIC_URL = `${API_URL}/static`;

    useEffect(() => {
        const fetchArticles = async () => {
            try {
                console.log('Fetching articles in NewsSection...');
                const response = await axios.get(`${API_URL}/api/news`, {
                    params: { category: category !== 'all' ? category : undefined, search },
                });
                console.log('Articles response in NewsSection:', response.data);
                // The response data has a 'news' property containing the array of articles
                setArticles(response.data.news || []);

                // Auto-select first article if none selected
                if (response.data.news?.length > 0 && !selectedGroupId) {
                    handleArticleClick(response.data.news[0]);
                }
            } catch (error) {
                console.error('Error fetching articles:', error);
                setArticles([]);
            }
        };

        fetchArticles();
    }, [category, search]);

    const fetchArticleDetail = async (groupId: string, date: string) => {
        try {
            setLoading(true);
            const response = await axios.get(
                `${API_URL}/api/articles/${date}/${groupId}`
            );
            setSelectedArticle(response.data);
        } catch (error) {
            console.error('Error fetching article detail:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleCategoryChange = (event: React.SyntheticEvent, newValue: string) => {
        setCategory(newValue);
        setPage(1);
    };

    const handleSearchChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        setSearch(event.target.value);
        setPage(1);
    };

    const handlePageChange = (event: React.ChangeEvent<unknown>, value: number) => {
        setPage(value);
    };

    const handleArticleClick = (article: NewsArticle) => {
        setSelectedGroupId(article.group_id);
        fetchArticleDetail(article.group_id, article.date);
        onArticleSelect(article.group_id, article.date);

        // Scroll to article detail
        setTimeout(() => {
            const detailElement = document.getElementById('article-detail');
            if (detailElement) {
                detailElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }, 100);
    };

    const handleChartReceived = (chartData: ChartData) => {
        setCharts(prev => [...prev, chartData]);
        onChartAdd(chartData);

        // Scroll to the new chart
        setTimeout(() => {
            const chartElement = document.getElementById(`chart-${chartData.id}`);
            if (chartElement) {
                chartElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
            }
        }, 100);
    };

    const handleChartClose = (chartId: string) => {
        setCharts(prev => prev.filter(chart => chart.id !== chartId));
    };

    const filteredArticles = articles.slice(
        (page - 1) * articlesPerPage,
        page * articlesPerPage
    );

    const renderSourceLinks = (content: string, sources: string[]) => {
        let processedContent = content;
        sources.forEach((source, index) => {
            const refNumber = index + 1;
            processedContent = processedContent.replace(
                new RegExp(`\\(([^)]*${source.split('/').pop()}[^)]*)\\)`, 'gi'),
                `<a href="${source}" target="_blank" rel="noopener noreferrer" class="source-ref">[${refNumber}]</a>`
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

    // Expose chart handler to parent component
    React.useEffect(() => {
        (window as any).addChart = handleChartReceived;
        return () => {
            delete (window as any).addChart;
        };
    }, []);

    return (
        <Box>
            <Box sx={{ mb: 4 }}>
                <TextField
                    fullWidth
                    variant="outlined"
                    placeholder="Search news..."
                    value={search}
                    onChange={handleSearchChange}
                    InputProps={{
                        startAdornment: (
                            <InputAdornment position="start">
                                <SearchIcon />
                            </InputAdornment>
                        ),
                    }}
                    sx={{ mb: 2 }}
                />
                <Tabs
                    value={category}
                    onChange={handleCategoryChange}
                    variant="scrollable"
                    scrollButtons="auto"
                    sx={{ borderBottom: 1, borderColor: 'divider' }}
                >
                    <Tab label="ALL" value="all" />
                    <Tab label="Social" value="social" />
                    <Tab label="Entertainment" value="entertainment" />
                    <Tab label="Technology" value="tech" />
                    <Tab label="Sport" value="sport" />
                </Tabs>
            </Box>

            <Grid container spacing={3}>
                {filteredArticles.map((article) => (
                    <Grid item xs={12} sm={6} md={4} key={article.id}>
                        <Card
                            sx={{
                                height: '100%',
                                display: 'flex',
                                flexDirection: 'column',
                                cursor: 'pointer',
                                border: selectedGroupId === article.group_id ? '2px solid #e63946' : '2px solid transparent',
                                '&:hover': {
                                    boxShadow: 6,
                                    transform: 'translateY(-4px)',
                                    transition: 'all 0.3s ease-in-out',
                                },
                            }}
                            onClick={() => handleArticleClick(article)}
                        >
                            {article.image_url && (
                                <CardMedia
                                    component="img"
                                    height="140"
                                    image={`${STATIC_URL}${article.image_url}`}
                                    alt={article.headline}
                                    onError={(e) => {
                                        (e.target as HTMLImageElement).src = 'https://images.unsplash.com/photo-1504711434969-e33886168f5c?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=80';
                                    }}
                                />
                            )}
                            <CardContent sx={{ flexGrow: 1 }}>
                                <Typography
                                    gutterBottom
                                    variant="h6"
                                    component="h2"
                                    sx={{
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        display: '-webkit-box',
                                        WebkitLineClamp: 2,
                                        WebkitBoxOrient: 'vertical',
                                    }}
                                >
                                    {article.headline}
                                </Typography>
                                <Typography
                                    variant="body2"
                                    color="text.secondary"
                                    sx={{
                                        overflow: 'hidden',
                                        textOverflow: 'ellipsis',
                                        display: '-webkit-box',
                                        WebkitLineClamp: 3,
                                        WebkitBoxOrient: 'vertical',
                                    }}
                                >
                                    {article.summary}
                                </Typography>
                                <Typography
                                    variant="caption"
                                    color="text.secondary"
                                    sx={{ display: 'block', mt: 1 }}
                                >
                                    {new Date(article.date).toLocaleDateString()}
                                </Typography>
                            </CardContent>
                        </Card>
                    </Grid>
                ))}
            </Grid>

            {articles.length > articlesPerPage && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                    <Pagination
                        count={Math.ceil(articles.length / articlesPerPage)}
                        page={page}
                        onChange={handlePageChange}
                        color="primary"
                    />
                </Box>
            )}

            {/* Charts Section */}
            {charts.map((chart) => (
                <Box key={chart.id} id={`chart-${chart.id}`}>
                    <ChartWidget chartData={chart} onClose={handleChartClose} />
                </Box>
            ))}

            {/* Article Detail Section */}
            {selectedArticle && (
                <ArticleDetailContainer id="article-detail">
                    {loading && <LinearProgress sx={{ mb: 2 }} />}

                    <Box sx={{ mb: 3 }}>
                        <Chip
                            label={selectedArticle.category.toUpperCase()}
                            sx={{
                                bgcolor: '#e63946',
                                color: 'white',
                                fontWeight: 600,
                                mb: 2,
                            }}
                        />
                        <Typography
                            variant="h3"
                            sx={{
                                fontSize: '2.5rem',
                                fontWeight: 700,
                                color: '#1d3557',
                                mb: 1,
                                lineHeight: 1.3,
                            }}
                        >
                            {selectedArticle.headline}
                        </Typography>
                        {selectedArticle.subheadline && (
                            <Typography
                                variant="h5"
                                sx={{
                                    color: '#666',
                                    fontWeight: 400,
                                    mb: 2,
                                    fontStyle: 'italic',
                                }}
                            >
                                {selectedArticle.subheadline}
                            </Typography>
                        )}
                    </Box>

                    {/* Meta Information */}
                    <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: '#666' }}>
                            <Schedule fontSize="small" />
                            <Typography variant="caption">
                                {new Date().toLocaleDateString()}
                            </Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: '#666' }}>
                            <LocationOn fontSize="small" />
                            <Typography variant="caption">Multiple Regions</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: '#666' }}>
                            <TrendingUp fontSize="small" />
                            <Typography variant="caption">Trending</Typography>
                        </Box>
                    </Box>

                    {/* Cover Image */}
                    <Box sx={{ mb: 3 }}>
                        <img
                            src={`${STATIC_URL}/images/2025-06-14/${selectedGroupId}.jpg`}
                            alt={selectedArticle.headline}
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

                    {/* Leading Paragraph */}
                    <LeadParagraph>{selectedArticle.lead}</LeadParagraph>

                    {/* Article Body */}
                    {selectedArticle.body.map((section, index) => (
                        <Box key={index} sx={{ mb: 4 }}>
                            <SectionTitle variant="h4">{section.section}</SectionTitle>

                            {/* Sentiment and Fake News Indicators */}
                            <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
                                <SentimentIndicator sentiment={parseFloat(section.sentisement_from_the_content)}>
                                    {parseFloat(section.sentisement_from_the_content) > 0 ? (
                                        <ThumbUp fontSize="small" />
                                    ) : (
                                        <ThumbDown fontSize="small" />
                                    )}
                                    Sentiment: {parseFloat(section.sentisement_from_the_content) > 0 ? 'Positive' : 'Negative'}
                                </SentimentIndicator>

                                <FakeNewsIndicator probability={section.fake_news_probability}>
                                    <Warning fontSize="small" />
                                    Reliability: {section.fake_news_probability > 0.7 ? 'Low' : section.fake_news_probability > 0.4 ? 'Medium' : 'High'}
                                </FakeNewsIndicator>

                                <Box
                                    sx={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '0.5rem',
                                        padding: '0.5rem 1rem',
                                        borderRadius: '20px',
                                        fontSize: '0.9rem',
                                        fontWeight: 500,
                                        background: calculateRegionDiversityScore(section.Publisher_region_diversity) === 'High' ? '#d4edda'
                                            : calculateRegionDiversityScore(section.Publisher_region_diversity) === 'Medium' ? '#fff3cd' : '#f8d7da',
                                        color: calculateRegionDiversityScore(section.Publisher_region_diversity) === 'High' ? '#155724'
                                            : calculateRegionDiversityScore(section.Publisher_region_diversity) === 'Medium' ? '#856404' : '#721c24',
                                        cursor: 'help'
                                    }}
                                    title={`Publisher Region Diversity: ${section.Publisher_region_diversity.join(', ')} | Unique Regions: ${new Set(section.Publisher_region_diversity).size}`}
                                >
                                    <LocationOn fontSize="small" />
                                    Diversity: {calculateRegionDiversityScore(section.Publisher_region_diversity)}
                                </Box>
                            </Box>

                            <Typography
                                variant="body1"
                                sx={{
                                    fontSize: '1.1rem',
                                    lineHeight: 1.8,
                                    color: '#444',
                                    mb: 2,
                                }}
                                dangerouslySetInnerHTML={{
                                    __html: renderSourceLinks(section.content, section.sources)
                                }}
                            />

                            {/* Publishers */}
                            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                                {section.Publishers.map((publisher, idx) => (
                                    <Chip
                                        key={idx}
                                        label={publisher}
                                        size="small"
                                        variant="outlined"
                                    />
                                ))}
                            </Box>
                        </Box>
                    ))}

                    {/* Conclusion */}
                    <Divider sx={{ my: 3 }} />
                    <SectionTitle variant="h4">Conclusion</SectionTitle>
                    <Typography
                        variant="body1"
                        sx={{
                            fontSize: '1.1rem',
                            lineHeight: 1.8,
                            color: '#444',
                        }}
                    >
                        {selectedArticle.conclusion}
                    </Typography>

                    {/* Timeline */}
                    {Object.keys(selectedArticle.timeline).length > 0 && (
                        <>
                            <Divider sx={{ my: 3 }} />
                            <SectionTitle variant="h4">Timeline</SectionTitle>
                            <Grid container spacing={2}>
                                {Object.entries(selectedArticle.timeline).map(([time, event], index) => (
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
                </ArticleDetailContainer>
            )}
        </Box>
    );
};

export default NewsSection; 