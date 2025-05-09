from post_extractor import PostExtractor

posts = [
    {
        "title": "نمونه پست ۱",
        "body": "این یک پست نمونه است با #تست #نمونه",
        "tags": ["#تست", "#نمونه"],
        "author": "علی",
        "created_at": "2025-05-09T10:00:00Z"
    }
]

extractor = PostExtractor('plugins/sample_plugin.json')
results = extractor.process_posts(posts, format_type='text')
for result in results:
    print(result)
