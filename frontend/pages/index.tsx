import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { 
  Shield, 
  Eye, 
  Upload, 
  Video, 
  Camera, 
  BarChart3, 
  Download,
  FileText,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  Clock,
  TrendingUp,
  Activity,
  ChevronLeft,
  ChevronRight,
  X,
  Play,
  Pause,
  Image as ImageIcon
} from 'lucide-react';

const API_URL = 'http://localhost:5000';

interface DetectionLog {
  id: string;
  timestamp: string;
  mode: 'ppe' | 'normal';
  type: 'image' | 'video' | 'live';
  filename?: string;
  total_objects: number;
  detections: any[];
  detection_summary?: string;
  object_categories?: any;
  detections_by_category?: any;
  unique_classes?: number;
  object_list?: Array<{
    category: string;
    number: number;
    confidence: number;
    label: string;
  }>;
  // PPE specific
  status?: string;
  compliance_score?: number;
  person_count?: number;
  detected_ppe?: any;
  missing_required?: string[];
  helmet?: number;
  vest?: number;
  boots?: number;
  mask?: number;
  gloves?: number;
  glasses?: number;
  goggles?: number;
  shoes?: number;
  // Normal specific
  class_counts?: any;
}

interface ImageResult {
  file: File;
  result: any;
  preview: string;
}

export default function Home() {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [imageResults, setImageResults] = useState<ImageResult[]>([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [videoFile, setVideoFile] = useState<File | null>(null);
  const [videoResult, setVideoResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [processingIndex, setProcessingIndex] = useState(-1);
  const [analytics, setAnalytics] = useState<any>(null);
  const [detectionLogs, setDetectionLogs] = useState<DetectionLog[]>([]);
  const [activeTab, setActiveTab] = useState('detect');
  const [detectionMode, setDetectionMode] = useState<'ppe' | 'normal'>('ppe');
  const videoRef = useRef<HTMLVideoElement>(null);
  const videoPreviewRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [isLiveDetection, setIsLiveDetection] = useState(false);
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    console.log('🔄 Fetching analytics for mode:', detectionMode);
    try {
      const response = await axios.get(`${API_URL}/analytics?mode=${detectionMode}`);
      console.log('✓ Analytics response:', response.data);
      console.log('✓ Records count:', response.data.records?.length || 0);
      console.log('✓ Summary:', response.data.summary);
      
      setAnalytics(response.data.summary);
      setDetectionLogs(response.data.records || []);
      console.log(`✓ Loaded ${response.data.records?.length || 0} records from DB`);
    } catch (error) {
      console.error('✗ Error fetching analytics:', error);
      if (axios.isAxiosError(error)) {
        console.error('✗ Response:', error.response?.data);
        console.error('✗ Status:', error.response?.status);
      }
    }
  };

  const handleMultipleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      const files = Array.from(e.target.files).slice(0, 15); // Max 15 images
      setSelectedFiles(files);
      setImageResults([]);
      setCurrentImageIndex(0);
    }
  };

  const handleVideoSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setVideoFile(e.target.files[0]);
      setVideoResult(null);
    }
  };

  const processAllImages = async () => {
    if (selectedFiles.length === 0) return;

    setLoading(true);
    const results: ImageResult[] = [];

    for (let i = 0; i < selectedFiles.length; i++) {
      setProcessingIndex(i);
      const file = selectedFiles[i];
      const formData = new FormData();
      formData.append('image', file);
      formData.append('mode', detectionMode);
      formData.append('filename', file.name);  // Send filename to backend

      try {
        const response = await axios.post(`${API_URL}/detect/image`, formData);
        const preview = URL.createObjectURL(file);
        results.push({ file, result: response.data, preview });
        console.log(`✓ Image ${i + 1} saved to DB with ID: ${response.data.record_id}`);
      } catch (error) {
        console.error(`Error processing image ${i + 1}:`, error);
      }
    }

    setImageResults(results);
    setProcessingIndex(-1);
    setLoading(false);
    
    // Refresh analytics after processing
    if (activeTab === 'analytics') {
      fetchAnalytics();
    }
  };

  const processVideo = async () => {
    if (!videoFile) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('video', videoFile);
    formData.append('mode', detectionMode);
    formData.append('filename', videoFile.name);  // Send filename to backend

    try {
      const response = await axios.post(`${API_URL}/detect/video`, formData);
      setVideoResult(response.data);
      console.log(`✓ Video saved to DB with ID: ${response.data.record_id}`);
      
      // Refresh analytics after processing
      if (activeTab === 'analytics') {
        fetchAnalytics();
      }
    } catch (error) {
      console.error('Error processing video:', error);
      alert('Video processing failed');
    }
    setLoading(false);
  };

  const startLiveDetection = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsLiveDetection(true);
        detectFromWebcam();
      }
    } catch (error) {
      console.error('Error accessing webcam:', error);
      alert('Cannot access webcam');
    }
  };

  const stopLiveDetection = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      setIsLiveDetection(false);
    }
  };

  const detectFromWebcam = async () => {
    if (!videoRef.current || !canvasRef.current || !isLiveDetection) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    const ctx = canvas.getContext('2d');

    if (ctx && video.readyState === video.HAVE_ENOUGH_DATA) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0);

      canvas.toBlob(async (blob) => {
        if (blob) {
          const formData = new FormData();
          formData.append('image', blob, 'webcam.jpg');
          formData.append('mode', detectionMode);

          try {
            const response = await axios.post(`${API_URL}/detect/image`, formData);
            setImageResults([{ 
              file: new File([blob], 'webcam.jpg'), 
              result: response.data, 
              preview: URL.createObjectURL(blob) 
            }]);
            // Detection already saved to DB by backend
          } catch (error) {
            console.error('Error:', error);
          }
        }
      });
    }

    setTimeout(detectFromWebcam, 1000);
  };

  const exportLogCSV = async (recordId: string) => {
    try {
      const response = await axios.get(`${API_URL}/export/csv/${recordId}`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `detection_${recordId}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      console.log(`✓ CSV exported for record ${recordId}`);
    } catch (error) {
      console.error('CSV export error:', error);
      alert('Failed to export CSV');
    }
  };

  const exportLogPDF = async (recordId: string) => {
    try {
      const response = await axios.get(`${API_URL}/export/pdf/${recordId}`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `detection_${recordId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      console.log(`✓ PDF exported for record ${recordId}`);
    } catch (error) {
      console.error('PDF export error:', error);
      alert('Failed to export PDF');
    }
  };

  const nextImage = () => {
    if (currentImageIndex < imageResults.length - 1) {
      setCurrentImageIndex(currentImageIndex + 1);
    }
  };

  const prevImage = () => {
    if (currentImageIndex > 0) {
      setCurrentImageIndex(currentImageIndex - 1);
    }
  };

  const removeImage = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    const newResults = imageResults.filter((_, i) => i !== index);
    setSelectedFiles(newFiles);
    setImageResults(newResults);
    if (currentImageIndex >= newResults.length && currentImageIndex > 0) {
      setCurrentImageIndex(currentImageIndex - 1);
    }
  };

  const toggleVideoPlayback = () => {
    if (videoPreviewRef.current) {
      if (isVideoPlaying) {
        videoPreviewRef.current.pause();
      } else {
        videoPreviewRef.current.play();
      }
      setIsVideoPlaying(!isVideoPlaying);
    }
  };

  const currentResult = imageResults[currentImageIndex];


  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white">
      {/* Elegant Navigation Bar */}
      <nav className="backdrop-blur-xl bg-slate-900/50 border-b border-slate-800/50 sticky top-0 z-50">
        <div className="container mx-auto px-8 py-5">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="p-2 bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl">
                <Activity className="w-7 h-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-light tracking-wider">Detection System</h1>
                <p className="text-xs text-slate-400">Professional AI Analysis</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setDetectionMode('ppe')}
                className={`group flex items-center space-x-2 px-6 py-3 rounded-xl font-medium transition-all duration-300 ${
                  detectionMode === 'ppe'
                    ? 'bg-white text-slate-900 shadow-xl shadow-white/20'
                    : 'bg-slate-800/50 text-slate-300 hover:bg-slate-800 border border-slate-700/50'
                }`}
              >
                <Shield className="w-4 h-4" />
                <span>PPE Detection</span>
              </button>
              <button
                onClick={() => setDetectionMode('normal')}
                className={`group flex items-center space-x-2 px-6 py-3 rounded-xl font-medium transition-all duration-300 ${
                  detectionMode === 'normal'
                    ? 'bg-white text-slate-900 shadow-xl shadow-white/20'
                    : 'bg-slate-800/50 text-slate-300 hover:bg-slate-800 border border-slate-700/50'
                }`}
              >
                <Eye className="w-4 h-4" />
                <span>Normal Detection</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Tab Navigation */}
      <div className="backdrop-blur-xl bg-slate-900/30 border-b border-slate-800/50">
        <div className="container mx-auto px-8">
          <div className="flex space-x-1">
            <button
              onClick={() => setActiveTab('detect')}
              className={`flex items-center space-x-2 px-8 py-4 font-medium transition-all duration-300 relative ${
                activeTab === 'detect'
                  ? 'text-white'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Camera className="w-4 h-4" />
              <span>Detection</span>
              {activeTab === 'detect' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-white to-transparent"></div>
              )}
            </button>
            <button
              onClick={() => { setActiveTab('analytics'); fetchAnalytics(); }}
              className={`flex items-center space-x-2 px-8 py-4 font-medium transition-all duration-300 relative ${
                activeTab === 'analytics'
                  ? 'text-white'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Analytics</span>
              {activeTab === 'analytics' && (
                <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-transparent via-white to-transparent"></div>
              )}
            </button>
          </div>
        </div>
      </div>

      <div className="container mx-auto px-8 py-10">
        {activeTab === 'detect' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Upload Section */}
            <div className="space-y-6">
              {/* Multiple Images Upload */}
              <div className="backdrop-blur-xl bg-slate-900/50 border border-slate-800/50 rounded-2xl p-8 shadow-2xl">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="p-2 bg-slate-800/50 rounded-lg">
                    <ImageIcon className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-xl font-light">Multiple Images</h2>
                    <p className="text-xs text-slate-400">Upload up to 15 images</p>
                  </div>
                </div>
                
                <div className="bg-slate-800/30 border border-slate-700/50 rounded-xl p-4 mb-6">
                  <p className="text-sm text-slate-300">
                    {detectionMode === 'ppe' 
                      ? '🛡️ Detects: Mask, Vest, Glasses, Goggles, Boots, Shoes, Helmet, Gloves'
                      : '👁️ Detects: All common objects (80 classes)'}
                  </p>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-3">
                      Select Images (Max 15)
                    </label>
                    <input
                      type="file"
                      accept="image/*"
                      multiple
                      onChange={handleMultipleFileSelect}
                      className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-white file:text-slate-900 file:font-medium hover:file:bg-slate-100 cursor-pointer transition-all"
                    />
                    {selectedFiles.length > 0 && (
                      <p className="text-sm text-slate-400 mt-2">
                        {selectedFiles.length} image{selectedFiles.length > 1 ? 's' : ''} selected
                      </p>
                    )}
                  </div>

                  <button
                    onClick={processAllImages}
                    disabled={selectedFiles.length === 0 || loading}
                    className="w-full flex items-center justify-center space-x-2 px-6 py-4 bg-white text-slate-900 rounded-xl font-semibold hover:bg-slate-100 disabled:bg-slate-700 disabled:text-slate-500 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-slate-900"></div>
                        <span>Processing {processingIndex + 1}/{selectedFiles.length}...</span>
                      </>
                    ) : (
                      <>
                        <Upload className="w-5 h-5" />
                        <span>Detect All Images</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Video Upload */}
              <div className="backdrop-blur-xl bg-slate-900/50 border border-slate-800/50 rounded-2xl p-8 shadow-2xl">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="p-2 bg-slate-800/50 rounded-lg">
                    <Video className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-xl font-light">Video Detection</h2>
                    <p className="text-xs text-slate-400">Upload a video file</p>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-3">
                      Select Video
                    </label>
                    <input
                      type="file"
                      accept="video/*"
                      onChange={handleVideoSelect}
                      className="w-full px-4 py-3 bg-slate-800/50 border border-slate-700/50 rounded-xl text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-white file:text-slate-900 file:font-medium hover:file:bg-slate-100 cursor-pointer transition-all"
                    />
                  </div>

                  {videoFile && (
                    <div className="bg-slate-800/30 rounded-xl p-4">
                      <video
                        ref={videoPreviewRef}
                        src={URL.createObjectURL(videoFile)}
                        className="w-full rounded-lg mb-3"
                        controls={false}
                      />
                      <button
                        onClick={toggleVideoPlayback}
                        className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-slate-700/50 hover:bg-slate-700 rounded-lg transition-all"
                      >
                        {isVideoPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                        <span>{isVideoPlaying ? 'Pause' : 'Play'} Preview</span>
                      </button>
                    </div>
                  )}

                  <button
                    onClick={processVideo}
                    disabled={!videoFile || loading}
                    className="w-full flex items-center justify-center space-x-2 px-6 py-4 bg-white text-slate-900 rounded-xl font-semibold hover:bg-slate-100 disabled:bg-slate-700 disabled:text-slate-500 disabled:cursor-not-allowed transition-all duration-300 shadow-lg hover:shadow-xl"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-slate-900"></div>
                        <span>Processing Video...</span>
                      </>
                    ) : (
                      <>
                        <Video className="w-5 h-5" />
                        <span>Detect Video</span>
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Live Camera */}
              <div className="backdrop-blur-xl bg-slate-900/50 border border-slate-800/50 rounded-2xl p-8 shadow-2xl">
                <div className="flex items-center space-x-3 mb-6">
                  <div className="p-2 bg-slate-800/50 rounded-lg">
                    <Camera className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h2 className="text-xl font-light">Live Camera</h2>
                    <p className="text-xs text-slate-400">Real-time detection</p>
                  </div>
                </div>

                <button
                  onClick={isLiveDetection ? stopLiveDetection : startLiveDetection}
                  className={`w-full flex items-center justify-center space-x-2 px-6 py-4 rounded-xl font-semibold transition-all duration-300 shadow-lg ${
                    isLiveDetection
                      ? 'bg-red-600 hover:bg-red-700 text-white'
                      : 'bg-slate-800/50 hover:bg-slate-800 text-white border border-slate-700/50'
                  }`}
                >
                  <Camera className="w-5 h-5" />
                  <span>{isLiveDetection ? 'Stop Live Detection' : 'Start Live Detection'}</span>
                </button>
                <video ref={videoRef} autoPlay className="mt-4 w-full rounded-xl hidden" />
                <canvas ref={canvasRef} className="hidden" />
              </div>
            </div>

            {/* Results Section */}
            <div className="backdrop-blur-xl bg-slate-900/50 border border-slate-800/50 rounded-2xl p-8 shadow-2xl">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-2 bg-slate-800/50 rounded-lg">
                  <Activity className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h2 className="text-xl font-light">Detection Results</h2>
                  <p className="text-xs text-slate-400">Analysis output</p>
                </div>
              </div>

              
              {loading && (
                <div className="flex flex-col items-center justify-center py-20">
                  <div className="relative">
                    <div className="animate-spin rounded-full h-20 w-20 border-b-2 border-white"></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <Activity className="w-8 h-8 text-white animate-pulse" />
                    </div>
                  </div>
                  <p className="text-slate-400 mt-6">Processing detection...</p>
                  {processingIndex >= 0 && (
                    <p className="text-sm text-slate-500 mt-2">
                      Image {processingIndex + 1} of {selectedFiles.length}
                    </p>
                  )}
                </div>
              )}
              
              {!loading && imageResults.length === 0 && !videoResult && (
                <div className="flex flex-col items-center justify-center py-20 text-slate-500">
                  <div className="p-6 bg-slate-800/30 rounded-2xl mb-4">
                    <ImageIcon className="w-16 h-16" />
                  </div>
                  <p className="text-lg">No detection results yet</p>
                  <p className="text-sm mt-2 text-slate-600">Upload images, video, or start live detection</p>
                </div>
              )}
              
              {/* Image Results Carousel */}
              {imageResults.length > 0 && (
                <div className="space-y-6">
                  {/* Image Navigation */}
                  <div className="flex items-center justify-between bg-slate-800/30 rounded-xl p-4">
                    <button
                      onClick={prevImage}
                      disabled={currentImageIndex === 0}
                      className="p-2 bg-slate-700/50 hover:bg-slate-700 rounded-lg disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                    >
                      <ChevronLeft className="w-5 h-5" />
                    </button>
                    
                    <div className="text-center">
                      <p className="text-sm text-slate-400">
                        Image {currentImageIndex + 1} of {imageResults.length}
                      </p>
                      <p className="text-xs text-slate-500 mt-1">
                        {currentResult?.file.name}
                      </p>
                    </div>
                    
                    <button
                      onClick={nextImage}
                      disabled={currentImageIndex === imageResults.length - 1}
                      className="p-2 bg-slate-700/50 hover:bg-slate-700 rounded-lg disabled:opacity-30 disabled:cursor-not-allowed transition-all"
                    >
                      <ChevronRight className="w-5 h-5" />
                    </button>
                  </div>

                  {/* Thumbnail Strip */}
                  <div className="flex space-x-2 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-slate-700 scrollbar-track-slate-800/30">
                    {imageResults.map((result, index) => (
                      <div
                        key={index}
                        className={`relative flex-shrink-0 cursor-pointer transition-all duration-300 ${
                          index === currentImageIndex
                            ? 'ring-2 ring-white rounded-lg scale-105'
                            : 'opacity-50 hover:opacity-100'
                        }`}
                        onClick={() => setCurrentImageIndex(index)}
                      >
                        <img
                          src={result.preview}
                          alt={`Thumbnail ${index + 1}`}
                          className="w-20 h-20 object-cover rounded-lg"
                        />
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            removeImage(index);
                          }}
                          className="absolute -top-2 -right-2 p-1 bg-red-600 hover:bg-red-700 rounded-full transition-all"
                        >
                          <X className="w-3 h-3" />
                        </button>
                      </div>
                    ))}
                  </div>

                  {/* Current Image Result */}
                  {currentResult && (
                    <div className="space-y-6 animate-fadeIn">
                      <img
                        src={`data:image/jpeg;base64,${currentResult.result.image}`}
                        alt="Detection result"
                        className="w-full rounded-xl border border-slate-700/50 shadow-2xl"
                      />
                      
                      {currentResult.result.mode === 'ppe' && currentResult.result.compliance && (
                        <div>
                          <div className={`p-6 rounded-xl border-2 transition-all duration-300 ${
                            currentResult.result.compliance.is_safe 
                              ? 'bg-emerald-900/20 border-emerald-500/50 shadow-emerald-500/20' 
                              : 'bg-red-900/20 border-red-500/50 shadow-red-500/20'
                          } shadow-xl`}>
                            <div className="flex items-center space-x-3 mb-4">
                              {currentResult.result.compliance.is_safe ? (
                                <CheckCircle2 className="w-8 h-8 text-emerald-400" />
                              ) : (
                                <XCircle className="w-8 h-8 text-red-400" />
                              )}
                              <h3 className="text-2xl font-light">
                                {currentResult.result.compliance.is_safe ? 'SAFE' : 'NOT SAFE'}
                              </h3>
                            </div>
                            <p className="text-slate-300 mb-4">{currentResult.result.compliance.status_message}</p>
                            <div className="grid grid-cols-2 gap-4">
                              <div className="bg-slate-900/50 rounded-xl p-4">
                                <p className="text-sm text-slate-400">Compliance Score</p>
                                <p className="text-3xl font-light mt-1">{currentResult.result.compliance.compliance_score}%</p>
                              </div>
                              <div className="bg-slate-900/50 rounded-xl p-4">
                                <p className="text-sm text-slate-400">Persons Detected</p>
                                <p className="text-3xl font-light mt-1">{currentResult.result.compliance.person_count}</p>
                              </div>
                            </div>
                          </div>

                          <div className="bg-slate-800/30 rounded-xl p-6">
                            <h4 className="font-medium text-emerald-400 mb-4 flex items-center space-x-2">
                              <CheckCircle2 className="w-5 h-5" />
                              <span>Detected PPE Items</span>
                            </h4>
                            {Object.keys(currentResult.result.compliance.detected_ppe).length > 0 ? (
                              <div className="space-y-2">
                                {Object.entries(currentResult.result.compliance.detected_ppe).map(([item, count]: [string, any], i) => (
                                  <div key={i} className="flex justify-between items-center bg-slate-900/50 rounded-lg px-4 py-3 transition-all hover:bg-slate-900/70">
                                    <span className="text-emerald-400">{item}</span>
                                    <span className="font-medium">{count} {count > 1 ? 'items' : 'item'}</span>
                                  </div>
                                ))}
                              </div>
                            ) : (
                              <p className="text-slate-500 italic">No PPE items detected</p>
                            )}
                          </div>

                          {currentResult.result.compliance.missing_required?.length > 0 && (
                            <div className="bg-slate-800/30 rounded-xl p-6">
                              <h4 className="font-medium text-red-400 mb-4 flex items-center space-x-2">
                                <AlertTriangle className="w-5 h-5" />
                                <span>Missing Required PPE</span>
                              </h4>
                              <div className="space-y-2">
                                {currentResult.result.compliance.missing_required.map((item: string, i: number) => (
                                  <div key={i} className="flex items-center space-x-2 bg-slate-900/50 rounded-lg px-4 py-3">
                                    <XCircle className="w-4 h-4 text-red-400" />
                                    <span className="text-red-400">{item}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      )}

                      {currentResult.result.mode === 'normal' && currentResult.result.statistics && (
                        <div>
                          <div className="bg-slate-800/30 rounded-xl p-6 mb-6">
                            <h3 className="text-xl font-light mb-4">Detection Summary</h3>
                            <div className="grid grid-cols-2 gap-4">
                              <div className="bg-slate-900/50 rounded-xl p-4">
                                <p className="text-sm text-slate-400">Total Objects</p>
                                <p className="text-3xl font-light mt-1">{currentResult.result.statistics.total_detections}</p>
                              </div>
                              <div className="bg-slate-900/50 rounded-xl p-4">
                                <p className="text-sm text-slate-400">Unique Classes</p>
                                <p className="text-3xl font-light mt-1">{currentResult.result.statistics.unique_classes}</p>
                              </div>
                            </div>
                          </div>

                          <div className="bg-slate-800/30 rounded-xl p-6">
                            <h4 className="font-medium mb-4">Detected Objects</h4>
                            <div className="space-y-2">
                              {Object.entries(currentResult.result.statistics.class_counts).map(([cls, count]: [string, any], i) => (
                                <div key={i} className="flex justify-between items-center bg-slate-900/50 rounded-lg px-4 py-3 transition-all hover:bg-slate-900/70">
                                  <span>{cls}</span>
                                  <span className="font-medium">{count} {count > 1 ? 'items' : 'item'}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}

              {/* Video Result */}
              {videoResult && (
                <div className="space-y-6 animate-fadeIn">
                  <img
                    src={`data:image/jpeg;base64,${videoResult.image}`}
                    alt="Video detection result"
                    className="w-full rounded-xl border border-slate-700/50 shadow-2xl"
                  />
                  {/* Similar result display as images */}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="space-y-8">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-slate-800/50 rounded-lg">
                  <BarChart3 className="w-6 h-6 text-white" />
                </div>
                <div>
                  <h2 className="text-3xl font-light">Detection Analytics</h2>
                  <p className="text-sm text-slate-400">Complete detection history from database</p>
                </div>
              </div>
              <button
                onClick={fetchAnalytics}
                className="px-4 py-2 bg-blue-600/20 hover:bg-blue-600/30 border border-blue-500/50 rounded-xl font-medium transition-all flex items-center space-x-2"
              >
                <Activity className="w-4 h-4" />
                <span>Refresh from DB</span>
              </button>
            </div>

            {/* Statistics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              {[
                { icon: Clock, label: 'Total Detections', value: detectionLogs.length, color: 'blue' },
                { icon: Camera, label: 'Image Detections', value: detectionLogs.filter(l => l.type === 'image').length, color: 'green' },
                { icon: Video, label: 'Live Detections', value: detectionLogs.filter(l => l.type === 'live').length, color: 'purple' },
                { icon: TrendingUp, label: 'PPE Detections', value: detectionLogs.filter(l => l.mode === 'ppe').length, color: 'yellow' }
              ].map((stat, i) => (
                <div key={i} className="backdrop-blur-xl bg-slate-900/50 border border-slate-800/50 rounded-2xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300">
                  <stat.icon className={`w-8 h-8 text-${stat.color}-400 mb-3`} />
                  <p className="text-sm text-slate-400">{stat.label}</p>
                  <p className="text-4xl font-light mt-2">{stat.value}</p>
                </div>
              ))}
            </div>

            {/* Detection Logs Table */}
            <div className="backdrop-blur-xl bg-slate-900/50 border border-slate-800/50 rounded-2xl overflow-hidden shadow-2xl">
              <div className="p-6 border-b border-slate-800/50">
                <h3 className="text-xl font-light">Detection History (From Database)</h3>
                <p className="text-sm text-slate-400 mt-1">All detections saved in MongoDB - Click row to expand details</p>
              </div>
              
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead className="bg-slate-900/70">
                    <tr>
                      {detectionMode === 'ppe' ? (
                        <>
                          <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Timestamp</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Filename</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Type</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Status</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Score</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Persons</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Objects</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">PPE Items</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Export</th>
                        </>
                      ) : (
                        <>
                          <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Timestamp</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Filename</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Type</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Objects</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Classes</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Top Detections</th>
                          <th className="px-6 py-4 text-left text-xs font-medium text-slate-400 uppercase">Export</th>
                        </>
                      )}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/50">
                    {detectionLogs.length === 0 ? (
                      <tr>
                        <td colSpan={detectionMode === 'ppe' ? 9 : 7} className="px-6 py-12 text-center text-slate-500">
                          <ImageIcon className="w-12 h-12 mx-auto mb-3 opacity-50" />
                          <p>No detection logs in database</p>
                          <p className="text-sm mt-1">Start detecting to see logs here</p>
                        </td>
                      </tr>
                    ) : (
                      detectionLogs.map((log) => (
                        <>
                          <tr 
                            key={log.id} 
                            className="hover:bg-slate-800/30 transition-all duration-200 cursor-pointer"
                            onClick={() => setExpandedRow(expandedRow === log.id ? null : log.id)}
                          >
                            {detectionMode === 'ppe' ? (
                              <>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="flex items-center space-x-2">
                                    <Clock className="w-4 h-4 text-slate-400" />
                                    <span className="text-sm">
                                      {new Date(log.timestamp).toLocaleString()}
                                    </span>
                                  </div>
                                </td>
                                <td className="px-6 py-4">
                                  <span className="text-sm text-slate-300">{log.filename || 'N/A'}</span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-slate-700/50 text-slate-300 border border-slate-600/50">
                                    {log.type === 'image' && <Camera className="w-3 h-3 mr-1" />}
                                    {log.type === 'video' && <Video className="w-3 h-3 mr-1" />}
                                    {log.type === 'live' && <Activity className="w-3 h-3 mr-1" />}
                                    {log.type.toUpperCase()}
                                  </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                                    log.status === 'SAFE'
                                      ? 'bg-emerald-900/30 text-emerald-300 border border-emerald-500/30' 
                                      : 'bg-red-900/30 text-red-300 border border-red-500/30'
                                  }`}>
                                    {log.status === 'SAFE' ? (
                                      <CheckCircle2 className="w-3 h-3 mr-1" />
                                    ) : (
                                      <XCircle className="w-3 h-3 mr-1" />
                                    )}
                                    {log.status}
                                  </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className="font-medium">{log.compliance_score}%</span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className="font-medium">{log.person_count}</span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className="font-medium">{log.total_objects}</span>
                                </td>
                                <td className="px-6 py-4">
                                  <div className="text-xs text-slate-400">
                                    {log.detected_ppe && Object.keys(log.detected_ppe).length > 0 ? (
                                      <span>{Object.entries(log.detected_ppe).map(([k, v]) => `${k}:${v}`).join(', ')}</span>
                                    ) : (
                                      <span className="text-slate-600">None</span>
                                    )}
                                  </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="flex items-center space-x-2">
                                    <button
                                      onClick={(e) => { e.stopPropagation(); exportLogCSV(log.id); }}
                                      className="p-2 bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/50 rounded-lg transition-all"
                                      title="Export as CSV"
                                    >
                                      <FileText className="w-4 h-4 text-emerald-400" />
                                    </button>
                                    <button
                                      onClick={(e) => { e.stopPropagation(); exportLogPDF(log.id); }}
                                      className="p-2 bg-red-600/20 hover:bg-red-600/30 border border-red-500/50 rounded-lg transition-all"
                                      title="Export as PDF"
                                    >
                                      <Download className="w-4 h-4 text-red-400" />
                                    </button>
                                  </div>
                                </td>
                              </>
                            ) : (
                              <>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="flex items-center space-x-2">
                                    <Clock className="w-4 h-4 text-slate-400" />
                                    <span className="text-sm">
                                      {new Date(log.timestamp).toLocaleString()}
                                    </span>
                                  </div>
                                </td>
                                <td className="px-6 py-4">
                                  <span className="text-sm text-slate-300">{log.filename || 'N/A'}</span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-slate-700/50 text-slate-300 border border-slate-600/50">
                                    {log.type === 'image' && <Camera className="w-3 h-3 mr-1" />}
                                    {log.type === 'video' && <Video className="w-3 h-3 mr-1" />}
                                    {log.type.toUpperCase()}
                                  </span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className="font-medium">{log.total_objects}</span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className="font-medium">{log.unique_classes}</span>
                                </td>
                                <td className="px-6 py-4">
                                  <div className="text-xs text-slate-400">
                                    {log.class_counts && Object.keys(log.class_counts).length > 0 ? (
                                      <span>{Object.entries(log.class_counts).slice(0, 3).map(([k, v]) => `${k}:${v}`).join(', ')}</span>
                                    ) : (
                                      <span className="text-slate-600">None</span>
                                    )}
                                  </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="flex items-center space-x-2">
                                    <button
                                      onClick={(e) => { e.stopPropagation(); exportLogCSV(log.id); }}
                                      className="p-2 bg-emerald-600/20 hover:bg-emerald-600/30 border border-emerald-500/50 rounded-lg transition-all"
                                      title="Export as CSV"
                                    >
                                      <FileText className="w-4 h-4 text-emerald-400" />
                                    </button>
                                    <button
                                      onClick={(e) => { e.stopPropagation(); exportLogPDF(log.id); }}
                                      className="p-2 bg-red-600/20 hover:bg-red-600/30 border border-red-500/50 rounded-lg transition-all"
                                      title="Export as PDF"
                                    >
                                      <Download className="w-4 h-4 text-red-400" />
                                    </button>
                                  </div>
                                </td>
                              </>
                            )}
                          </tr>
                          {/* Expanded Row Details */}
                          {expandedRow === log.id && (
                            <tr className="bg-slate-800/50">
                              <td colSpan={detectionMode === 'ppe' ? 9 : 7} className="px-6 py-6">
                                <div className="space-y-4">
                                  <h4 className="font-medium text-white mb-3">Complete Detection Details</h4>
                                  
                                  {detectionMode === 'ppe' && (
                                    <div className="grid grid-cols-4 gap-4 mb-4">
                                      <div className="bg-slate-900/50 rounded-lg p-3">
                                        <p className="text-xs text-slate-400">Helmet</p>
                                        <p className="text-lg font-medium">{log.helmet || 0}</p>
                                      </div>
                                      <div className="bg-slate-900/50 rounded-lg p-3">
                                        <p className="text-xs text-slate-400">Vest</p>
                                        <p className="text-lg font-medium">{log.vest || 0}</p>
                                      </div>
                                      <div className="bg-slate-900/50 rounded-lg p-3">
                                        <p className="text-xs text-slate-400">Boots</p>
                                        <p className="text-lg font-medium">{log.boots || 0}</p>
                                      </div>
                                      <div className="bg-slate-900/50 rounded-lg p-3">
                                        <p className="text-xs text-slate-400">Mask</p>
                                        <p className="text-lg font-medium">{log.mask || 0}</p>
                                      </div>
                                      <div className="bg-slate-900/50 rounded-lg p-3">
                                        <p className="text-xs text-slate-400">Gloves</p>
                                        <p className="text-lg font-medium">{log.gloves || 0}</p>
                                      </div>
                                      <div className="bg-slate-900/50 rounded-lg p-3">
                                        <p className="text-xs text-slate-400">Glasses</p>
                                        <p className="text-lg font-medium">{log.glasses || 0}</p>
                                      </div>
                                      <div className="bg-slate-900/50 rounded-lg p-3">
                                        <p className="text-xs text-slate-400">Goggles</p>
                                        <p className="text-lg font-medium">{log.goggles || 0}</p>
                                      </div>
                                      <div className="bg-slate-900/50 rounded-lg p-3">
                                        <p className="text-xs text-slate-400">Shoes</p>
                                        <p className="text-lg font-medium">{log.shoes || 0}</p>
                                      </div>
                                    </div>
                                  )}
                                  
                                  {log.missing_required && log.missing_required.length > 0 && (
                                    <div className="bg-red-900/20 border border-red-500/30 rounded-lg p-4">
                                      <p className="text-sm font-medium text-red-400 mb-2">Missing Required PPE:</p>
                                      <p className="text-sm text-red-300">{log.missing_required.join(', ')}</p>
                                    </div>
                                  )}
                                  
                                  <div className="bg-slate-900/50 rounded-lg p-4">
                                    <p className="text-sm font-medium text-slate-300 mb-3">All Detections ({log.detections.length}):</p>
                                    <div className="max-h-60 overflow-y-auto space-y-2">
                                      {log.object_list && log.object_list.length > 0 ? (
                                        <div className="grid grid-cols-2 gap-2">
                                          {log.object_list.map((obj: any, i: number) => (
                                            <div key={i} className="bg-slate-800/50 rounded px-3 py-2 flex justify-between items-center">
                                              <span className="text-sm font-medium text-white">{obj.label}</span>
                                              <span className="text-xs text-slate-400">{(obj.confidence * 100).toFixed(0)}%</span>
                                            </div>
                                          ))}
                                        </div>
                                      ) : (
                                        log.detections.map((det: any, i: number) => (
                                          <div key={i} className="text-xs text-slate-400 flex justify-between bg-slate-800/30 rounded px-3 py-2">
                                            <span className="font-medium text-slate-300">{det.class}</span>
                                            <span>Confidence: {(det.confidence * 100).toFixed(0)}%</span>
                                          </div>
                                        ))
                                      )}
                                    </div>
                                  </div>
                                  
                                  {log.object_categories && Object.keys(log.object_categories).length > 0 && (
                                    <div className="bg-slate-900/50 rounded-lg p-4">
                                      <p className="text-sm font-medium text-slate-300 mb-3">Category Summary:</p>
                                      <div className="grid grid-cols-3 gap-2">
                                        {Object.entries(log.object_categories).map(([cat, count]: [string, any], i) => (
                                          <div key={i} className="bg-slate-800/50 rounded px-3 py-2 text-center">
                                            <p className="text-xs text-slate-400">{cat}</p>
                                            <p className="text-lg font-medium text-white">{count}</p>
                                          </div>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </td>
                            </tr>
                          )}
                        </>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
        .scrollbar-thin::-webkit-scrollbar {
          height: 6px;
        }
        .scrollbar-thumb-slate-700::-webkit-scrollbar-thumb {
          background-color: rgb(51 65 85);
          border-radius: 3px;
        }
        .scrollbar-track-slate-800\/30::-webkit-scrollbar-track {
          background-color: rgba(30 41 59 / 0.3);
        }
      `}</style>
    </div>
  );
}
