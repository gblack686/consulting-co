# Dynamous Community Knowledge Base

This folder contains curated, high-quality content from the Dynamous community forum.

## Structure

Each post is saved as a JSON file with the following structure:

```json
{
  "title": "Post title",
  "url": "Full URL to the post",
  "category": "Category/topic of the post",
  "date_scraped": "ISO date string",
  "summary": "Brief summary of the post content",
  "value_proposition": "Key value or learning from this post",
  "links": [
    {
      "url": "link URL",
      "description": "what the link is about"
    }
  ],
  "key_insights": [
    "Insight 1",
    "Insight 2"
  ],
  "replies_summary": "Summary of helpful replies if applicable",
  "tags": ["tag1", "tag2"]
}
```

## Categories

Posts are categorized into:
- Tutorials & How-To
- Best Practices
- Architecture & Design
- Integration Examples
- Performance Optimization
- Use Cases
- Feature Discussions
- (Others as discovered)

## Exclusions

We exclude:
- Troubleshooting/bug report posts
- Simple Q&A without substantial value
- Duplicate content
























