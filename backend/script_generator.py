import json
import random
import re

NICHE_TEMPLATES = {
    "dark_psychology": {
        "name": "Dark Psychology & Manipulation",
        "bg_music": "dark_suspense.mp3",
        "visual_keywords": ["mysterious shadow", "rainy city street light", "dramatic lighting silhouette", "dark fog neon", "psychological noir"],
        "sample_topics": [
            "3 Unspoken Signs Someone is Trying to Manipulate You",
            "The Power of Silence in Arguments",
            "Why Narcissists Never Change Their Behavior",
            "How People Read Your Body Language Instantly"
        ]
    },
    "facts_curiosities": {
        "name": "Mind-Blowing Facts & Curiosities",
        "bg_music": "upbeat_cyber.mp3",
        "visual_keywords": ["cosmic nebula", "deep sea creature glowing", "ancient temple ruins", "futuristic tech particles", "galaxy starry sky"],
        "sample_topics": [
            "5 Things You Didn't Know About Space",
            "Bizarre Historical Events That Sound Fake",
            "Unbelievable Ocean Secrets Deep Below",
            "Mind-Bending Science Facts You Weren't Taught"
        ]
    },
    "tech_ai": {
        "name": "Tech Breakthroughs & AI News",
        "bg_music": "tech_ambient.mp3",
        "visual_keywords": ["cyberpunk server room", "digital brain network", "robot humanoid interface", "holographic matrix data", "future smart city"],
        "sample_topics": [
            "AI Tools That Will Change Everything in 2026",
            "The Dark Side of Artificial Superintelligence",
            "How Quantum Computing Will Shatter Encryption",
            "The Future of Humanoid Robots in Daily Life"
        ]
    },
    "finance_business": {
        "name": "Wealth Secrets & Money Mindset",
        "bg_music": "inspiring_modern.mp3",
        "visual_keywords": ["luxury skyscraper view", "stock market chart lines", "golden hour city sky line", "private jet runway", "vault money counter"],
        "sample_topics": [
            "How the Top 1% Build Generational Wealth",
            "The Invisible Trap Keeping Most People Broke",
            "3 Money Rules You Must Master in Your 20s",
            "Passive Income Models That Work in 2026"
        ]
    },
    "philosophy_stoicism": {
        "name": "Stoicism & Ancient Wisdom",
        "bg_music": "cinematic_epic.mp3",
        "visual_keywords": ["roman marble statue dusk", "mountaintop sunrise fog", "ancient Greek temple sunset", "lonely warrior cliff", "calm ocean waves sunset"],
        "sample_topics": [
            "Marcus Aurelius: 3 Lessons to Master Your Mind",
            "Stop Caring What Others Think of You",
            "The Art of Remaining Calm Under Extreme Pressure",
            "Why Solitude is Your Greatest Superpower"
        ]
    },
    "horror_truecrime": {
        "name": "Horror & Unsolved Mysteries",
        "bg_music": "scary_drone.mp3",
        "visual_keywords": ["abandoned mansion corridor", "dark misty woods night", "vintage security camera flickering", "haunted house window", "creepy forest path"],
        "sample_topics": [
            "The Creepiest Unsolved Glitch in Real Life",
            "Terrifying Disturbing Phenomena Scientists Can't Explain",
            "Nighttime Encounters That Left No Trace",
            "Urban Legends That Turned Out to Be Real"
        ]
    },
    "motivation_success": {
        "name": "High Performance & Discipline",
        "bg_music": "triumphant_build.mp3",
        "visual_keywords": ["athlete running morning mist", "boxer shadowboxing ring", "mountain peak climber top", "high rise office night work", "sunrise over ocean cliff"],
        "sample_topics": [
            "How to Build Unshakeable Self-Discipline",
            "100 Days of Monastic Focus Changed My Life",
            "The 1% Rule for Relentless Self-Improvement",
            "How to Reset Your Dopamine Baseline"
        ]
    },
    "custom_niche": {
        "name": "✨ Custom Topic / Any Custom Niche",
        "bg_music": "tech_ambient.mp3",
        "visual_keywords": ["cinematic aesthetic", "dramatic lighting 4k", "futuristic background", "luxury modern view", "abstract motion graphics"],
        "sample_topics": [
            "The Hidden Psychology Behind Viral Trends",
            "Unbelievable Historical Secrets Revealed",
            "Mind-Blowing Mysteries Science Cannot Explain"
        ]
    }
}

class ScriptGenerator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key

    def auto_select_bgm(self, topic: str, niche: str) -> str:
        t = topic.lower()
        if any(w in t for w in ["scary", "ghost", "horror", "murder", "creepy", "mystery", "dark", "haunted", "unsolved"]):
            return "scary_drone.mp3"
        elif any(w in t for w in ["manipulate", "psychology", "mind", "silence", "narcissist", "secret", "body language"]):
            return "dark_suspense.mp3"
        elif any(w in t for w in ["ai", "tech", "robot", "quantum", "computer", "future", "cyber", "code", "system"]):
            return "tech_ambient.mp3"
        elif any(w in t for w in ["money", "wealth", "finance", "rich", "business", "invest", "broke", "passive", "dollar"]):
            return "inspiring_modern.mp3"
        elif any(w in t for w in ["stoic", "marcus", "philosophy", "aurelius", "warrior", "space", "universe", "ancient"]):
            return "cinematic_epic.mp3"
        elif any(w in t for w in ["discipline", "success", "workout", "grind", "focus", "1%", "win", "rule", "life"]):
            return "triumphant_build.mp3"
        elif any(w in t for w in ["fact", "curious", "bizarre", "ocean", "did you know", "science", "anime"]):
            return "upbeat_cyber.mp3"
        
        niche_info = NICHE_TEMPLATES.get(niche)
        if niche_info:
            return niche_info.get("bg_music", "tech_ambient.mp3")
        return "tech_ambient.mp3"

    def _derive_visual_keywords(self, topic: str, niche: str) -> list:
        t = topic.lower()
        if any(w in t for w in ["anime", "manga", "japan", "naruto", "dragon ball", "goku"]):
            return ["anime neon city", "tokyo street night lights", "manga drawing artistic", "japanese cyberpunk aesthetic", "cherry blossom dusk"]
        elif any(w in t for w in ["food", "cook", "recipe", "kitchen", "chef", "saffron"]):
            return ["gourmet dish preparation", "luxury kitchen chef cooking", "vibrant spices close up", "steaming hot food cinematic", "fresh organic ingredients"]
        elif any(w in t for w in ["space", "galaxy", "nasa", "planet", "star", "cosmic"]):
            return ["deep space galaxy nebula", "astronaut looking starry sky", "earth from orbit space", "glowing cosmic particles", "alien planet horizon"]
        elif any(w in t for w in ["car", "speed", "supercar", "engine", "ferrari"]):
            return ["supercar driving highway night", "sleek sports car neon studio", "engine roaring close up", "luxury vehicle cockpit", "speed motion blur city"]
        elif any(w in t for w in ["crypto", "bitcoin", "blockchain", "trade"]):
            return ["digital crypto currency network", "bitcoin golden coin glow", "stock market chart green", "future financial matrix", "holographic trading desk"]

        niche_info = NICHE_TEMPLATES.get(niche, NICHE_TEMPLATES["custom_niche"])
        base_keywords = list(niche_info["visual_keywords"])
        topic_words = [w.lower() for w in topic.split() if len(w) > 3]
        if topic_words:
            base_keywords.insert(0, " ".join(topic_words[:2]) + " cinematic")
        return base_keywords

    def generate_script(self, niche: str, topic: str = "", video_type: str = "shorts", tone: str = "dramatic") -> dict:
        niche_info = NICHE_TEMPLATES.get(niche, NICHE_TEMPLATES["custom_niche"])
        
        # Robust placeholder filtering
        if not topic or not topic.strip() or "type any custom" in topic.lower() or "placeholder" in topic.lower():
            if niche == "custom_niche":
                topic = random.choice(niche_info["sample_topics"])
            else:
                valid_topics = [t for t in niche_info.get("sample_topics", []) if not t.startswith("Type any")]
                topic = random.choice(valid_topics) if valid_topics else "The Secrets of Human Mind"

        auto_bgm = self.auto_select_bgm(topic, niche)
        visual_keywords = self._derive_visual_keywords(topic, niche)

        if video_type == "shorts":
            scenes = self._generate_shorts_scenes(niche, topic, tone, visual_keywords)
        else:
            scenes = self._generate_longform_scenes(niche, topic, tone, visual_keywords)

        total_words = sum(len(s["text"].split()) for s in scenes)
        estimated_duration = round(total_words / 2.5, 1)

        clean_topic_word = re.sub(r'[^a-zA-Z0-9]', '', topic.split()[0]).lower()
        tags = [
            f"#{niche}",
            "#shorts",
            "#viral",
            "#facts",
            "#trending",
            f"#{clean_topic_word}"
        ]

        title = f"{topic} | Must Watch!" if len(topic) < 45 else topic

        return {
            "niche": niche,
            "topic": topic,
            "video_type": video_type,
            "tone": tone,
            "title": title,
            "bg_music": auto_bgm,
            "estimated_duration_sec": estimated_duration,
            "seo": {
                "description": f"Explore {topic} in this deep dive video. Subscribe for daily videos!\n\n" + " ".join(tags),
                "tags": [t.replace("#", "") for t in tags]
            },
            "scenes": scenes
        }

    def _generate_shorts_scenes(self, niche: str, topic: str, tone: str, visual_keywords: list) -> list:
        kw = visual_keywords
        t_low = topic.lower()

        if "anime" in t_low or "manga" in t_low:
            hook = f"Did you know these mind-blowing secrets about {topic}?"
            body1 = "Anime creators frequently hide secret codes and real-world history inside background frames."
            body2 = "The most legendary scenes take over three months of manual frame-by-frame animation."
            climax = "Look closer next time you watch, because nothing in anime is drawn by accident!"
            cta = "Subscribe for daily anime breakdowns!"
        elif "food" in t_low or "cook" in t_low or "saffron" in t_low:
            hook = f"Here is the incredible secret behind {topic}!"
            body1 = "Master chefs use precise temperature control to unlock deep natural flavors."
            body2 = "Even rare luxury spices like real saffron require over 75,000 flowers per pound."
            climax = "Once you try authentic artisanal cooking, ordinary food will never taste the same."
            cta = "Subscribe for more delicious culinary secrets!"
        elif "space" in t_low or "galaxy" in t_low:
            hook = f"What scientists just discovered about {topic} will shock you!"
            body1 = "Deep space holds ancient cosmic structures that defy our understanding of physics."
            body2 = "Signals traveling millions of light-years reach Earth carrying clues to our origin."
            climax = "The universe is far stranger and more vast than humanity ever imagined."
            cta = "Subscribe for mind-blowing space discoveries!"
        else:
            hook = f"Did you know the secret behind {topic}?"
            body1 = f"Most people completely misunderstand {topic}, but the reality is fascinating."
            body2 = "When you analyze the deeper facts, a shocking pattern begins to emerge."
            climax = "Once you see this truth, you can never look at it the same way again."
            cta = "Subscribe for more daily insights!"

        return [
            {
                "scene_num": 1,
                "type": "Hook",
                "text": hook,
                "search_term": kw[0] if len(kw) > 0 else "cinematic intro",
                "on_screen_text": "THE TRUTH REVEALED"
            },
            {
                "scene_num": 2,
                "type": "Insight 1",
                "text": body1,
                "search_term": kw[1] if len(kw) > 1 else "dramatic mystery",
                "on_screen_text": "DEEPER INSIGHT"
            },
            {
                "scene_num": 3,
                "type": "Insight 2",
                "text": body2,
                "search_term": kw[2] if len(kw) > 2 else "futuristic abstract",
                "on_screen_text": "CRITICAL FACT"
            },
            {
                "scene_num": 4,
                "type": "Climax",
                "text": climax,
                "search_term": kw[3] if len(kw) > 3 else "epic climax",
                "on_screen_text": "THE REVELATION"
            },
            {
                "scene_num": 5,
                "type": "Call to Action",
                "text": cta,
                "search_term": kw[4] if len(kw) > 4 else "aesthetic landscape",
                "on_screen_text": "SUBSCRIBE NOW"
            }
        ]

    def _generate_longform_scenes(self, niche: str, topic: str, tone: str, visual_keywords: list) -> list:
        kw = visual_keywords
        return [
            {
                "scene_num": 1,
                "type": "Introduction",
                "text": f"Welcome back. Today we are uncovering the unbelievable truth about {topic}.",
                "search_term": kw[0] if len(kw) > 0 else "epic opening cinematic",
                "on_screen_text": topic.upper()
            },
            {
                "scene_num": 2,
                "type": "Historical Context",
                "text": f"To understand {topic}, we must look back at how this hidden phenomenon first began.",
                "search_term": kw[1] if len(kw) > 1 else "historical archives",
                "on_screen_text": "THE ORIGINS"
            },
            {
                "scene_num": 3,
                "type": "Deep Dive Analysis",
                "text": "Experts and researchers have analyzed this for years, uncovering unexpected patterns.",
                "search_term": kw[2] if len(kw) > 2 else "digital network data",
                "on_screen_text": "KEY EVIDENCE"
            },
            {
                "scene_num": 4,
                "type": "The Turning Point",
                "text": "What happens next changes everything we thought we knew about the topic.",
                "search_term": kw[3] if len(kw) > 3 else "dramatic light glow",
                "on_screen_text": "THE TURNING POINT"
            },
            {
                "scene_num": 5,
                "type": "Conclusion & CTA",
                "text": "If you found this valuable, hit subscribe and share your thoughts in the comments below.",
                "search_term": kw[4] if len(kw) > 4 else "dramatic sunset horizon",
                "on_screen_text": "SUBSCRIBE & COMMENT"
            }
        ]

script_gen = ScriptGenerator()
