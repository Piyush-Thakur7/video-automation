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
        """
        AI Mood Engine: Analyzes topic sentiment and keywords to automatically pick the best matching background music track.
        """
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
        elif any(w in t for w in ["fact", "curious", "bizarre", "ocean", "did you know", "science"]):
            return "upbeat_cyber.mp3"
        
        niche_info = NICHE_TEMPLATES.get(niche)
        if niche_info:
            return niche_info.get("bg_music", "tech_ambient.mp3")
        return "tech_ambient.mp3"

    def generate_script(self, niche: str, topic: str = "", video_type: str = "shorts", tone: str = "dramatic") -> dict:
        """
        Generates a structured video script broken down into timed scenes with text, visual keywords, audio cues, and SEO.
        """
        niche_info = NICHE_TEMPLATES.get(niche, NICHE_TEMPLATES["custom_niche"])
        
        if not topic.strip():
            if niche == "custom_niche":
                topic = "The Hidden Secret of Success"
            else:
                topic = random.choice(niche_info["sample_topics"])

        auto_bgm = self.auto_select_bgm(topic, niche)

        visual_keywords = list(niche_info["visual_keywords"])
        topic_words = [w.lower() for w in topic.split() if len(w) > 3]
        if topic_words:
            visual_keywords.insert(0, " ".join(topic_words[:2]) + " cinematic")

        if video_type == "shorts":
            scenes = self._generate_shorts_scenes(niche, topic, tone, visual_keywords)
        else:
            scenes = self._generate_longform_scenes(niche, topic, tone, visual_keywords)

        total_words = sum(len(s["text"].split()) for s in scenes)
        estimated_duration = round(total_words / 2.5, 1)

        tags = [
            f"#{niche.replace('_', '')}",
            f"#{video_type}",
            "#viral",
            "#facts",
            "#trending",
            f"#{topic.split()[0].lower()}",
            "#mindset",
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
        scene_templates = [
            {
                "hook": f"Did you know about {topic}?",
                "middle_1": "Most people ignore this critical sign until it's far too late.",
                "middle_2": "When this happens, your brain automatically shifts into survival mode.",
                "climax": "Pay close attention next time, because once you see it, you can never unsee it.",
                "cta": "Follow for more secret insights every single day."
            },
            {
                "hook": f"Here is the real truth about {topic}.",
                "middle_1": "Experts discovered that 90% of people misunderstand how this works.",
                "middle_2": "It functions by targeting your core instincts of curiosity and focus.",
                "climax": "If you recognize this pattern in your life, take action immediately.",
                "cta": "Subscribe now so you never miss another truth."
            }
        ]

        choice = random.choice(scene_templates)
        visuals = visual_keywords * 2
        random.shuffle(visuals)

        clean_topic = topic.replace("Did you know about", "").replace("Here is the real truth about", "").strip().upper()

        scenes = [
            {
                "scene_number": 1,
                "type": "Hook",
                "text": choice["hook"],
                "visual_prompt": f"{visuals[0]}, dramatic eye contact, cinematic dark atmosphere, high contrast",
                "search_term": visuals[0],
                "overlay_text": clean_topic[:30] if len(clean_topic) > 5 else "LISTEN CLOSELY"
            },
            {
                "scene_number": 2,
                "type": "Revelation",
                "text": choice["middle_1"],
                "visual_prompt": f"{visuals[1]}, intense close-up, dramatic neon lighting, suspense",
                "search_term": visuals[1],
                "overlay_text": "THE REVELATION"
            },
            {
                "scene_number": 3,
                "type": "Deep Dive",
                "text": choice["middle_2"],
                "visual_prompt": f"{visuals[2]}, slow motion motion blur, high tech futuristic mood",
                "search_term": visuals[2],
                "overlay_text": "LOOK CLOSER"
            },
            {
                "scene_number": 4,
                "type": "Climax",
                "text": choice["climax"],
                "visual_prompt": f"{visuals[3]}, sudden dramatic movement, epic lighting, sharp focus",
                "search_term": visuals[3],
                "overlay_text": "NEVER IGNORE THIS"
            },
            {
                "scene_number": 5,
                "type": "CTA",
                "text": choice["cta"],
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
            ("Introduction Hook", f"Welcome back. Today we are diving deep into {topic}. What you are about to learn has been kept out of mainstream awareness for decades."),
            ("Context & Background", "To understand why this matters, we must look at how human perception really works under pressure."),
            ("Core Principle 1", "First, notice how subtle shifts in environment completely change human decision making. Small cues trigger massive behavioral changes."),
            ("Core Principle 2", "Second, the brain prioritizes immediate familiarity over truth. This creates blind spots that can be easily exploited."),
            ("Case Study / Example", "Consider what happens when individuals are exposed to continuous subtle influence without realizing it."),
            ("Key Takeaway", "The takeaway is simple: awareness is your ultimate shield. Once you recognize these mechanisms, you become immune to them."),
            ("Actionable Strategy", "Start observing your surroundings with detached curiosity. Test this principle in your next interaction."),
            ("Conclusion & Call to Action", f"If this breakdown on {topic} brought you value, leave a like and subscribe for more deep dives. Drop your thoughts in the comments below!")
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
