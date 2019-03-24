## Process

1. Get unprocessed podcasts by comparing `raw/` and podcast rss feed
2. Copy podcast mp3/mp4/wav/flac to `scratch`
3. Trigger Transcribe Jobs
4. Copy Transcribed files to `raw/<episode_id>`
5. Process raw transcription to get Profanity and copy results to `processed/<episode_id>.json`
6. Merge results together into `results.json`


## Files

- **SwearWords Dictionary:** A list of profanities | `dictionary.json`
- **Raw Podcast Results:** The Podcast after being processed by Transcribe | `raw/<podcast_name>.json`
- **Processed Podcast Results:** The Podcast after being filtered through the dictionary | `processed/<podcast_name>.json`
- **MergedResults:** Merged the Swear Dictionary Together | `merged.json`

## Processed Merged File

Raw File:
```json
[
  {
    "Podcast": "A",
    "Words" : {
      "WordA": 5,
      "WordB": 7
    }
  },
  {
    ...
  }
]
```