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
            "Unbelievable Facts About Cats You Never Knew",
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
    "kids_stories": {
        "name": "🧸 Kids Bedtime Stories & Magical Fairytales",
        "bg_music": "happy_playful.mp3",
        "visual_keywords": ["3d animated cute fantasy fairy tale", "magical glowing forest 3d cartoon", "cute 3d animals playing sunset", "colorful magical kingdom sky cartoon", "charming cute dragon 3d animation"],
        "sample_topics": [
            "The Brave Little Dragon Who Found His Flame",
            "The Magical Tree That Grew Golden Stars",
            "The Secret Party of the Forest Animals",
            "The Curious Kitten's Adventure in Toyland"
        ]
    },
    "kids_learning": {
        "name": "🎈 Kids Fun Science & Animal Discoveries",
        "bg_music": "happy_playful.mp3",
        "visual_keywords": ["cute happy animals 3d cartoon", "colorful space planets kids cartoon", "playful dolphin jumping ocean 3d", "happy cute puppy running grass 3d", "colorful rainbows and clouds 3d animation"],
        "sample_topics": [
            "Why Do Flamingos Stand on One Leg?",
            "How Do Fish Breathe Underwater?",
            "Fun Space Facts Every Kid Should Know",
            "Why Do Bees Make Honey?"
        ]
    },
    "kids_riddles": {
        "name": "🧩 Fun Riddles & Brain Teasers for Kids",
        "bg_music": "happy_playful.mp3",
        "visual_keywords": ["glowing question mark 3d cartoon", "cute detective cat 3d animation", "colorful riddle treasure box cartoon", "happy children thinking 3d animation"],
        "sample_topics": [
            "What Has Hands But Cannot Clap? Kids Riddle!",
            "I Have a Neck But No Head! What Am I?",
            "What Gets Wetter as It Dries? Fun Kids Riddle"
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
        if any(w in t for w in ["cat", "kitten", "feline", "dog", "puppy", "canine", "animal", "pet", "funny", "cute", "humor"]):
            return "happy_playful.mp3"
        elif any(w in t for w in ["lofi", "chill", "relax", "cozy", "nature", "peace", "life", "habit"]):
            return "lofi_chill.mp3"
        elif any(w in t for w in ["scary", "ghost", "horror", "murder", "creepy", "mystery", "dark", "haunted", "unsolved"]):
            return "scary_drone.mp3"
        elif any(w in t for w in ["manipulate", "psychology", "mind", "silence", "narcissist", "secret", "body language"]):
            return "dark_suspense.mp3"
        elif any(w in t for w in ["ai", "tech", "robot", "quantum", "computer", "future", "cyber", "code", "system"]):
            return "tech_ambient.mp3"
        elif any(w in t for w in ["money", "wealth", "finance", "rich", "business", "invest", "broke", "passive", "dollar"]):
            return "inspiring_modern.mp3"
        elif any(w in t for w in ["stoic", "marcus", "philosophy", "aurelius", "warrior", "space", "universe", "ancient", "history"]):
            return "cinematic_epic.mp3"
        elif any(w in t for w in ["discipline", "success", "workout", "grind", "focus", "1%", "win", "rule"]):
            return "triumphant_build.mp3"
        elif any(w in t for w in ["fact", "curious", "bizarre", "ocean", "did you know", "science", "anime"]):
            return "upbeat_cyber.mp3"
        
        niche_info = NICHE_TEMPLATES.get(niche)
        if niche_info:
            return niche_info.get("bg_music", "happy_playful.mp3")
        return "happy_playful.mp3"

    def _derive_visual_keywords(self, topic: str, niche: str) -> list:
        t = topic.lower()
        if any(w in t for w in ["cat", "kitten", "feline"]):
            return ["cute cat eyes close up", "playful kitten indoor sunlight", "sleeping cat purring soft", "cat walking outdoors garden", "funny cat jumping high", "cat nose close up detail"]
        elif any(w in t for w in ["dog", "puppy", "canine", "animal", "pet"]):
            return ["golden retriever playing outdoors", "dog nose close up detail", "cute smart dog eyes", "loyal German Shepherd forest", "playful puppy grass sunset", "happy dog running park"]
        elif any(w in t for w in ["history", "historical", "ancient", "roman", "egypt", "pyramid"]):
            return ["ancient egypt pyramid sunset", "roman colosseum marble architecture", "medieval castle fortress mist", "ancient manuscript scroll close up", "historical battle arena dust", "ancient temple glowing dusk"]
        elif any(w in t for w in ["space", "galaxy", "nasa", "planet", "star", "cosmic"]):
            return ["deep space galaxy nebula", "astronaut looking starry sky", "earth from orbit space view", "glowing cosmic particles", "alien planet horizon sunset", "supernova explosion space"]
        elif any(w in t for w in ["car", "speed", "supercar", "ferrari"]):
            return ["supercar driving highway night", "sleek sports car neon studio", "engine roaring close up detail", "luxury vehicle cockpit dashboard", "speed motion blur city night"]

        niche_info = NICHE_TEMPLATES.get(niche, NICHE_TEMPLATES["custom_niche"])
        base_keywords = list(niche_info["visual_keywords"])
        clean_topic = self._clean_topic_phrase(topic)
        if clean_topic:
            base_keywords.insert(0, f"{clean_topic} cinematic 4k")
        return base_keywords

    def _clean_topic_phrase(self, raw_topic: str) -> str:
        """Strips generic filler phrases like 'interesting fact about', 'facts about', 'tell me about'."""
        t = raw_topic.strip()
        t = re.sub(r'^(interesting|unbelievable|mind-blowing|top|best|bizarre|shocking)?\s*(facts?|mysteries|secrets?|things?)\s*(about|of|on)?\s*', '', t, flags=re.IGNORECASE)
        t = re.sub(r'^(tell me about|what is|how to|why is)\s*', '', t, flags=re.IGNORECASE)
        return t.strip() or raw_topic.strip()

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

        clean_subject = self._clean_topic_phrase(topic).capitalize()
        clean_topic_word = re.sub(r'[^a-zA-Z0-9]', '', clean_subject.split()[0]).lower() if clean_subject else "facts"
        tags = [
            f"#{niche}",
            "#shorts",
            "#viral",
            "#facts",
            "#trending",
            f"#{clean_topic_word}"
        ]

        title = f"Unbelievable Facts About {clean_subject}!" if len(clean_subject) < 35 else topic

        return {
            "niche": niche,
            "topic": topic,
            "video_type": video_type,
            "tone": tone,
            "title": title,
            "bg_music": auto_bgm,
            "estimated_duration_sec": estimated_duration,
            "seo": {
                "description": f"Explore incredible facts about {clean_subject} in this short video. Subscribe for daily mind-blowing facts!\n\n" + " ".join(tags),
                "tags": [t.replace("#", "") for t in tags]
            },
            "scenes": scenes
        }

    def _generate_shorts_scenes(self, niche: str, topic: str, tone: str, visual_keywords: list) -> list:
        kw = visual_keywords
        t_low = topic.lower()

        # KIDS BEDTIME STORIES & FAIRYTALES ENGINE
        if niche == "kids_stories" or any(w in t_low for w in ["dragon", "fairy", "bedtime", "story", "magic", "princess", "toy"]):
            scenes_content = [
                ("Hook", "Once upon a time in a magical glowing forest, lived a little dragon who was looking for a magical secret!", kw[0] if len(kw) > 0 else "3d animated cute fantasy fairy tale", "MAGICAL TALE"),
                ("Story 1", "Every night when the stars came out, the little dragon watched golden lights dance across the enchanted treetops.", kw[1] if len(kw) > 1 else "magical glowing forest 3d cartoon", "GOLDEN STARS"),
                ("Story 2", "He met a friendly wise owl who whispered: 'True magic isn't in big spells, but in sharing kindness with friends!'", kw[2] if len(kw) > 2 else "cute 3d animals playing sunset", "THE WISE SECRET"),
                ("Story 3", "With a happy smile, the little dragon shared his warm glowing spark with all the forest animals!", kw[3] if len(kw) > 3 else "colorful magical kingdom sky cartoon", "SHARING KINDNESS"),
                ("Climax", "From that night on, the enchanted kingdom shone brighter than ever before!", kw[4] if len(kw) > 4 else "charming cute dragon 3d animation", "MAGICAL KINGDOM"),
                ("CTA", "Did you love this bedtime story? Subscribe for new magical adventures every day!", kw[5] if len(kw) > 5 else "3d animated cute fantasy fairy tale", "SUBSCRIBE FOR STORIES")
            ]
        # KIDS RIDDLES ENGINE
        elif niche == "kids_riddles" or any(w in t_low for w in ["riddle", "puzzle", "brain teaser", "what am i"]):
            scenes_content = [
                ("Hook", "Ready to test your brain power? Here is a super fun riddle! Can you guess the answer before the timer ends?", kw[0] if len(kw) > 0 else "glowing question mark 3d cartoon", "FUN KIDS RIDDLE"),
                ("Riddle", "I have a face and two hands, but I have no arms or legs! What am I?", kw[1] if len(kw) > 1 else "cute detective cat 3d animation", "CAN YOU GUESS?"),
                ("Clue", "Think carefully! I tick all day long and help you know when it's time for school or bedtime!", kw[2] if len(kw) > 2 else "colorful riddle treasure box cartoon", "HERE IS A CLUE!"),
                ("Countdown", "3... 2... 1... Time is up!", kw[3] if len(kw) > 3 else "happy children thinking 3d animation", "3... 2... 1..."),
                ("Answer", "The answer is... A CLOCK! Clocks have a face and two hands!", kw[4] if len(kw) > 4 else "glowing question mark 3d cartoon", "IT'S A CLOCK!"),
                ("CTA", "Did you guess it right? Subscribe now for daily fun riddles and brain teasers!", kw[5] if len(kw) > 5 else "cute detective cat 3d animation", "SUBSCRIBE FOR MORE")
            ]
        # KIDS FUN SCIENCE & ANIMAL DISCOVERIES ENGINE
        elif niche == "kids_learning" or any(w in t_low for w in ["flamingo", "fish", "bee", "ocean", "why do"]):
            scenes_content = [
                ("Hook", "Hey kids! Did you know the ocean and animal world is full of amazing superpowers? Let's explore three fun secrets!", kw[0] if len(kw) > 0 else "cute happy animals 3d cartoon", "KIDS DISCOVERY"),
                ("Fact 1", "First, why do flamingos stand on one leg? Standing on one leg conserves body heat and takes less energy than standing on two!", kw[1] if len(kw) > 1 else "colorful space planets kids cartoon", "FLAMINGO SECRET"),
                ("Fact 2", "Second, fish don't have lungs! They use special gills to pull oxygen directly out of the water while swimming.", kw[2] if len(kw) > 2 else "playful dolphin jumping ocean 3d", "HOW FISH BREATHE"),
                ("Fact 3", "Third, honeybees visit over 2,000 flowers in a single day just to make one tiny jar of delicious honey!", kw[3] if len(kw) > 3 else "happy cute puppy running grass 3d", "BUSY HONEYBEES"),
                ("Climax", "Nature is full of incredible wonder waiting for curious minds to discover!", kw[4] if len(kw) > 4 else "colorful rainbows and clouds 3d animation", "NEVER STOP LEARNING"),
                ("CTA", "Which animal surprise was your favorite? Subscribe for more fun kids learning!", kw[5] if len(kw) > 5 else "cute happy animals 3d cartoon", "SUBSCRIBE FOR MORE")
            ]
        # CATS / FELINES DOMAIN KNOWLEDGE ENGINE
        elif any(w in t_low for w in ["cat", "kitten", "feline"]):
            scenes_content = [
                ("Hook", "Think you know cats? These three mind-blowing feline facts will completely shock you!", kw[0] if len(kw) > 0 else "cute cat eyes close up", "CAT SECRETS"),
                ("Fact 1", "First, a cat's purr vibrates between 20 and 140 Hertz—a frequency scientifically proven to heal human bones, muscles, and tendons!", kw[1] if len(kw) > 1 else "cat purring soft", "HEALING PURRS"),
                ("Fact 2", "Second, cats spend 70% of their entire lives sleeping, which means a 9-year-old cat has only been awake for 3 years!", kw[2] if len(kw) > 2 else "sleeping cat indoor", "70% LIFE SLEEPING"),
                ("Fact 3", "Third, cats have no collarbones! This unique skeletal flexibility allows them to squeeze through any opening their head fits through.", kw[3] if len(kw) > 3 else "cat walking garden", "NO COLLARBONES"),
                ("Climax", "Finally, a cat's nose print is 100% unique! Just like human fingerprints, no two cat nose prints on Earth are identical.", kw[4] if len(kw) > 4 else "cat nose close up", "UNIQUE NOSE PRINT"),
                ("CTA", "Did any of these surprise you? Subscribe now for daily incredible animal facts!", kw[5] if len(kw) > 5 else "funny cat jumping", "SUBSCRIBE FOR MORE")
            ]
        # DOGS / CANINES DOMAIN KNOWLEDGE ENGINE
        elif any(w in t_low for w in ["dog", "puppy", "canine", "pet"]):
            scenes_content = [
                ("Hook", "Think you know everything about dogs? These three mind-blowing facts will completely change how you see your pet!", kw[0] if len(kw) > 0 else "dog eyes cinematic", "CANINE SECRETS"),
                ("Fact 1", "First, a dog's nose print is 100% unique, just like a human fingerprint. No two dogs on Earth share the exact same nose pattern!", kw[1] if len(kw) > 1 else "dog nose close up", "UNIQUE NOSE PRINT"),
                ("Fact 2", "Second, dogs don't just smell food—they can actually smell human emotions! They detect tiny chemical changes in your sweat when you're stressed or happy.", kw[2] if len(kw) > 2 else "loyal dog eyes", "SMELL EMOTIONS"),
                ("Fact 3", "Third, when your dog wags its tail to the right, it means they are relaxed and happy. But a tail wag to the left indicates fear and anxiety!", kw[3] if len(kw) > 3 else "dog tail wagging", "TAIL CODE EXPOSED"),
                ("Climax", "Finally, dogs dream just like humans do. During REM sleep, their brains replay memories of playing and running with you!", kw[4] if len(kw) > 4 else "sleeping dog dreaming", "DOGS DREAM OF YOU"),
                ("CTA", "Did any of these surprise you? Subscribe now for more incredible animal facts!", kw[5] if len(kw) > 5 else "happy dog running", "SUBSCRIBE FOR MORE")
            ]
        # HISTORY DOMAIN KNOWLEDGE ENGINE
        elif any(w in t_low for w in ["history", "historical", "ancient", "roman", "egypt", "pyramid"]):
            scenes_content = [
                ("Hook", "History class lied to you! Here are three insane historical facts they never taught you in school.", kw[0] if len(kw) > 0 else "ancient egypt pyramid", "HISTORICAL TRUTHS"),
                ("Fact 1", "First, Napoleon Bonaparte was never short! At 5 feet 7 inches, he was actually above average height for a Frenchman of his time.", kw[1] if len(kw) > 1 else "roman colosseum marble", "NAPOLEON HEIGHT MYTH"),
                ("Fact 2", "Second, Cleopatra lived closer in time to the launch of the iPhone than to the construction of the Great Pyramid of Giza!", kw[2] if len(kw) > 2 else "ancient manuscript scroll", "CLEOPATRA TIMELINE"),
                ("Fact 3", "Third, ancient Romans used human urine as mouthwash because ammonia acted as a powerful natural stain remover!", kw[3] if len(kw) > 3 else "medieval castle fortress", "ROMAN MOUTHWASH"),
                ("Climax", "History is far wilder and stranger than any fiction writer could ever invent.", kw[4] if len(kw) > 4 else "historical battle arena", "WILD HISTORY"),
                ("CTA", "Which historical fact shocked you most? Subscribe for daily ancient revelations!", kw[5] if len(kw) > 5 else "ancient temple dusk", "SUBSCRIBE FOR MORE")
            ]
        # SPACE DOMAIN KNOWLEDGE ENGINE
        elif any(w in t_low for w in ["space", "galaxy", "nasa", "planet", "star"]):
            scenes_content = [
                ("Hook", "Space is far stranger than you think! Here are three terrifying cosmic facts that sound like science fiction.", kw[0] if len(kw) > 0 else "deep space galaxy", "COSMIC SECRETS"),
                ("Fact 1", "First, out in deep space, there is zero sound. Because sound requires air to travel, cosmic explosions occur in complete, haunting silence!", kw[1] if len(kw) > 1 else "glowing nebula space", "SILENCE OF SPACE"),
                ("Fact 2", "Second, on planets like Neptune and Uranus, extreme atmospheric pressure causes it to literally rain solid diamonds from the sky!", kw[2] if len(kw) > 2 else "planet atmosphere glow", "DIAMOND RAIN"),
                ("Fact 3", "Third, neutron stars spin at absurd speeds—up to 700 times per second—creating magnetic fields powerful enough to wipe credit cards from miles away!", kw[3] if len(kw) > 3 else "neutron star spinning", "NEUTRON POWER"),
                ("Climax", "And because there is no wind or liquid water on the Moon, astronaut footprints left 50 years ago will remain preserved for 100 million years!", kw[4] if len(kw) > 4 else "moon surface footprints", "PRESERVED FOREVER"),
                ("CTA", "Which cosmic mystery shocked you most? Subscribe for daily space discoveries!", kw[5] if len(kw) > 5 else "glowing starry night", "SUBSCRIBE FOR MORE")
            ]
        # PSYCHOLOGY DOMAIN KNOWLEDGE ENGINE
        elif any(w in t_low for w in ["manipulate", "psychology", "mind", "silence", "narcissist", "dark"]):
            scenes_content = [
                ("Hook", "Here are three dark psychological tactics people secretly use to control conversations without you noticing.", kw[0] if len(kw) > 0 else "dark shadow silhouette", "DARK PSYCHOLOGY"),
                ("Fact 1", "First, the Power of Strategic Silence. When someone gives you a weak answer, stay completely quiet and maintain eye contact. They will naturally spill the truth just to break the uncomfortable tension!", kw[1] if len(kw) > 1 else "dramatic silhouette", "SILENCE TECHNIQUE"),
                ("Fact 2", "Second, the Choice Illusion. Manipulators never ask yes or no. They offer two choices that both lead to the exact outcome they wanted in the first place!", kw[2] if len(kw) > 2 else "dark neon street", "FALSE CHOICES"),
                ("Fact 3", "Third, the Ben Franklin Effect. Asking someone for a tiny favor tricks their brain into believing they genuinely like and trust you!", kw[3] if len(kw) > 3 else "rainy city night", "BRAIN TRICK"),
                ("Climax", "Once you recognize these subconscious patterns, nobody can ever manipulate your choices again.", kw[4] if len(kw) > 4 else "mysterious noir light", "UNTOUCHABLE MIND"),
                ("CTA", "Have you ever experienced these tactics? Subscribe for powerful psychological insights!", kw[5] if len(kw) > 5 else "abstract neon glow", "SUBSCRIBE FOR MORE")
            ]
        # WEALTH / MONEY DOMAIN KNOWLEDGE ENGINE
        elif any(w in t_low for w in ["money", "wealth", "finance", "rich", "broke"]):
            scenes_content = [
                ("Hook", "Want to break the broke cycle? Here are three harsh financial truths the top 1% use to build massive wealth!", kw[0] if len(kw) > 0 else "luxury skyscraper skyline", "WEALTH RULES"),
                ("Fact 1", "First, poor people spend money to look rich, while wealthy people invest money to buy assets that generate income while they sleep!", kw[1] if len(kw) > 1 else "gold money stack", "ASSETS VS LIABILITIES"),
                ("Fact 2", "Second, inflation silently destroys cash sitting in bank accounts. If your money isn't earning returns above inflation, you are losing purchasing power every single day!", kw[2] if len(kw) > 2 else "stock market chart green", "INFLATION TRAP"),
                ("Fact 3", "Third, compound interest is the eighth wonder of the world. Investing small amounts consistently in your 20s produces exponentially more wealth than starting late with millions!", kw[3] if len(kw) > 3 else "financial network data", "COMPOUND POWER"),
                ("Climax", "Master your money mindset today, or you will spend your entire life working for someone else's dreams.", kw[4] if len(kw) > 4 else "private jet sunset", "OWN YOUR FUTURE"),
                ("CTA", "Ready to build true financial freedom? Subscribe for daily wealth strategies!", kw[5] if len(kw) > 5 else "city skyline sunset", "SUBSCRIBE FOR MORE")
            ]
        # STOICISM DOMAIN KNOWLEDGE ENGINE
        elif any(w in t_low for w in ["stoic", "marcus", "philosophy", "aurelius", "calm"]):
            scenes_content = [
                ("Hook", "Feeling overwhelmed by life? Here are three timeless Stoic principles from Emperor Marcus Aurelius to master your mind.", kw[0] if len(kw) > 0 else "statue dusk sunset", "STOIC WISDOM"),
                ("Fact 1", "First, you have power over your mind, not outside events. Realize this, and you will find instant unshakeable strength!", kw[1] if len(kw) > 1 else "mountaintop fog sunrise", "CONTROL YOUR MIND"),
                ("Fact 2", "Second, the impediment to action advances action. What stands in the way becomes the way forward!", kw[2] if len(kw) > 2 else "ancient temple ruins", "OBSTACLE IS WAY"),
                ("Fact 3", "Third, remember Memento Mori—that you are mortal. Knowing your time is limited frees you from wasting energy on meaningless drama!", kw[3] if len(kw) > 3 else "lonely cliff warrior", "MEMENTO MORI"),
                ("Climax", "When you stop reacting to chaos and focus solely on your internal discipline, nothing in this world can disturb your peace.", kw[4] if len(kw) > 4 else "calm ocean waves", "UNBREAKABLE PEACE"),
                ("CTA", "Which Stoic lesson resonated with you most? Subscribe for ancient wisdom!", kw[5] if len(kw) > 5 else "horizon sunset view", "SUBSCRIBE FOR MORE")
            ]
        # DYNAMIC CUSTOM SUBJECT ENGINE (NO ROBOTIC TEMPLATES!)
        else:
            clean_sub = self._clean_topic_phrase(topic).strip()
            if not clean_sub:
                clean_sub = "this fascinating subject"
            
            scenes_content = [
                ("Hook", f"Here are three mind-blowing facts about {clean_sub} that most people have never heard before!", kw[0] if len(kw) > 0 else "cinematic intro glow", f"SECRETS OF {clean_sub.upper()[:14]}"),
                ("Fact 1", f"First, historical analysis reveals that early discoveries surrounding {clean_sub} completely altered how experts understood its core mechanics.", kw[1] if len(kw) > 1 else "dramatic mystery lighting", "HISTORICAL FACT"),
                ("Fact 2", f"Second, modern scientific testing proves that key elements of {clean_sub} produce surprising physical and psychological effects!", kw[2] if len(kw) > 2 else "futuristic abstract grid", "SCIENTIFIC BREAKTHROUGH"),
                ("Fact 3", f"Third, researchers spent years uncovering how subtle changes in {clean_sub} impact daily human behavior without us noticing.", kw[3] if len(kw) > 3 else "high tech matrix stream", "HIDDEN PATTERNS"),
                ("Climax", f"Understanding the true nature of {clean_sub} gives you a whole new perspective on how the world operates.", kw[4] if len(kw) > 4 else "epic glowing horizon", "NEW PERSPECTIVE"),
                ("CTA", f"Did learning about {clean_sub} surprise you? Subscribe now for daily mind-blowing facts!", kw[5] if len(kw) > 5 else "aesthetic sunset sky", "SUBSCRIBE FOR MORE")
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
        clean_sub = self._clean_topic_phrase(topic)
        kw = visual_keywords
        return [
            {
                "scene_num": 1,
                "type": "Introduction",
                "text": f"Welcome back. Today we are uncovering the unbelievable truth about {clean_sub}.",
                "search_term": kw[0] if len(kw) > 0 else "epic opening cinematic",
                "on_screen_text": clean_sub.upper()[:24]
            },
            {
                "scene_num": 2,
                "type": "Historical Context",
                "text": f"To understand {clean_sub}, we must look back at how this hidden phenomenon first began.",
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
