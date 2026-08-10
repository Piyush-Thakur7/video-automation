import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Video, Sparkles, Play, Pause, Layers, RefreshCw, Upload,
  CheckCircle, AlertCircle, Settings, Film, Music, Mic, FileText, Download,
  ExternalLink, BarChart3, ChevronRight, Zap, PlayCircle, Plus, Eye, Clock, Radio
} from 'lucide-react';

const Youtube = ({ size = 24, color = "currentColor" }) => (
  <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="2.5 17a24.12 24.12 0 0 1 0-10 2 2 0 0 1 1.4-1.4 49.56 49.56 0 0 1 16.2 0A2 2 0 0 1 21.5 7a24.12 24.12 0 0 1 0 10 2 2 0 0 1-1.4 1.4 49.56 49.56 0 0 1-16.2 0A2 2 0 0 1 2.5 17" fill="currentColor" fillOpacity="0.2" />
    <path d="M10 15l5-3-5-3v6z" fill="currentColor" />
  </svg>
);

const RENDER_BACKEND = 'https://video-automation-7cvy.onrender.com/api';
const LOCAL_BACKEND = 'http://127.0.0.1:8000/api';

const API_BASE = localStorage.getItem('AUTOTUBE_API_BASE') || LOCAL_BACKEND;

const BGM_TRACKS = [
  { id: "none", name: "🔇 No Background Music (Pure Voiceover)", url: null },
  { id: "happy_playful.mp3", name: "🐶 Happy Playful (Dogs, Pets, Funny)", url: "/storage/bgm/happy_playful.mp3" },
  { id: "lofi_chill.mp3", name: "☕ Lofi Chill (Relaxing, Nature)", url: "/storage/bgm/lofi_chill.mp3" },
  { id: "dark_suspense.mp3", name: "Dark Suspense Ambient", url: "/storage/bgm/dark_suspense.mp3" },
  { id: "upbeat_cyber.mp3", name: "Upbeat Cyber Synth", url: "/storage/bgm/upbeat_cyber.mp3" },
  { id: "tech_ambient.mp3", name: "Tech Ambient Futuristic", url: "/storage/bgm/tech_ambient.mp3" },
  { id: "inspiring_modern.mp3", name: "Inspiring Modern Atmosphere", url: "/storage/bgm/inspiring_modern.mp3" },
  { id: "cinematic_epic.mp3", name: "Cinematic Epic Drone", url: "/storage/bgm/cinematic_epic.mp3" },
  { id: "scary_drone.mp3", name: "Scary Mystery Tension", url: "/storage/bgm/scary_drone.mp3" },
  { id: "triumphant_build.mp3", name: "Triumphant Motivation Build", url: "/storage/bgm/triumphant_build.mp3" }
];

export default function App() {
  const [activeTab, setActiveTab] = useState('creator');

  // Engine state
  const [niches, setNiches] = useState([]);
  const [voices, setVoices] = useState([]);
  const [videos, setVideos] = useState([]);
  const [ytStatus, setYtStatus] = useState({ authenticated: false });
  const [autoPilotStatus, setAutoPilotStatus] = useState({ enabled: false, history: [] });

  // Custom BGM state
  const [serverBgmTracks, setServerBgmTracks] = useState([]);
  const [customBgmTracks, setCustomBgmTracks] = useState([]);
  const [bgmAudioObj, setBgmAudioObj] = useState(null);
  const [isPlayingBgm, setIsPlayingBgm] = useState(false);

  // Creator state
  const [selectedNiche, setSelectedNiche] = useState('dark_psychology');
  const [topicInput, setTopicInput] = useState('');
  const [videoType, setVideoType] = useState('shorts');
  const [selectedVoice, setSelectedVoice] = useState('en-US-ChristopherNeural');
  const [selectedBgm, setSelectedBgm] = useState('none');
  
  const [isGeneratingScript, setIsGeneratingScript] = useState(false);
  const [scriptData, setScriptData] = useState(null);
  
  const [isRendering, setIsRendering] = useState(false);
  const [currentJobId, setCurrentJobId] = useState(null);
  const [renderProgress, setRenderProgress] = useState(0);
  const [renderMessage, setRenderMessage] = useState('');
  const [renderedResult, setRenderedResult] = useState(null);

  // Selected video for player/upload
  const [activeVideo, setActiveVideo] = useState(null);

  // Channel Profile State ('quantum_facts' vs 'kids_wonder')
  const [activeProfile, setActiveProfile] = useState('quantum_facts');

  // YouTube Upload Form
  const [ytUploadData, setYtUploadData] = useState({
    title: '',
    description: '',
    tags: '',
    privacy: 'private'
  });
  const [clientSecretsInput, setClientSecretsInput] = useState('');
  const [isUploadingYt, setIsUploadingYt] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);

  // AutoPilot Config Form
  const [autoInterval, setAutoInterval] = useState(60);
  const [autoPrivacy, setAutoPrivacy] = useState('private');

  useEffect(() => {
    fetchNiches();
    fetchVoices();
    fetchBgmTracks();
    fetchLibrary();
    fetchYtStatus();
    fetchAutoPilotStatus();
  }, []);

  // Poll render job status if active
  useEffect(() => {
    let interval;
    if (currentJobId && isRendering) {
      interval = setInterval(async () => {
        try {
          const res = await axios.get(`${API_BASE}/video/status/${currentJobId}`);
          const data = res.data;
          setRenderProgress(data.progress || 0);
          setRenderMessage(data.message || '');
          
          if (data.status === 'completed') {
            setIsRendering(false);
            setRenderedResult(data.output);
            fetchLibrary();
            clearInterval(interval);
          } else if (data.status === 'failed') {
            setIsRendering(false);
            alert(`Rendering failed: ${data.error}`);
            clearInterval(interval);
          }
        } catch (e) {
          console.error(e);
        }
      }, 1500);
    }
    return () => clearInterval(interval);
  }, [currentJobId, isRendering]);

  const fetchNiches = async () => {
    try {
      const res = await axios.get(`${API_BASE}/niches`);
      setNiches(res.data.niches || []);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchVoices = async () => {
    try {
      const res = await axios.get(`${API_BASE}/tts/voices`);
      setVoices(res.data.voices || []);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchLibrary = async () => {
    try {
      const res = await axios.get(`${API_BASE}/video/library`);
      setVideos(res.data.videos || []);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchYtStatus = async () => {
    try {
      const res = await axios.get(`${API_BASE}/youtube/status`);
      setYtStatus(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchAutoPilotStatus = async () => {
    try {
      const res = await axios.get(`${API_BASE}/autopilot/status`);
      setAutoPilotStatus(res.data);
      setAutoInterval(res.data.interval_minutes || 60);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchBgmTracks = async () => {
    try {
      const res = await axios.get(`${API_BASE}/bgm/tracks`);
      if (res.data.tracks && res.data.tracks.length > 0) {
        setServerBgmTracks(res.data.tracks);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleGenerateScript = async () => {
    setIsGeneratingScript(true);
    setRenderedResult(null);
    try {
      const rawTopic = topicInput.trim();
      const cleanTopic = (rawTopic.toLowerCase().includes('type any custom') || rawTopic.toLowerCase().includes('placeholder')) ? '' : rawTopic;
      const targetNiche = cleanTopic ? 'custom_niche' : selectedNiche;
      const res = await axios.post(`${API_BASE}/script/generate`, {
        niche: targetNiche,
        topic: cleanTopic,
        video_type: videoType
      });
      if (res.data.success) {
        setScriptData(res.data.script);
        if (res.data.script.bg_music) {
          setSelectedBgm(res.data.script.bg_music);
        }
        setYtUploadData({
          title: res.data.script.title,
          description: res.data.script.seo.description,
          tags: res.data.script.seo.tags.join(', '),
          privacy: 'private'
        });
      }
    } catch (e) {
      alert(`Script error: ${e.response?.data?.detail || e.message}`);
    } finally {
      setIsGeneratingScript(false);
    }
  };

  const handleVoicePreview = async () => {
    try {
      const res = await axios.post(`${API_BASE}/tts/preview?voice_id=${selectedVoice}&text=AutoTube%20AI%20Voice%20Synthesis%20Test`);
      if (res.data.audio_url) {
        const audio = new Audio(`${API_BASE}${res.data.audio_url}`);
        audio.play();
      }
    } catch (e) {
      console.error(e);
    }
  };

  const handleToggleBgmPreview = () => {
    if (isPlayingBgm && bgmAudioObj) {
      bgmAudioObj.pause();
      setIsPlayingBgm(false);
      return;
    }

    const allTracks = [...BGM_TRACKS, ...customBgmTracks];
    const target = allTracks.find(t => t.id === selectedBgm);
    if (!target || !target.url) {
      alert("No background music selected (Pure Voiceover mode is active).");
      return;
    }

    const audioUrl = `${API_BASE}${target.url.startsWith('/') ? '' : '/'}${target.url}`;
    const audio = new Audio(audioUrl);
    audio.onended = () => setIsPlayingBgm(false);
    audio.play();
    setBgmAudioObj(audio);
    setIsPlayingBgm(true);
  };

  const handleCustomBgmUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await axios.post(`${API_BASE}/bgm/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      if (res.data.success) {
        const newTrack = {
          id: res.data.filename,
          name: `🎵 Custom: ${res.data.filename}`,
          url: res.data.url
        };
        setCustomBgmTracks(prev => [...prev, newTrack]);
        setSelectedBgm(res.data.filename);
        alert(`✓ Custom MP3 uploaded & selected: ${res.data.filename}`);
      }
    } catch (err) {
      alert(`Upload Error: ${err.response?.data?.detail || err.message}`);
    }
  };

  const handleStartRender = async () => {
    if (!scriptData) return;
    setIsRendering(true);
    setRenderProgress(0);
    setRenderMessage('Initiating video render pipeline...');

    try {
      const res = await axios.post(`${API_BASE}/video/render`, {
        script_data: scriptData,
        voice_id: selectedVoice,
        bgm_track: selectedBgm
      });
      if (res.data.job_id) {
        setCurrentJobId(res.data.job_id);
      }
    } catch (e) {
      setIsRendering(false);
      alert(`Render start error: ${e.message}`);
    }
  };

  const handleYouTubeUpload = async () => {
    if (!activeVideo && !renderedResult) return;
    const vPath = activeVideo ? activeVideo.path : renderedResult.output_path;

    setIsUploadingYt(true);
    setUploadResult(null);
    try {
      const res = await axios.post(`${API_BASE}/youtube/upload`, {
        video_path: vPath,
        title: ytUploadData.title,
        description: ytUploadData.description,
        tags: ytUploadData.tags.split(',').map(t => t.trim()),
        privacy_status: ytUploadData.privacy
      });
      setUploadResult(res.data);
    } catch (e) {
      setUploadResult({ success: false, error: e.message });
    } finally {
      setIsUploadingYt(false);
    }
  };

  const handleSaveClientSecrets = async () => {
    if (!clientSecretsInput.trim()) return;
    try {
      const res = await axios.post(`${API_BASE}/youtube/credentials?client_secrets_json=${encodeURIComponent(clientSecretsInput)}`);
      alert(res.data.message);
      fetchYtStatus();
    } catch (e) {
      alert(`Error saving credentials: ${e.response?.data?.detail || e.message}`);
    }
  };

  const handleToggleAutoPilot = async () => {
    const newState = !autoPilotStatus.enabled;
    try {
      const res = await axios.post(`${API_BASE}/autopilot/toggle?enable=${newState}`);
      if (res.data.success) {
        fetchAutoPilotStatus();
      }
    } catch (e) {
      alert(`AutoPilot error: ${e.message}`);
    }
  };

  const handleSaveAutoConfig = async () => {
    try {
      const res = await axios.post(`${API_BASE}/autopilot/config`, {
        interval_minutes: parseInt(autoInterval),
        privacy_status: autoPrivacy,
        video_type: videoType,
        voice_id: selectedVoice
      });
      if (res.data.success) {
        alert('AutoPilot schedule updated successfully!');
        fetchAutoPilotStatus();
      }
    } catch (e) {
      alert(`AutoPilot config error: ${e.message}`);
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', backgroundColor: 'var(--bg-dark)' }}>
      {/* Sidebar Navigation */}
      <aside style={{ width: '260px', background: '#0c1220', borderRight: '1px solid var(--border-color)', padding: '24px 16px', display: 'flex', flexDirection: 'column', gap: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ background: 'linear-gradient(135deg, #ff0055, #8b5cf6)', width: '40px', height: '40px', borderRadius: '10px', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 15px rgba(255,0,85,0.4)' }}>
            <Youtube size={24} color="#fff" />
          </div>
          <div>
            <h2 style={{ fontSize: '1.2rem', fontWeight: 800, background: 'linear-gradient(90deg, #fff, #94a3b8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              AutoTube <span style={{ color: '#ff0055', WebkitTextFillColor: '#ff0055' }}>AI</span>
            </h2>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-dim)' }}>v1.0 Automation Hub</p>
          </div>
        </div>

        {/* Channel Profile Switcher */}
        <div style={{ background: 'rgba(255,255,255,0.04)', padding: '12px', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.08)' }}>
          <p style={{ fontSize: '0.68rem', textTransform: 'uppercase', letterSpacing: '1px', color: 'var(--text-dim)', marginBottom: '8px', fontWeight: 700 }}>Active Channel Profile</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <button
              onClick={() => {
                setActiveProfile('quantum_facts');
                setSelectedNiche('dark_psychology');
                setSelectedVoice('en-US-ChristopherNeural');
                setSelectedBgm('none');
              }}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 10px', borderRadius: '8px',
                background: activeProfile === 'quantum_facts' ? 'rgba(139,92,246,0.2)' : 'transparent',
                border: activeProfile === 'quantum_facts' ? '1px solid #8b5cf6' : '1px solid transparent',
                color: activeProfile === 'quantum_facts' ? '#c084fc' : 'var(--text-muted)',
                cursor: 'pointer', textAlign: 'left', fontWeight: 600, fontSize: '0.8rem'
              }}
            >
              🌌 Quantum Facts (Main)
            </button>
            <button
              onClick={() => {
                setActiveProfile('kids_wonder');
                setSelectedNiche('kids_stories');
                setSelectedVoice('en-US-AnaNeural');
                setSelectedBgm('happy_playful.mp3');
              }}
              style={{
                display: 'flex', alignItems: 'center', gap: '8px', padding: '8px 10px', borderRadius: '8px',
                background: activeProfile === 'kids_wonder' ? 'rgba(236,72,153,0.2)' : 'transparent',
                border: activeProfile === 'kids_wonder' ? '1px solid #ec4899' : '1px solid transparent',
                color: activeProfile === 'kids_wonder' ? '#f472b6' : 'var(--text-muted)',
                cursor: 'pointer', textAlign: 'left', fontWeight: 600, fontSize: '0.8rem'
              }}
            >
              🎈 Kids Wonder (Children)
            </button>
          </div>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <button
            onClick={() => setActiveTab('dashboard')}
            className="btn-secondary"
            style={{
              justifyContent: 'flex-start',
              background: activeTab === 'dashboard' ? 'rgba(255,0,85,0.12)' : 'transparent',
              borderColor: activeTab === 'dashboard' ? 'rgba(255,0,85,0.4)' : 'transparent',
              color: activeTab === 'dashboard' ? '#ff0055' : 'var(--text-muted)'
            }}
          >
            <BarChart3 size={18} /> Studio Overview
          </button>
          
          <button
            onClick={() => setActiveTab('creator')}
            className="btn-secondary"
            style={{
              justifyContent: 'flex-start',
              background: activeTab === 'creator' ? 'rgba(255,0,85,0.12)' : 'transparent',
              borderColor: activeTab === 'creator' ? 'rgba(255,0,85,0.4)' : 'transparent',
              color: activeTab === 'creator' ? '#ff0055' : 'var(--text-muted)'
            }}
          >
            <Sparkles size={18} /> AI Video Studio
          </button>

          <button
            onClick={() => setActiveTab('autopilot')}
            className="btn-secondary"
            style={{
              justifyContent: 'flex-start',
              background: activeTab === 'autopilot' ? 'rgba(255,0,85,0.12)' : 'transparent',
              borderColor: activeTab === 'autopilot' ? 'rgba(255,0,85,0.4)' : 'transparent',
              color: activeTab === 'autopilot' ? '#ff0055' : 'var(--text-muted)'
            }}
          >
            <Radio size={18} color={autoPilotStatus.enabled ? "#10b981" : "var(--text-muted)"} /> Auto-Pilot Scheduler
          </button>

          <button
            onClick={() => setActiveTab('library')}
            className="btn-secondary"
            style={{
              justifyContent: 'flex-start',
              background: activeTab === 'library' ? 'rgba(255,0,85,0.12)' : 'transparent',
              borderColor: activeTab === 'library' ? 'rgba(255,0,85,0.4)' : 'transparent',
              color: activeTab === 'library' ? '#ff0055' : 'var(--text-muted)'
            }}
          >
            <Film size={18} /> Video Library ({videos.length})
          </button>

          <button
            onClick={() => setActiveTab('youtube')}
            className="btn-secondary"
            style={{
              justifyContent: 'flex-start',
              background: activeTab === 'youtube' ? 'rgba(255,0,85,0.12)' : 'transparent',
              borderColor: activeTab === 'youtube' ? 'rgba(255,0,85,0.4)' : 'transparent',
              color: activeTab === 'youtube' ? '#ff0055' : 'var(--text-muted)'
            }}
          >
            <Youtube size={18} /> YouTube Publishing
          </button>

          <button
            onClick={() => setActiveTab('settings')}
            className="btn-secondary"
            style={{
              justifyContent: 'flex-start',
              background: activeTab === 'settings' ? 'rgba(255,0,85,0.12)' : 'transparent',
              borderColor: activeTab === 'settings' ? 'rgba(255,0,85,0.4)' : 'transparent',
              color: activeTab === 'settings' ? '#ff0055' : 'var(--text-muted)'
            }}
          >
            <Settings size={18} /> API & Credentials
          </button>
        </nav>

        <div style={{ marginTop: 'auto', padding: '16px', background: 'rgba(255,255,255,0.03)', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <Zap size={16} color="#10b981" />
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>System Status</span>
          </div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Pexels Stock: <span style={{ color: '#10b981' }}>Active</span></p>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Auto-Pilot: <span style={{ color: autoPilotStatus.enabled ? '#10b981' : '#fbbf24' }}>{autoPilotStatus.enabled ? 'Running' : 'Standby'}</span></p>
        </div>
      </aside>

      {/* Main Content View */}
      <main style={{ flex: 1, padding: '32px 40px', overflowY: 'auto', maxWidth: '1400px' }}>
        
        {/* TAB 1: STUDIO OVERVIEW */}
        {activeTab === 'dashboard' && (
          <div>
            <header style={{ marginBottom: '32px' }}>
              <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '8px' }}>YouTube Automation Studio</h1>
              <p style={{ color: 'var(--text-muted)' }}>Manage channels, generate viral scripts, synthesize audio, and automate 1080p video production.</p>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '20px', marginBottom: '32px' }}>
              <div className="glass-card" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Rendered Videos</span>
                  <Film size={20} color="#ff0055" />
                </div>
                <h3 style={{ fontSize: '1.8rem', fontWeight: 700 }}>{videos.length}</h3>
                <p style={{ fontSize: '0.8rem', color: '#34d399', marginTop: '4px' }}>+100% Ready for publish</p>
              </div>

              <div className="glass-card" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Auto-Pilot Mode</span>
                  <Radio size={20} color={autoPilotStatus.enabled ? "#10b981" : "#fbbf24"} />
                </div>
                <h3 style={{ fontSize: '1.8rem', fontWeight: 700 }}>{autoPilotStatus.enabled ? 'ACTIVE' : 'OFF'}</h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>Every {autoPilotStatus.interval_minutes} mins</p>
              </div>

              <div className="glass-card" style={{ padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px' }}>
                  <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>YouTube Channel</span>
                  <Youtube size={20} color="#00f2fe" />
                </div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 600, color: ytStatus.authenticated ? '#34d399' : '#fbbf24' }}>
                  {ytStatus.authenticated ? ytStatus.channel.title : 'Ready for Client Secrets'}
                </h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>Auto-publish API v3</p>
              </div>
            </div>

            <div className="glass-card" style={{ padding: '32px', marginBottom: '32px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
                <Sparkles size={24} color="#ff0055" />
                <h2 style={{ fontSize: '1.4rem', fontWeight: 700 }}>Quick 1-Click Video Creator</h2>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr auto', gap: '16px', alignItems: 'end' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Target Niche</label>
                  <select className="select-field" value={selectedNiche} onChange={(e) => setSelectedNiche(e.target.value)}>
                    {niches.map(n => <option key={n.key} value={n.key}>{n.name}</option>)}
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Format</label>
                  <select className="select-field" value={videoType} onChange={(e) => setVideoType(e.target.value)}>
                    <option value="shorts">YouTube Shorts (9:16 Vertical)</option>
                    <option value="longform">Landscape Video (16:9 1080p)</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Topic (Optional)</label>
                  <input type="text" className="input-field" placeholder="e.g. Secret Rules of Body Language" value={topicInput} onChange={(e) => setTopicInput(e.target.value)} />
                </div>

                <button className="btn-primary" onClick={() => { setActiveTab('creator'); handleGenerateScript(); }}>
                  <Zap size={18} /> Launch Studio
                </button>
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: AI VIDEO CREATOR & STUDIO */}
        {activeTab === 'creator' && (
          <div>
            <header style={{ marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '6px' }}>
                  <h1 style={{ fontSize: '2rem', fontWeight: 700 }}>AI Content Creator & Pipeline</h1>
                  {activeProfile === 'kids_wonder' ? (
                    <span style={{ background: 'rgba(236,72,153,0.2)', border: '1px solid #ec4899', color: '#f472b6', padding: '4px 12px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                      🎈 Kids Content Mode (COPPA Safe & 3D Animated Visuals)
                    </span>
                  ) : (
                    <span style={{ background: 'rgba(139,92,246,0.2)', border: '1px solid #8b5cf6', color: '#c084fc', padding: '4px 12px', borderRadius: '20px', fontSize: '0.8rem', fontWeight: 700, display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                      🌌 Quantum Facts Mode (Science & Adult Knowledge)
                    </span>
                  )}
                </div>
                <p style={{ color: 'var(--text-muted)' }}>Design AI scripts, select background music, preview scene beats, and render 1080p MP4.</p>
              </div>
              
              <button className="btn-primary" onClick={handleGenerateScript} disabled={isGeneratingScript}>
                {isGeneratingScript ? <RefreshCw size={18} className="animate-spin" /> : <Sparkles size={18} />}
                {isGeneratingScript ? 'Generating AI Script...' : 'Generate New Script'}
              </button>
            </header>

            <div className="glass-card" style={{ padding: '24px', marginBottom: '28px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', marginBottom: '16px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Niche Preset</label>
                  <select className="select-field" value={selectedNiche} onChange={(e) => setSelectedNiche(e.target.value)}>
                    {niches.map(n => <option key={n.key} value={n.key}>{n.name}</option>)}
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                    {selectedNiche === 'custom_niche' ? '✨ Custom Niche / Topic (Type Anything)' : 'Topic / Key Subject (Optional)'}
                  </label>
                  <input 
                    type="text" 
                    className="input-field" 
                    placeholder={selectedNiche === 'custom_niche' ? 'e.g. Saffron Secrets, Black Hole Gravity, Stoic Rules...' : 'e.g. Unspoken Signs of Manipulation'} 
                    value={topicInput} 
                    onChange={(e) => {
                      setTopicInput(e.target.value);
                      if (e.target.value.trim().length > 0) {
                        setSelectedNiche('custom_niche');
                      }
                    }}
                    style={{ borderColor: selectedNiche === 'custom_niche' ? '#ff0055' : 'var(--border-color)' }}
                  />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Aspect Ratio</label>
                  <select className="select-field" value={videoType} onChange={(e) => setVideoType(e.target.value)}>
                    <option value="shorts">YouTube Shorts (9:16 Vertical)</option>
                    <option value="longform">Long-form Video (16:9 Horizontal)</option>
                  </select>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>TTS Voice Actor</label>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    <select className="select-field" value={selectedVoice} onChange={(e) => setSelectedVoice(e.target.value)}>
                      {voices.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
                    </select>
                    <button className="btn-secondary" onClick={handleVoicePreview} title="Listen sample"><Mic size={16} color="#ff0055" /></button>
                  </div>
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Background Music Track</label>
                  <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
                    <select className="select-field" value={selectedBgm} onChange={(e) => setSelectedBgm(e.target.value)}>
                      {[...BGM_TRACKS, ...customBgmTracks].map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
                    </select>

                    <label className="btn-secondary" style={{ cursor: 'pointer', padding: '0 12px', display: 'flex', alignItems: 'center', gap: '6px' }} title="Upload Custom MP3 Track">
                      <Upload size={16} color="#34d399" />
                      <span style={{ fontSize: '0.8rem' }}>Upload MP3</span>
                      <input type="file" accept="audio/mp3,audio/mpeg" style={{ display: 'none' }} onChange={handleCustomBgmUpload} />
                    </label>
                  </div>

                  {selectedBgm !== 'none' && (() => {
                    const allTracks = [...(serverBgmTracks.length > 0 ? serverBgmTracks : BGM_TRACKS), ...customBgmTracks];
                    const target = allTracks.find(t => t.id === selectedBgm);
                    const cleanApiHost = API_BASE.replace(/\/api\/?$/, '');
                    const rawUrl = target && target.url ? target.url : `/storage/bgm/${selectedBgm}`;
                    const audioSrc = `${cleanApiHost}${rawUrl.startsWith('/') ? '' : '/'}${rawUrl}`;
                    return (
                      <div style={{ marginTop: '8px', background: 'rgba(15, 23, 42, 0.8)', padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                        <p style={{ fontSize: '0.75rem', color: '#34d399', marginBottom: '6px', fontWeight: 600 }}>🎵 Audio Preview Player ({target ? target.name : selectedBgm}):</p>
                        <audio 
                          key={audioSrc}
                          controls 
                          preload="auto"
                          style={{ width: '100%', height: '36px', borderRadius: '6px' }}
                          src={audioSrc}
                        >
                          <source src={audioSrc} type="audio/mpeg" />
                          Your browser does not support audio elements.
                        </audio>
                      </div>
                    );
                  })()}
                </div>
              </div>
            </div>

            {scriptData && (
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '28px' }}>
                <div>
                  <div className="glass-card" style={{ padding: '24px', marginBottom: '24px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                      <div>
                        <span className={scriptData.video_type === 'shorts' ? 'badge badge-shorts' : 'badge badge-longform'}>
                          {scriptData.video_type === 'shorts' ? 'Shorts 9:16' : 'Landscape 16:9'}
                        </span>
                        <h2 style={{ fontSize: '1.4rem', fontWeight: 700, marginTop: '8px' }}>{scriptData.title}</h2>
                      </div>
                      <span style={{ fontSize: '0.9rem', color: 'var(--gold)', fontWeight: 600 }}>~{scriptData.estimated_duration}s duration</span>
                    </div>

                    <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '16px' }}>Scene Beats & Visual Overlay Plan</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                      {scriptData.scenes.map((scene, idx) => (
                        <div key={idx} style={{ background: 'rgba(15, 23, 42, 0.6)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '16px' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                            <span style={{ fontWeight: 700, fontSize: '0.85rem', color: '#ff0055' }}>SCENE {scene.scene_number} • {scene.type}</span>
                            <span style={{ fontSize: '0.8rem', color: 'var(--text-dim)' }}>Pexels/Stock Search: {scene.search_term}</span>
                          </div>
                          
                          <p style={{ fontSize: '0.95rem', lineHeight: '1.5', marginBottom: '10px' }}>"{scene.text}"</p>
                          
                          <div style={{ display: 'flex', gap: '12px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                            <span style={{ background: 'rgba(251, 191, 36, 0.15)', color: '#fbbf24', padding: '2px 8px', borderRadius: '4px' }}>
                              Screen Banner: {scene.overlay_text}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                <div>
                  <div className="glass-card" style={{ padding: '24px', position: 'sticky', top: '24px' }}>
                    <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px' }}>Render Engine Pipeline</h3>

                    {!isRendering && !renderedResult && (
                      <div>
                        <button className="btn-primary" style={{ width: '100%', justifyContent: 'center' }} onClick={handleStartRender}>
                          <Film size={20} /> Render 1080p Video Now
                        </button>
                      </div>
                    )}

                    {isRendering && (
                      <div style={{ textAlign: 'center', padding: '16px 0' }}>
                        <div style={{ height: '8px', background: 'rgba(255,255,255,0.1)', borderRadius: '9999px', overflow: 'hidden', marginBottom: '16px' }}>
                          <div className="progress-bar-fill" style={{ width: `${renderProgress}%` }}></div>
                        </div>
                        <h4 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#ff0055', marginBottom: '8px' }}>{renderProgress}%</h4>
                        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{renderMessage}</p>
                      </div>
                    )}

                    {renderedResult && (
                      <div>
                        <div style={{ background: 'rgba(16, 185, 129, 0.1)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '16px', borderRadius: '12px', marginBottom: '16px', textAlign: 'center' }}>
                          <CheckCircle size={32} color="#34d399" style={{ margin: '0 auto 8px' }} />
                          <h4 style={{ fontWeight: 700, color: '#34d399' }}>Render Completed!</h4>
                          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Output: {renderedResult.file_size_mb} MB ({renderedResult.resolution})</p>
                        </div>

                        <video src={`http://127.0.0.1:8000${renderedResult.video_url}`} controls autoPlay style={{ width: '100%', borderRadius: '10px', marginBottom: '16px', background: '#000' }} />

                        <div style={{ display: 'flex', gap: '8px' }}>
                          <a href={`http://127.0.0.1:8000${renderedResult.video_url}`} download className="btn-secondary" style={{ flex: 1, justifyContent: 'center' }}>
                            <Download size={16} /> Save
                          </a>
                          <button className="btn-primary" style={{ flex: 1, justifyContent: 'center' }} onClick={() => { setActiveVideo({ path: renderedResult.output_path, url: renderedResult.video_url }); setActiveTab('youtube'); }}>
                            <Youtube size={16} /> Publish
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

              </div>
            )}
          </div>
        )}

        {/* TAB 3: AUTOPILOT SCHEDULER */}
        {activeTab === 'autopilot' && (
          <div>
            <header style={{ marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '4px' }}>24/7 Autonomous Auto-Pilot</h1>
                <p style={{ color: 'var(--text-muted)' }}>Fully automated hands-free video generation & YouTube channel publishing on a recurring schedule.</p>
              </div>

              <button
                className="btn-primary"
                onClick={handleToggleAutoPilot}
                style={{
                  background: autoPilotStatus.enabled ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' : 'linear-gradient(135deg, #ff0055 0%, #d90429 100%)',
                  boxShadow: autoPilotStatus.enabled ? '0 4px 15px rgba(16, 185, 129, 0.4)' : '0 4px 15px rgba(255, 0, 85, 0.4)'
                }}
              >
                <Radio size={18} /> {autoPilotStatus.enabled ? 'Auto-Pilot ACTIVE (Click to Pause)' : 'Enable Autonomous Auto-Pilot'}
              </button>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '28px' }}>
              {/* Left Column: Auto-Pilot Config */}
              <div className="glass-card" style={{ padding: '28px' }}>
                <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '20px' }}>Auto-Pilot Settings</h2>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Posting Frequency</label>
                    <select className="select-field" value={autoInterval} onChange={(e) => setAutoInterval(e.target.value)}>
                      <option value={15}>Every 15 Minutes (Testing Mode)</option>
                      <option value={60}>Every 1 Hour (High Frequency)</option>
                      <option value={180}>Every 3 Hours</option>
                      <option value={360}>Every 6 Hours</option>
                      <option value={1440}>Once Daily (24 Hours)</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>YouTube Privacy Setting</label>
                    <select className="select-field" value={autoPrivacy} onChange={(e) => setAutoPrivacy(e.target.value)}>
                      <option value="private">Private (Review drafts before publishing)</option>
                      <option value="unlisted">Unlisted</option>
                      <option value="public">Public (Instant Auto-Publish to Channel)</option>
                    </select>
                  </div>

                  <button className="btn-secondary" onClick={handleSaveAutoConfig}>Save Auto-Pilot Schedule</button>
                </div>
              </div>

              {/* Right Column: Auto-Pilot Activity Stream */}
              <div className="glass-card" style={{ padding: '28px' }}>
                <h2 style={{ fontSize: '1.3rem', fontWeight: 700, marginBottom: '20px' }}>Live Activity Feed</h2>

                <div style={{ background: 'rgba(0,0,0,0.3)', padding: '16px', borderRadius: '12px', marginBottom: '20px', border: '1px solid var(--border-color)' }}>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Status: <strong style={{ color: autoPilotStatus.enabled ? '#34d399' : '#fbbf24' }}>{autoPilotStatus.enabled ? 'ACTIVE RUNNING' : 'STANDBY'}</strong></p>
                  <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>Total Automated Videos: <strong>{autoPilotStatus.total_auto_videos || 0}</strong></p>
                  {autoPilotStatus.next_run && (
                    <p style={{ fontSize: '0.85rem', color: '#ff0055', marginTop: '4px' }}>Next Auto-Run Scheduled: <strong>{autoPilotStatus.next_run}</strong></p>
                  )}
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '300px', overflowY: 'auto' }}>
                  {autoPilotStatus.history && autoPilotStatus.history.length > 0 ? (
                    autoPilotStatus.history.map((item, idx) => (
                      <div key={idx} style={{ background: 'rgba(255,255,255,0.03)', padding: '12px', borderRadius: '8px', fontSize: '0.85rem', border: '1px solid var(--border-color)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600 }}>
                          <span>{item.title}</span>
                          <span style={{ color: '#34d399' }}>{item.timestamp}</span>
                        </div>
                        <p style={{ color: 'var(--text-dim)', fontSize: '0.75rem', marginTop: '4px' }}>YouTube: {item.yt_status}</p>
                      </div>
                    ))
                  ) : (
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-dim)', textAlign: 'center', padding: '20px 0' }}>No automated runs recorded yet. Enable Auto-Pilot above!</p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* TAB 4: VIDEO LIBRARY */}
        {activeTab === 'library' && (
          <div>
            <header style={{ marginBottom: '28px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '4px' }}>Video Library</h1>
                <p style={{ color: 'var(--text-muted)' }}>All rendered videos saved in local studio storage.</p>
              </div>
              <button className="btn-secondary" onClick={fetchLibrary}><RefreshCw size={16} /> Refresh</button>
            </header>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '24px' }}>
              {videos.map((vid, idx) => (
                <div key={idx} className="glass-card" style={{ padding: '20px' }}>
                  <video src={`http://127.0.0.1:8000${vid.url}`} controls style={{ width: '100%', height: '200px', objectFit: 'cover', borderRadius: '10px', marginBottom: '16px' }} />
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <span className={vid.is_shorts ? 'badge badge-shorts' : 'badge badge-longform'}>{vid.is_shorts ? 'Shorts 9:16' : '16:9 HD'}</span>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{vid.size_mb} MB</span>
                  </div>

                  <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '16px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{vid.filename}</h3>

                  <div style={{ display: 'flex', gap: '8px' }}>
                    <a href={`http://127.0.0.1:8000${vid.url}`} download className="btn-secondary" style={{ flex: 1, justifyContent: 'center' }}>
                      <Download size={16} /> Save
                    </a>
                    <button className="btn-primary" style={{ flex: 1, justifyContent: 'center' }} onClick={() => { setActiveVideo(vid); setYtUploadData({ ...ytUploadData, title: vid.filename.replace('.mp4', '') }); setActiveTab('youtube'); }}>
                      <Youtube size={16} /> Upload
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 5: YOUTUBE PUBLISHING */}
        {activeTab === 'youtube' && (
          <div>
            <header style={{ marginBottom: '28px' }}>
              <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '4px' }}>YouTube API v3 Publisher</h1>
              <p style={{ color: 'var(--text-muted)' }}>Upload MP4 videos directly to your channel with automated SEO tags & privacy settings.</p>
            </header>

            <div className="glass-card" style={{ padding: '28px', maxWidth: '800px' }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-color)', padding: '16px 20px', borderRadius: '12px', marginBottom: '28px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <Youtube size={28} color="#ff0055" />
                  <div>
                    <h3 style={{ fontSize: '1rem', fontWeight: 600 }}>YouTube Channel Connection</h3>
                    <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      {ytStatus.authenticated ? `Connected to ${ytStatus.channel.title}` : 'Ready for Client Secrets JSON'}
                    </p>
                  </div>
                </div>
                <span className={ytStatus.authenticated ? 'badge badge-success' : 'badge badge-shorts'}>
                  {ytStatus.authenticated ? 'Connected' : 'Credentials Needed'}
                </span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Selected Video File</label>
                  <input type="text" className="input-field" readOnly value={activeVideo ? activeVideo.filename : (renderedResult ? renderedResult.output_path : 'No video selected. Render or select from library.')} />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>YouTube Title</label>
                  <input type="text" className="input-field" value={ytUploadData.title} onChange={(e) => setYtUploadData({ ...ytUploadData, title: e.target.value })} />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Description & Tags</label>
                  <textarea className="textarea-field" rows={4} value={ytUploadData.description} onChange={(e) => setYtUploadData({ ...ytUploadData, description: e.target.value })} />
                </div>

                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Privacy Status</label>
                  <select className="select-field" value={ytUploadData.privacy} onChange={(e) => setYtUploadData({ ...ytUploadData, privacy: e.target.value })}>
                    <option value="private">Private (Recommended for Draft Review)</option>
                    <option value="unlisted">Unlisted</option>
                    <option value="public">Public (Instant Publish)</option>
                  </select>
                </div>

                <button className="btn-primary" style={{ justifyContent: 'center', marginTop: '12px' }} onClick={handleYouTubeUpload} disabled={isUploadingYt}>
                  {isUploadingYt ? <RefreshCw className="animate-spin" size={18} /> : <Upload size={18} />}
                  {isUploadingYt ? 'Publishing to YouTube...' : 'Publish to YouTube Channel'}
                </button>

                {uploadResult && (
                  <div style={{ marginTop: '16px', padding: '16px', borderRadius: '10px', background: uploadResult.success ? 'rgba(16, 185, 129, 0.1)' : 'rgba(255, 0, 85, 0.1)', border: '1px solid var(--border-color)' }}>
                    <p style={{ fontWeight: 600, color: uploadResult.success ? '#34d399' : '#ff0055' }}>
                      {uploadResult.success ? `Video Uploaded Successfully! ID: ${uploadResult.video_id}` : `Upload Status: ${uploadResult.error || 'Simulated Upload complete'}`}
                    </p>
                  </div>
                )}
              </div>

            </div>
          </div>
        )}

        {/* TAB 6: API & CREDENTIALS */}
        {activeTab === 'settings' && (
          <div>
            <header style={{ marginBottom: '28px' }}>
              <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '4px' }}>API Keys & Credentials</h1>
              <p style={{ color: 'var(--text-muted)' }}>Configure API keys for stock media providers & YouTube OAuth client secrets.</p>
            </header>

            <div className="glass-card" style={{ padding: '28px', maxWidth: '750px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>Pexels API Key</label>
                <input type="text" className="input-field" readOnly value="f9pRnqk0T38aFRraTo5NugtO8ow9AJ1u6TBBoBAtqv4yrlv3Sz5g4CyU" />
                <p style={{ fontSize: '0.75rem', color: '#34d399', marginTop: '4px' }}>✓ Pexels API Key Active</p>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>YouTube OAuth Connection</label>
                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
                  <button 
                    className="btn-primary" 
                    onClick={async () => {
                      try {
                        const res = await axios.get(`${API_BASE}/youtube/auth-url`);
                        if (res.data.auth_url) {
                          window.open(res.data.auth_url, '_blank');
                        }
                      } catch (e) {
                        alert(`Auth Error: ${e.response?.data?.detail || e.message}`);
                      }
                    }}
                    style={{ background: 'linear-gradient(135deg, #ff0055, #8b5cf6)', borderColor: '#ff0055' }}
                  >
                    <Youtube size={18} /> Authenticate & Link YouTube Channel
                  </button>

                  <button 
                    className="btn-secondary" 
                    onClick={async () => {
                      try {
                        let secJson = clientSecretsInput;
                        let tokJson = null;
                        const renderRes = await axios.post(`${RENDER_BACKEND}/sync/credentials`, {
                          client_secrets_json: secJson || undefined,
                          youtube_token_json: tokJson || undefined
                        });
                        alert("✓ Render Cloud Engine Synced! 24/7 Auto-Pilot is ready to post when laptop is OFF.");
                      } catch (e) {
                        alert(`Cloud Sync: ${e.response?.data?.detail || e.message}`);
                      }
                    }}
                  >
                    ☁️ Sync Tokens to Render Cloud (24/7 Mode)
                  </button>
                </div>
                <p style={{ fontSize: '0.75rem', color: ytStatus.authenticated ? '#34d399' : '#fbbf24', marginTop: '8px' }}>
                  {ytStatus.authenticated ? `✓ Connected to YouTube Channel: ${ytStatus.channel.title}` : '• client_secrets.json is loaded. Click button to complete Google Login.'}
                </p>
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '8px' }}>YouTube OAuth client_secrets.json (Paste Content)</label>
                <textarea
                  className="textarea-field"
                  rows={6}
                  placeholder="Paste contents of client_secrets.json from Google Cloud Console..."
                  value={clientSecretsInput}
                  onChange={(e) => setClientSecretsInput(e.target.value)}
                />
                <button className="btn-primary" style={{ marginTop: '12px' }} onClick={handleSaveClientSecrets}>
                  Save YouTube Credentials
                </button>
              </div>
            </div>
          </div>
        )}

      </main>
    </div>
  );
}
