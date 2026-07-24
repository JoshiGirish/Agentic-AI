import feedparser

d = feedparser.parse('https://www.artificialintelligence-news.com/feed')

print(d.feed.title)
print(d.feed.link)

for entry in d.entries:
    print(entry.title, entry.published)