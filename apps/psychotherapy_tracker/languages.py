"""
Language configuration for the Psychotherapy Tracker application.
Supports English, German, and Czech with pre-made monologues.
"""

# Supported languages with their Azure Speech locale codes
LANGUAGES = {
    "en-US": {
        "name": "English",
        "display": "English",
        "speech_locale": "en-US",
    },
    "de-DE": {
        "name": "German",
        "display": "Deutsch",
        "speech_locale": "de-DE",
    },
    "cs-CZ": {
        "name": "Czech",
        "display": "Čeština",
        "speech_locale": "cs-CZ",
    },
}

# Pre-made monologues for each language (5 scenarios)
MONOLOGUES = {
    "en-US": {
        "high_anxiety": {
            "title": "Anxious Thoughts",
            "text": (
                "I've been feeling really anxious lately. My mind keeps racing with all "
                "these worries about work and the future. I can't seem to relax even when "
                "I try. My heart feels like it's beating too fast sometimes, and I keep "
                "thinking about everything that could go wrong. It's hard to focus on "
                "anything else when these thoughts keep coming."
            ),
        },
        "low_mood": {
            "title": "Feeling Down",
            "text": (
                "Everything feels heavy today. I don't really have the motivation to do "
                "much of anything. I've been feeling sad for a while now, and I'm not "
                "sure why. Things that used to make me happy don't seem to anymore. "
                "I just want to stay in bed and not face the day. It's like there's "
                "this weight on my chest that won't go away."
            ),
        },
        "work_stress": {
            "title": "Work Pressure",
            "text": (
                "Work has been incredibly stressful lately. The deadlines keep piling up "
                "and I feel like I can never catch up. My boss keeps adding more tasks "
                "and I don't know how to say no. I'm working late almost every day and "
                "it's affecting my sleep. I feel like I'm on the edge of burnout but "
                "I don't know what to do about it."
            ),
        },
        "positive_stable": {
            "title": "Good Day",
            "text": (
                "Today has been a really good day actually. I woke up feeling rested "
                "and had a nice breakfast. I got some things done that I've been putting "
                "off and it felt great to check them off my list. I had a nice chat with "
                "a friend and we made plans for the weekend. I'm feeling hopeful about "
                "things and looking forward to what's coming."
            ),
        },
        "mixed_emotions": {
            "title": "Mixed Feelings",
            "text": (
                "It's been an up and down week for me. Some days I feel pretty okay, "
                "like I can handle things. But then other days, everything feels "
                "overwhelming again. I'm trying to take things one day at a time but "
                "it's not always easy. I'm not sure if I'm getting better or just "
                "having good moments. The uncertainty is frustrating."
            ),
        },
    },
    "de-DE": {
        "high_anxiety": {
            "title": "Ängstliche Gedanken",
            "text": (
                "Ich fühle mich in letzter Zeit wirklich ängstlich. Meine Gedanken "
                "kreisen ständig um Sorgen über die Arbeit und die Zukunft. Ich kann "
                "mich einfach nicht entspannen, selbst wenn ich es versuche. Mein Herz "
                "schlägt manchmal zu schnell und ich denke ständig an alles, was "
                "schiefgehen könnte. Es ist schwer, mich auf etwas anderes zu "
                "konzentrieren."
            ),
        },
        "low_mood": {
            "title": "Niedergeschlagen",
            "text": (
                "Heute fühlt sich alles schwer an. Ich habe nicht wirklich die "
                "Motivation, viel zu tun. Ich fühle mich schon eine Weile traurig und "
                "bin mir nicht sicher warum. Dinge, die mich früher glücklich gemacht "
                "haben, tun es nicht mehr. Ich möchte einfach im Bett bleiben und dem "
                "Tag nicht begegnen. Es ist wie ein Gewicht auf meiner Brust."
            ),
        },
        "work_stress": {
            "title": "Arbeitsdruck",
            "text": (
                "Die Arbeit war in letzter Zeit unglaublich stressig. Die Termine "
                "häufen sich und ich habe das Gefühl, dass ich nie aufholen kann. "
                "Mein Chef fügt ständig neue Aufgaben hinzu und ich weiß nicht, wie "
                "ich nein sagen soll. Ich arbeite fast jeden Tag bis spät und es "
                "beeinträchtigt meinen Schlaf. Ich fühle mich am Rande eines Burnouts."
            ),
        },
        "positive_stable": {
            "title": "Guter Tag",
            "text": (
                "Heute war wirklich ein guter Tag. Ich bin ausgeruht aufgewacht und "
                "hatte ein schönes Frühstück. Ich habe einige Dinge erledigt, die ich "
                "aufgeschoben hatte, und es fühlte sich großartig an. Ich hatte ein "
                "nettes Gespräch mit einem Freund und wir haben Pläne fürs Wochenende "
                "gemacht. Ich bin hoffnungsvoll und freue mich auf das, was kommt."
            ),
        },
        "mixed_emotions": {
            "title": "Gemischte Gefühle",
            "text": (
                "Es war eine Woche mit Höhen und Tiefen für mich. An manchen Tagen "
                "fühle ich mich ziemlich okay, als könnte ich die Dinge bewältigen. "
                "Aber dann fühlt sich an anderen Tagen alles wieder überwältigend an. "
                "Ich versuche, alles Tag für Tag zu nehmen, aber es ist nicht immer "
                "einfach. Die Ungewissheit ist frustrierend."
            ),
        },
    },
    "cs-CZ": {
        "high_anxiety": {
            "title": "Úzkostné myšlenky",
            "text": (
                "V poslední době se cítím opravdu úzkostně. Moje myšlenky se neustále "
                "točí kolem starostí o práci a budoucnost. Nedokážu se uvolnit, ani "
                "když se snažím. Srdce mi někdy bije příliš rychle a pořád přemýšlím "
                "o všem, co by se mohlo pokazit. Je těžké soustředit se na něco "
                "jiného, když tyto myšlenky stále přicházejí."
            ),
        },
        "low_mood": {
            "title": "Špatná nálada",
            "text": (
                "Dnes se všechno zdá těžké. Nemám motivaci dělat cokoliv. Už nějakou "
                "dobu se cítím smutně a nejsem si jistý proč. Věci, které mě dříve "
                "těšily, už netěší. Chci jen zůstat v posteli a nečelit dni. Je to "
                "jako bych měl na hrudi nějakou tíhu, která nechce zmizet."
            ),
        },
        "work_stress": {
            "title": "Pracovní tlak",
            "text": (
                "Práce byla v poslední době neuvěřitelně stresující. Termíny se kupí "
                "a mám pocit, že nikdy nedoženu. Šéf mi stále přidává další úkoly a "
                "nevím, jak říct ne. Pracuji do pozdna skoro každý den a ovlivňuje to "
                "můj spánek. Cítím se na pokraji vyhoření, ale nevím, co s tím dělat."
            ),
        },
        "positive_stable": {
            "title": "Dobrý den",
            "text": (
                "Dnes byl opravdu dobrý den. Probudil jsem se odpočatý a dal si "
                "příjemnou snídani. Udělal jsem pár věcí, které jsem odkládal, a bylo "
                "skvělé je odškrtnout ze seznamu. Měl jsem příjemný rozhovor s přítelem "
                "a naplánovali jsme víkend. Cítím se nadějně a těším se na to, co přijde."
            ),
        },
        "mixed_emotions": {
            "title": "Smíšené pocity",
            "text": (
                "Byl to pro mě týden plný vzestupů a pádů. Některé dny se cítím docela "
                "dobře, jako bych zvládal věci. Ale pak se další dny zase všechno zdá "
                "přemáhající. Snažím se brát věci den po dni, ale není to vždy snadné. "
                "Nejistota je frustrující."
            ),
        },
    },
}

# UI translations for each language
UI_TRANSLATIONS = {
    "en-US": {
        "title": "Psychotherapy Tracker",
        "subtitle": "Track your emotional wellness with voice",
        "language": "Language",
        "select_monologue": "Select a sample monologue",
        "sample_text": "Sample text (read this aloud or share your own thoughts)",
        "start_recording": "Start Recording",
        "stop_recording": "Stop Recording",
        "recording": "Recording...",
        "processing": "Analyzing your words...",
        "ready": "Ready to record",
        "sessions_today": "Sessions today",
        "analysis_complete": "Analysis complete",
        "current_session": "Current Session",
        "todays_sessions": "Today's Progress",
        "analysis_report": "Analysis Report",
        "summary": "Summary",
        "key_emotions": "Key Emotions",
        "concerns_themes": "Concerns & Themes",
        "insights": "Insights",
        "transcription": "What you said",
        "try_another": "Want to track how you feel later? Record another session.",
        "disclaimer": "This is a wellness tool, not a medical device. For mental health concerns, please consult a professional.",
        "no_speech": "No speech detected. Please try again.",
        "mic_error": "Could not access microphone. Please check permissions.",
        "processing_error": "Processing failed. Please try again.",
    },
    "de-DE": {
        "title": "Psychotherapie-Tracker",
        "subtitle": "Verfolgen Sie Ihr emotionales Wohlbefinden mit Sprache",
        "language": "Sprache",
        "select_monologue": "Wählen Sie einen Beispielmonolog",
        "sample_text": "Beispieltext (lesen Sie dies laut vor oder teilen Sie Ihre eigenen Gedanken)",
        "start_recording": "Aufnahme starten",
        "stop_recording": "Aufnahme stoppen",
        "recording": "Aufnahme läuft...",
        "processing": "Analysiere Ihre Worte...",
        "ready": "Bereit zur Aufnahme",
        "sessions_today": "Sitzungen heute",
        "analysis_complete": "Analyse abgeschlossen",
        "current_session": "Aktuelle Sitzung",
        "todays_sessions": "Heutiger Fortschritt",
        "analysis_report": "Analysebericht",
        "summary": "Zusammenfassung",
        "key_emotions": "Wichtige Emotionen",
        "concerns_themes": "Bedenken & Themen",
        "insights": "Erkenntnisse",
        "transcription": "Was Sie gesagt haben",
        "try_another": "Möchten Sie später verfolgen, wie Sie sich fühlen? Nehmen Sie eine weitere Sitzung auf.",
        "disclaimer": "Dies ist ein Wellness-Tool, kein medizinisches Gerät. Bei psychischen Problemen wenden Sie sich bitte an einen Fachmann.",
        "no_speech": "Keine Sprache erkannt. Bitte versuchen Sie es erneut.",
        "mic_error": "Konnte nicht auf das Mikrofon zugreifen. Bitte überprüfen Sie die Berechtigungen.",
        "processing_error": "Verarbeitung fehlgeschlagen. Bitte versuchen Sie es erneut.",
    },
    "cs-CZ": {
        "title": "Psychoterapeutický tracker",
        "subtitle": "Sledujte své emocionální zdraví pomocí hlasu",
        "language": "Jazyk",
        "select_monologue": "Vyberte ukázkový monolog",
        "sample_text": "Ukázkový text (přečtěte nahlas nebo sdílejte své vlastní myšlenky)",
        "start_recording": "Zahájit nahrávání",
        "stop_recording": "Zastavit nahrávání",
        "recording": "Nahrávání...",
        "processing": "Analyzuji vaše slova...",
        "ready": "Připraveno k nahrávání",
        "sessions_today": "Dnešní sezení",
        "analysis_complete": "Analýza dokončena",
        "current_session": "Aktuální sezení",
        "todays_sessions": "Dnešní pokrok",
        "analysis_report": "Analytická zpráva",
        "summary": "Shrnutí",
        "key_emotions": "Klíčové emoce",
        "concerns_themes": "Obavy a témata",
        "insights": "Postřehy",
        "transcription": "Co jste řekli",
        "try_another": "Chcete později sledovat, jak se cítíte? Nahrajte další sezení.",
        "disclaimer": "Toto je wellness nástroj, nikoli zdravotnický přístroj. V případě psychických problémů se prosím poraďte s odborníkem.",
        "no_speech": "Nebyla detekována žádná řeč. Zkuste to prosím znovu.",
        "mic_error": "Nelze získat přístup k mikrofonu. Zkontrolujte prosím oprávnění.",
        "processing_error": "Zpracování selhalo. Zkuste to prosím znovu.",
    },
}


def get_language_options():
    """Get list of (locale, display_name) tuples for dropdown."""
    return [(locale, info["display"]) for locale, info in LANGUAGES.items()]


def get_speech_locale(locale: str) -> str:
    """Get the Azure Speech locale code for a given language."""
    return LANGUAGES.get(locale, LANGUAGES["en-US"])["speech_locale"]


def get_monologues(locale: str) -> list[dict]:
    """Get all monologues for a given locale as list of dicts."""
    monologues = MONOLOGUES.get(locale, MONOLOGUES["en-US"])
    return [
        {"id": key, "title": value["title"], "text": value["text"]}
        for key, value in monologues.items()
    ]


def get_monologue_options(locale: str) -> list[tuple[str, str]]:
    """Get monologue options for dropdown (id, title)."""
    monologues = MONOLOGUES.get(locale, MONOLOGUES["en-US"])
    return [(key, value["title"]) for key, value in monologues.items()]


def get_monologue_text(locale: str, monologue_id: str) -> str:
    """Get the text for a specific monologue."""
    monologues = MONOLOGUES.get(locale, MONOLOGUES["en-US"])
    if monologue_id in monologues:
        return monologues[monologue_id]["text"]
    return ""


def get_translation(locale: str, key: str) -> str:
    """Get a UI translation string."""
    translations = UI_TRANSLATIONS.get(locale, UI_TRANSLATIONS["en-US"])
    return translations.get(key, key)
