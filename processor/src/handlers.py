import src.swearjar as swearjar


def transcribe_postprocessor(event, context):
    swearjar.move_transcription_output(event['detail']['TranscriptionJobName'])
    return 0


def reprocess_all_postprocessors(event, context):
    pass
