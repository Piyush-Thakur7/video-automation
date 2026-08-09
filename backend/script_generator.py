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
            "Type any custom topic or niche subject..."
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
        
        if not topic.strip():
            if niche == "custom_niche":
                topic = "The Hidden Secret of Success"
            else:
                topic = random.choice(niche_info["sample_topics"])

        auto_bgm = self.auto_select_bgm(topic, niche)
        visual_keywords = self._derive_visual_keywords(topic, niche)

        if video_type == "shorts":
            scenes = self._generate_shorts_scenes(niche, topic, tone, visual_keywords)
        else:
            scenes = self._generate_longform_scenes(niche, topic, tone, visual_keywords)

        total_words = sum(len(s["text"].split()) for s in scenes)
        estimated_duration = round(total_words / 2.5, 1)

        clean_topic_word = re.sub(r'[^a-zA-Z0-0]', '', topic.split()[0]).lower()
        tags = [
            f"#{niche.replace('_', '')}",
            f"#{video_type}",
            "#viral",
            "#facts",
            "#trending",
            f"#{clean_topic_word}",
            "#shorts" if video_type == "shorts" else "#youtube"
        ]

        title = f"{topic} | Must Watch!" if video_type == "shorts" else f"The Hidden Truth About {topic}"
        description = f"Explore {topic} in this deep dive video. Subscribe for daily videos!\n\n" + " ".join(tags)

        thumbnail_prompt = f"Cinematic dramatic 8k lighting thumbnail for {topic}, {visual_keywords[0]}, highly detailed, vivid color contrast, photorealistic"

        return {
            "title": title,
            "niche": niche,
            "video_type": video_type,
            "topic": topic,
            "estimated_duration": estimated_duration,
            "bg_music": auto_bgm,
            "seo": {
                "tags": tags,
                "description": description,
                "thumbnail_prompt": thumbnail_prompt
            },
            "scenes": scenes
        }

    def _generate_shorts_scenes(self, niche: str, topic: str, tone: str, visual_keywords: list) -> list:
        t = topic.lower()
        clean_topic = topic.strip().upper()

        if any(w in t for w in ["anime", "manga", "cartoon", "japan"]):
            hook_text = f"Did you know these mind-blowing secrets about {topic}?"
            rev_text = "Anime creators frequently hide secret codes and real-world history inside background frames."
            deep_text = "From record-breaking animation budgets to easter eggs, every single detail is crafted with intense precision."
            climax_text = "Once you learn these hidden facts, you will watch your favorite series in a completely new light."
            cta_text = "Subscribe now for daily anime facts and breakdown insights!"
        elif any(w in t for w in ["food", "cook", "saffron", "kitchen", "recipe"]):
            hook_text = f"Here is the incredible story behind {topic}."
            rev_text = "Master chefs use precise temperature science that completely transforms flavor profiles."
            deep_text = "A single gram of rare ingredients requires hundreds of hours of delicate hand harvesting."
            climax_text = "Respect the art behind every dish, because true culinary perfection is pure science."
            cta_text = "Follow for daily gourmet food secrets and cooking breakdowns!"
        elif any(w in t for w in ["fact", "curious", "bizarre", "science", "ocean", "space"]):
            hook_text = f"Here are bizarre facts about {topic} that sound completely fake."
            rev_text = "Scientists discovered that fundamental natural laws behave unexpectedly under extreme conditions."
            deep_text = "What seems like science fiction is actually documented physical reality observed by researchers."
            climax_text = "The universe is far stranger than human imagination could ever predict."
            cta_text = "Subscribe for daily mind-bending science and curiosity facts!"
        elif niche == "dark_psychology" and not any(w in t for w in ["anime", "fact", "food", "cook", "tech", "money"]):
            hook_text = f"Did you know the psychological secret behind {topic}?"
            rev_text = "Most people ignore subtle behavioral cues until someone exploits them."
            deep_text = "Subconscious body language triggers automatic responses before your rational mind even reacts."
            climax_text = "Recognize these psychological patterns so you stay in total control of every conversation."
            cta_text = "Subscribe for daily psychological insights and mental protection!"
        else:
            hook_text = f"Did you know the incredible truth about {topic}?"
            rev_text = f"Experts confirm that {topic} holds key insights most people never discover."
            deep_text = "When you look beneath the surface, the underlying mechanics become instantly clear."
            climax_text = "Understanding this principle gives you a massive advantage in understanding how things really work."
            cta_text = "Subscribe now for daily deep dives and viral knowledge!"

        visuals = visual_keywords * 2
        random.shuffle(visuals)

        scenes = [
            {
                "scene_number": 1,
                "type": "Hook",
                "text": hook_text,
                "visual_prompt": f"{visuals[0]}, 4k cinematic lighting, vivid colors",
                "search_term": visuals[0],
                "overlay_text": clean_topic[:30] if len(clean_topic) > 5 else "MUST WATCH"
            },
            {
                "scene_number": 2,
                "type": "Revelation",
                "text": rev_text,
                "visual_prompt": f"{visuals[1]}, intense close-up, dramatic lighting, high contrast",
                "search_term": visuals[1],
                "overlay_text": "THE REVELATION"
            },
            {
                "scene_number": 3,
                "type": "Deep Dive",
                "text": deep_text,
                "visual_prompt": f"{visuals[2]}, slow motion motion blur, artistic mood",
                "search_term": visuals[2],
                "overlay_text": "LOOK CLOSER"
            },
            {
                "scene_number": 4,
                "type": "Climax",
                "text": climax_text,
                "visual_prompt": f"{visuals[3]}, sudden dramatic movement, epic lighting, sharp focus",
                "search_term": visuals[3],
                "overlay_text": "THE TRUTH REVEALED"
            },
            {
                "scene_number": 5,
                "type": "CTA",
                "text": cta_text,
                "visual_prompt": f"{visuals[4]}, inspiring dramatic view, glowing light beam",
                "search_term": visuals[4],
                "overlay_text": "SUBSCRIBE FOR MORE"
            }
        ]
        return scenes

    def _generate_longform_scenes(self, niche: str, topic: str, tone: str, visual_keywords: list) -> list:
        scenes = []
        visuals = visual_keywords * 3
        random.shuffle(visuals)

        parts = [
            ("Introduction Hook", f"Welcome back. Today we are exploring {topic} in full detail."),
            ("Context & Background", f"To understand {topic}, we must look at the foundational principles that drive it."),
            ("Core Principle 1", "First, notice how subtle elements interact to create powerful overall effects."),
            ("Core Principle 2", "Second, key patterns emerge when you analyze the data carefully over time."),
            ("Case Study / Example", f"Consider real-world applications where {topic} altered outcomes completely."),
            ("Key Takeaway", "The takeaway is clear: deeper understanding yields far greater appreciation and results."),
            ("Actionable Strategy", "Apply these insights today to sharpen your knowledge and perspective."),
            ("Conclusion & Call to Action", f"If this breakdown on {topic} brought you value, leave a like and subscribe for more deep dives!")
        ]

        for idx, (title, text) in enumerate(parts, 1):
            scenes.append({
                "scene_number": idx,
                "type": title,
                "text": text,
                "visual_prompt": f"{visuals[idx-1]}, 4k cinematic lighting, ultra detailed",
                "search_term": visuals[idx-1],
                "overlay_text": title.upper()
            })

        return scenes

script_gen = ScriptGenerator()
