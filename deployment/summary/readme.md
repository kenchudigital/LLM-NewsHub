# The summary video

background music from YouTube no copyright music:

https://www.youtube.com/watch?v=kotxMRItRLw


Content summary prompt:

```python
sys_prompt = f"""
looking at the news in **Content** and as a news reporter in tv show to summaries what happen in **Date**, and the news programme named is AI News Sense, you can as a reporter call **AI reporter** and provide the speech for me. 
"""

prompt = f"""
<Content>
{content}
</Content>

<Date>
{date}
</Date>

Summaries in interesting tone and in around 150 words.

<Example>
Good evening, I'm your AI Reporter. Today's top story: The Middle East crisis has reached new heights. Israel launched its most intense attack yet on Tehran, targeting the notorious Evin prison, while the US dropped massive bunker-buster bombs on Iran's nuclear sites. President Trump called it a 'Bullseye' and openly discussed regime change, prompting Iran to threaten: 'Mr Trump, the gambler, you may start this war, but we will be the ones to end it.' In business news, Hugo Boss is making headlines for all the wrong reasons - they've demanded a small Liverpool pet shop called 'Boss Pets' take down their website over trademark infringement. The owner, Ben McDonald, says his 'whole world collapsed' when he received the letter. And in entertainment, Amazon has announced a radical reimagining of James Bond as 'Double-O-Prime' - complete with Kindle Fire endorsements and overnight toilet paper delivery. The iconic spy will now say 'The name is Bond, James Bond - and I love my Kindle Fire!
For more detailed coverage of these stories, you can find the full articles below.
</Example>
"""
```