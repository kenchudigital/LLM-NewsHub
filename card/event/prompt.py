def get_event_card_prompt(news_content: str, image_captions_with_url: list, publishing_date: str) -> str:
    """
    Generate the prompt for event card generation.
    
    Args:
        news_content: The news content to analyze
        image_captions_with_url: List of image captions with URLs
        publishing_date: The publishing date of the news
        
    Returns:
        Formatted prompt string
    """
    return f"""
    <Publishing Date>
    {publishing_date}
    </Publishing Date>

    <News Content>
    {news_content}
    </News Content>

    Image captions with url format should be like this:{{image_captions: url}}
    
    <image captions>
    {chr(10).join(f"{i+1}. {item}" for i, item in enumerate(image_captions_with_url))}
    </image captions>

    Rule:
    1. If the image captions is the evidence of the news, then the image caption and the image url of this caption should be included in the event card.
    2. Some information may be missing in the event card, just fill "Empty" in the field.
    3. The order should be ordered by the event_date and event_time. 
    4. If there is no event_date and event_time, then order by the image_caption. Please use the event description logic to decide the order number.
    5. fake_news_score is the score of the news, it is a number between 0 and 1. You need to think about the pattern of news and the content of the news to decide the fake_news_score. 
    6. ai_generated_score is the score of the news, it is a number between 0 and 1. You need to think about the pattern of news and the frequency of wording of the news to decide the ai_generated_score.
    7. state out the most important keywords in the list_of_keywords which can represent the news.
    8. news_category is the category of the news, it is a string. You can select more than one category from the following: [technology, politic, social, entertainment] if there is no category selected, then it should be ['other']
    
    Extract event details in the following JSON format:
    {{
        "summary": "1-2 sentences summary of the news",
        'news_category': [category1, category2],
        "content_sentiment": "-1 to 1",
        "fake_news_score": "0-1",
        "ai_generated_score": "0-1",
        "list_of_keywords": [keyword1, keyword2],
        "events": [
            {{
                "event_type": "e.g., political, disaster, sports",
                "event_description": "1-2 sentences",
                "event_date": "YYYY-MM-DD or range",
                "event_time": "HH:MM:SS",
                "event_location": ["city", "country"],
                "event_organizer": ["org1", "org2"],
                "event_people_involved": ["name1", "name2"],
                "event_connections": "How this event links to others",
                "statement_or_comment": "Key quote or reaction",
                "statement_source": "source",
                "statement_source_url": "LINK",
                "image_caption": "image caption",
                "image_url": "LINK",
                "order": 1
            }}
        ]
    }}
    """
