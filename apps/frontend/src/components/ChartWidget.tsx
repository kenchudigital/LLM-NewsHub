import React from 'react';
import {
    Box,
    Paper,
    Typography,
    IconButton,
    Card,
    CardContent,
    CardHeader,
} from '@mui/material';
import { Close as CloseIcon, BarChart, TrendingUp, PieChart } from '@mui/icons-material';
import {
    BarChart as RechartsBarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    Legend,
    ResponsiveContainer,
    LineChart,
    Line,
    PieChart as RechartsPieChart,
    Pie,
    Cell,
    Area,
    AreaChart,
} from 'recharts';

export interface ChartData {
    id: string;
    type: 'bar' | 'line' | 'pie' | 'area';
    title: string;
    description?: string;
    data: any[];
    xKey?: string;
    yKey?: string;
    colors?: string[];
}

interface ChartWidgetProps {
    chartData: ChartData;
    onClose: (chartId: string) => void;
}

const COLORS = ['#e63946', '#1d3557', '#457b9d', '#a8dadc', '#f1faee', '#2a9d8f', '#e9c46a', '#f4a261'];

const ChartWidget: React.FC<ChartWidgetProps> = ({ chartData, onClose }) => {
    const renderChart = () => {
        const { type, data, xKey = 'name', yKey = 'value', colors = COLORS } = chartData;

        switch (type) {
            case 'bar':
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <RechartsBarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey={xKey} />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey={yKey} fill={colors[0]} />
                        </RechartsBarChart>
                    </ResponsiveContainer>
                );

            case 'line':
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey={xKey} />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey={yKey} stroke={colors[0]} strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                );

            case 'area':
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey={xKey} />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Area type="monotone" dataKey={yKey} stroke={colors[0]} fill={colors[0]} fillOpacity={0.6} />
                        </AreaChart>
                    </ResponsiveContainer>
                );

            case 'pie':
                return (
                    <ResponsiveContainer width="100%" height={300}>
                        <RechartsPieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, percent }: { name: any; percent: any }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey={yKey}
                            >
                                {data.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                        </RechartsPieChart>
                    </ResponsiveContainer>
                );

            default:
                return <Typography>Unsupported chart type</Typography>;
        }
    };

    const getChartIcon = () => {
        switch (chartData.type) {
            case 'bar':
                return <BarChart />;
            case 'line':
            case 'area':
                return <TrendingUp />;
            case 'pie':
                return <PieChart />;
            default:
                return <BarChart />;
        }
    };

    return (
        <Card
            sx={{
                mb: 3,
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
                border: '1px solid #e0e0e0',
                borderRadius: '12px',
                overflow: 'hidden',
                animation: 'fadeIn 0.5s ease-in-out',
                '@keyframes fadeIn': {
                    from: { opacity: 0, transform: 'translateY(20px)' },
                    to: { opacity: 1, transform: 'translateY(0)' },
                },
            }}
        >
            <CardHeader
                avatar={getChartIcon()}
                action={
                    <IconButton
                        onClick={() => onClose(chartData.id)}
                        size="small"
                        sx={{
                            color: 'grey.500',
                            '&:hover': {
                                color: 'error.main',
                                backgroundColor: 'error.light',
                            },
                        }}
                    >
                        <CloseIcon />
                    </IconButton>
                }
                title={
                    <Typography variant="h6" sx={{ fontWeight: 600, color: '#1d3557' }}>
                        {chartData.title}
                    </Typography>
                }
                subheader={chartData.description}
                sx={{
                    backgroundColor: '#f8f9fa',
                    borderBottom: '1px solid #e0e0e0',
                }}
            />
            <CardContent>
                <Box sx={{ width: '100%', height: 300 }}>
                    {renderChart()}
                </Box>
            </CardContent>
        </Card>
    );
};

export default ChartWidget; 