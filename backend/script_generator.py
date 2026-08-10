import json
import random
import re

NICHE_TEMPLATES = {
    "dark_psychology": {
        "name": "Dark Psychology & Manipulation",
        "bg_music": "dark_suspense.mp3",
        "visual_keywords": ["mysterious shadow silhouette", "rainy city street night lights", "dramatic cinematic lighting", "dark fog neon glow", "psychological thriller noir"],
        "sample_topics": [
            "3 Unspoken Signs Someone is Trying to Manipulate You",
            "The Power of Silence in High Stakes Arguments",
            "Why Narcissists Never Change Their Behavior",
            "How People Read Your Micro Expressions Instantly"
        ]
    },
    "facts_curiosities": {
        "name": "Mind-Blowing Facts & Curiosities",
        "bg_music": "upbeat_cyber.mp3",
        "visual_keywords": ["cosmic nebula starry sky", "deep sea glowing creature", "ancient temple ruins sunset", "futuristic tech particles", "galaxy cosmic horizon"],
        "sample_topics": [
            "Unbelievable Facts About Dogs You Never Knew",
            "5 Things You Didn't Know About Deep Space",
            "Bizarre Historical Events That Sound Completely Fake",
            "Mind-Bending Science Facts You Weren't Taught in School"
        ]
    },
    "tech_ai": {
        "name": "Tech Breakthroughs & AI News",
        "bg_music": "tech_ambient.mp3",
        "visual_keywords": ["cyberpunk server room data", "digital brain neural network", "robot humanoid interface", "holographic matrix data stream", "future smart city skyline"],
        "sample_topics": [
            "AI Tools That Will Change Everything in 2026",
            "The Dark Side of Artificial Superintelligence",
            "How Quantum Computing Will Shatter Modern Encryption",
            "The Future of Humanoid Autonomous Robots"
        ]
    },
    "finance_business": {
        "name": "Wealth Secrets & Money Mindset",
        "bg_music": "inspiring_modern.mp3",
        "visual_keywords": ["luxury skyscraper window view", "stock market chart green lines", "golden hour city skyline", "private jet runway dusk", "vault money stack counter"],
        "sample_topics": [
            "How the Top 1% Build Generational Wealth",
            "The Invisible Financial Trap Keeping Most People Broke",
            "3 Money Rules You Must Master Before 30",
            "Passive Income Models That Work in 2026"
        ]
    },
    "philosophy_stoicism": {
        "name": "Stoicism & Ancient Wisdom",
        "bg_music": "cinematic_epic.mp3",
        "visual_keywords": ["roman marble statue dusk", "mountaintop sunrise fog", "ancient Greek temple sunset", "lonely warrior cliff horizon", "calm ocean waves sunset"],
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
        "visual_keywords": ["abandoned mansion corridor night", "dark misty woods moonlight", "vintage security camera glitch", "haunted house window shadow", "creepy forest path fog"],
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
        "visual_keywords": ["athlete running morning mist", "boxer shadowboxing ring lights", "mountain peak climber top view", "high rise office night work", "sunrise over ocean cliff"],
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
        "visual_keywords": ["cinematic aesthetic background", "dramatic lighting 4k", "futuristic glowing particle grid", "luxury modern architectural view", "abstract motion graphics 4k"],
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
        elif any(w in t for w in ["fact", "curious", "bizarre", "ocean", "did you know", "science", "anime", "dog", "animal"]):
            return "upbeat_cyber.mp3"
        
        niche_info = NICHE_TEMPLATES.get(niche)
        if niche_info:
            return niche_info.get("bg_music", "tech_ambient.mp3")
        return "tech_ambient.mp3"

    def _derive_visual_keywords(self, topic: str, niche: str) -> list:
        t = topic.lower()
        if any(w in t for w in ["dog", "puppy", "canine", "animal", "pet"]):
            return ["golden retriever playing outdoors", "dog nose close up detail", "cute smart dog eyes", "loyal German Shepherd forest", "playful puppy grass sunset", "happy dog running park"]
        elif any(w in t for w in ["anime", "manga", "japan", "naruto", "goku"]):
            return ["anime neon city night", "tokyo street night lights", "manga drawing artistic pencil", "japanese cyberpunk aesthetic", "cherry blossom dusk glow", "epic anime battle scene"]
        elif any(w in t for w in ["food", "cook", "recipe", "kitchen", "chef", "saffron"]):
            return ["gourmet dish preparation", "luxury kitchen chef cooking", "vibrant spices close up", "steaming hot food cinematic", "fresh organic ingredients", "sizzling pan culinary art"]
        elif any(w in t for w in ["space", "galaxy", "nasa", "planet", "star", "cosmic"]):
            return ["deep space galaxy nebula", "astronaut looking starry sky", "earth from orbit space view", "glowing cosmic particles", "alien planet horizon sunset", "supernova explosion space"]
        elif any(w in t for w in ["car", "speed", "supercar", "ferrari"]):
            return ["supercar driving highway night", "sleek sports car neon studio", "engine roaring close up detail", "luxury vehicle cockpit dashboard", "speed motion blur city night"]

        niche_info = NICHE_TEMPLATES.get(niche, NICHE_TEMPLATES["custom_niche"])
        base_keywords = list(niche_info["visual_keywords"])
        topic_words = [w.lower() for w in topic.split() if len(w) > 3]
        if topic_words:
            base_keywords.insert(0, " ".join(topic_words[:2]) + " cinematic 4k")
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
        # Average reading speed is ~2.5 words per second
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

        # 6-Scene High-Retention Script (100 - 130 words for ~38 to 45 seconds total duration)
        if any(w in t_low for w in ["dog", "puppy", "canine", "animal", "pet"]):
            scenes_content = [
                ("Hook", f"Think you know everything about dogs? These three mind-blowing facts will completely change how you see your pet!", kw[0] if len(kw) > 0 else "dog eyes cinematic", "CANINE SECRETS"),
                ("Fact 1", "First, a dog's nose print is 100% unique, just like a human fingerprint. No two dogs on Earth share the exact same nose pattern!", kw[1] if len(kw) > 1 else "dog nose close up", "UNIQUE NOSE PRINT"),
                ("Fact 2", "Second, dogs don't just smell food—they can actually smell human emotions! They detect tiny chemical changes in your sweat when you're stressed or happy.", kw[2] if len(kw) > 2 else "loyal dog eyes", "SMELL EMOTIONS"),
                ("Fact 3", "Third, when your dog wags its tail to the right, it means they are relaxed and happy. But a tail wag to the left indicates fear and anxiety!", kw[3] if len(kw) > 3 else "dog tail wagging", "TAIL CODE EXPOSED"),
                ("Climax", "Finally, dogs dream just like humans do. During REM sleep, their brains replay memories of playing and running with you!", kw[4] if len(kw) > 4 else "sleeping dog dreaming", "DOGS DREAM OF YOU"),
                ("CTA", "Did any of these surprise you? Subscribe now for more incredible animal facts!", kw[5] if len(kw) > 5 else "happy dog running", "SUBSCRIBE FOR MORE")
            ]
        elif any(w in t_low for w in ["space", "galaxy", "nasa", "planet", "star"]):
            scenes_content = [
                ("Hook", f"Space is far stranger than you think! Here are three terrifying cosmic facts that sound like science fiction.", kw[0] if len(kw) > 0 else "deep space galaxy", "COSMIC SECRETS"),
                ("Fact 1", "First, out in deep space, there is zero sound. Because sound requires air to travel, cosmic explosions occur in complete, haunting silence!", kw[1] if len(kw) > 1 else "glowing nebula space", "SILENCE OF SPACE"),
                ("Fact 2", "Second, on planets like Neptune and Uranus, extreme atmospheric pressure causes it to literally rain solid diamonds from the sky!", kw[2] if len(kw) > 2 else "planet atmosphere glow", "DIAMOND RAIN"),
                ("Fact 3", "Third, neutron stars spin at absurd speeds—up to 700 times per second—creating magnetic fields powerful enough to wipe your credit cards from miles away!", kw[3] if len(kw) > 3 else "neutron star spinning", "NEUTRON POWER"),
                ("Climax", "And because there is no wind or liquid water on the Moon, astronaut footprints left 50 years ago will remain preserved for 100 million years!", kw[4] if len(kw) > 4 else "moon surface footprints", "PRESERVED FOREVER"),
                ("CTA", "Which cosmic mystery shocked you most? Subscribe for daily space discoveries!", kw[5] if len(kw) > 5 else "glowing starry night", "SUBSCRIBE FOR MORE")
            ]
        elif any(w in t_low for w in ["manipulate", "psychology", "mind", "silence", "narcissist", "dark"]):
            scenes_content = [
                ("Hook", f"Here are three dark psychological tactics people secretly use to control conversations without you noticing.", kw[0] if len(kw) > 0 else "dark shadow silhouette", "DARK PSYCHOLOGY"),
                ("Fact 1", "First, the Power of Strategic Silence. When someone gives you a weak answer, stay completely quiet and maintain eye contact. They will naturally spill the truth just to break the uncomfortable tension!", kw[1] if len(kw) > 1 else "dramatic silhouette", "SILENCE TECHNIQUE"),
                ("Fact 2", "Second, the Choice Illusion. Manipulators never ask yes or no. They offer two choices that both lead to the exact outcome they wanted in the first place!", kw[2] if len(kw) > 2 else "dark neon street", "FALSE CHOICES"),
                ("Fact 3", "Third, the Ben Franklin Effect. Asking someone for a tiny favor tricks their brain into believing they genuinely like and trust you!", kw[3] if len(kw) > 3 else "rainy city night", "BRAIN TRICK"),
                ("Climax", "Once you recognize these subconscious patterns, nobody can ever manipulate your choices again.", kw[4] if len(kw) > 4 else "mysterious noir light", "UNTOUCHABLE MIND"),
                ("CTA", "Have you ever experienced these tactics? Subscribe for powerful psychological insights!", kw[5] if len(kw) > 5 else "abstract neon glow", "SUBSCRIBE FOR MORE")
            ]
        elif any(w in t_low for w in ["money", "wealth", "finance", "rich", "broke"]):
            scenes_content = [
                ("Hook", f"Want to break the broke cycle? Here are three harsh financial truths the top 1% use to build massive wealth!", kw[0] if len(kw) > 0 else "luxury skyscraper skyline", "WEALTH RULES"),
                ("Fact 1", "First, poor people spend money to look rich, while wealthy people invest money to buy assets that generate income while they sleep!", kw[1] if len(kw) > 1 else "gold money stack", "ASSETS VS LIABILITIES"),
                ("Fact 2", "Second, inflation silently destroys cash sitting in bank accounts. If your money isn't earning returns above inflation, you are losing purchasing power every single day!", kw[2] if len(kw) > 2 else "stock market chart green", "INFLATION TRAP"),
                ("Fact 3", "Third, compound interest is the eighth wonder of the world. Investing small amounts consistently in your 20s produces exponentially more wealth than starting late with millions!", kw[3] if len(kw) > 3 else "financial network data", "COMPOUND POWER"),
                ("Climax", "Master your money mindset today, or you will spend your entire life working for someone else's dreams.", kw[4] if len(kw) > 4 else "private jet sunset", "OWN YOUR FUTURE"),
                ("CTA", "Ready to build true financial freedom? Subscribe for daily wealth strategies!", kw[5] if len(kw) > 5 else "city skyline sunset", "SUBSCRIBE FOR MORE")
            ]
        elif any(w in t_low for w in ["stoic", "marcus", "philosophy", "aurelius", "calm"]):
            scenes_content = [
                ("Hook", f"Feeling overwhelmed by life? Here are three timeless Stoic principles from Emperor Marcus Aurelius to master your mind.", kw[0] if len(kw) > 0 else "statue dusk sunset", "STOIC WISDOM"),
                ("Fact 1", "First, you have power over your mind, not outside events. Realize this, and you will find instant unshakeable strength!", kw[1] if len(kw) > 1 else "mountaintop fog sunrise", "CONTROL YOUR MIND"),
                ("Fact 2", "Second, the impediment to action advances action. What stands in the way becomes the way forward!", kw[2] if len(kw) > 2 else "ancient temple ruins", "OBSTACLE IS WAY"),
                ("Fact 3", "Third, remember Memento Mori—that you are mortal. Knowing your time is limited frees you from wasting energy on meaningless drama!", kw[3] if len(kw) > 3 else "lonely cliff warrior", "MEMENTO MORI"),
                ("Climax", "When you stop reacting to chaos and focus solely on your internal discipline, nothing in this world can disturb your peace.", kw[4] if len(kw) > 4 else "calm ocean waves", "UNBREAKABLE PEACE"),
                ("CTA", "Which Stoic lesson resonated with you most? Subscribe for ancient wisdom!", kw[5] if len(kw) > 5 else "horizon sunset view", "SUBSCRIBE FOR MORE")
            ]
        else:
            scenes_content = [
                ("Hook", f"Did you know these unbelievable facts about {topic}? The truth will completely surprise you!", kw[0] if len(kw) > 0 else "cinematic intro glow", "THE HIDDEN TRUTH"),
                ("Fact 1", f"First, most people think {topic} is simple, but deep historical records reveal a shocking secret that changed everything.", kw[1] if len(kw) > 1 else "dramatic mystery lighting", "HISTORICAL REVELATION"),
                ("Fact 2", f"Second, modern researchers discovered that key aspects of {topic} operate completely differently under close scientific analysis!", kw[2] if len(kw) > 2 else "futuristic abstract grid", "SCIENTIFIC PROOF"),
                ("Fact 3", f"Third, experts spent decades decoding how {topic} impacts our daily choices without us ever realizing it!", kw[3] if len(kw) > 3 else "high tech matrix stream", "HIDDEN INFLUENCE"),
                ("Climax", f"Once you understand the real mechanics behind {topic}, you will never see the world in the same way again.", kw[4] if len(kw) > 4 else "epic glowing horizon", "MIND SHIFT"),
                ("CTA", "Did this open your eyes? Subscribe now for more daily mind-blowing breakdowns!", kw[5] if len(kw) > 5 else "aesthetic sunset sky", "SUBSCRIBE FOR MORE")
            ]

        return [
            {
                "scene_num": i + 1,
                "type": item[0],
                "text": item[1],
                "search_term": item[2],
                "on_screen_text": item[3]
            }
            for i, item in enumerate(scenes_content)
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
