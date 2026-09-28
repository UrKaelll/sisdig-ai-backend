def analyze_content(slides_data):
    full_text = ""

    for slide in slides_data:
        for content in slide["content"]:
            full_text += content + " "

    full_text = full_text.lower()

    topics = []

    if "sistem bilangan biner" in full_text:
        topics.append({
            "title": "Sistem Bilangan Biner",
            "type": "theory"
        })

    if "desimal-biner" in full_text or "desimal ke biner" in full_text:
        topics.append({
            "title": "Konversi Desimal ke Biner",
            "type": "interactive_conversion"
        })

    if "biner ke desimal" in full_text:
        topics.append({
            "title": "Konversi Biner ke Desimal",
            "type": "interactive_conversion"
        })

    if "oktal" in full_text:
        topics.append({
            "title": "Sistem Bilangan Oktal",
            "type": "theory"
        })

    if "heksa" in full_text or "hex" in full_text:
        topics.append({
            "title": "Sistem Bilangan Heksadesimal",
            "type": "theory"
        })

    return {
        "course": "Sistem Digital",
        "week": 1,
        "title": "Sistem Bilangan Digital",
        "learning_objectives": [
            "Memahami sistem bilangan biner",
            "Memahami basis dan digit pada sistem bilangan",
            "Melakukan konversi desimal ke biner",
            "Melakukan konversi biner ke desimal",
            "Memahami sistem bilangan oktal dan heksadesimal"
        ],
        "topics": topics
    }