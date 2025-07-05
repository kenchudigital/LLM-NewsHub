export interface NewsArticle {
    id: number;
    group_id: string;
    headline: string;
    category: string;
    content: string;
    summary: string;
    date: string;
    image_url?: string;
}

export interface ArticleData {
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

export interface AudioState {
    isPlaying: boolean;
    currentTime: number;
    duration: number;
    audioError: boolean;
    isBookmarked: boolean;
}

export interface AudioHandlers {
    handlePlayPause: () => void;
    handleTimeUpdate: () => void;
    handleLoadedMetadata: () => void;
    resetAudio: () => void;
    checkAudioAvailability: (date: string, groupId: string) => void;
    formatTime: (time: number) => string;
} 