'use client';

import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import Sidebar from '@/components/Sidebar';
import PhotoLibraryGrid from '@/components/PhotoLibraryGrid';
import MemoryGuidePanel from '@/components/MemoryGuidePanel';
import ResearchUploadView from '@/components/ResearchUploadView';
import ResearchDebugTrace from '@/components/ResearchDebugTrace';

import {
  createSession,
  uploadPhotos,
  submitQuery,
  submitAnswer,
  selectCandidate,
  submitFeedback,
  QuestionData,
  ProgressData,
  CandidateData,
  FoundSummary,
  SelectionMetadata,
} from '@/lib/api';

type PanelStep = 'memory_input' | 'question' | 'recognition' | 'found';

export default function HomePage() {
  const [activeTab, setActiveTab] = useState<'photos' | 'memories' | 'search' | 'collections'>('photos');
  const [isGuideActive, setIsGuideActive] = useState<boolean>(false);
  const [panelStep, setPanelStep] = useState<PanelStep>('memory_input');

  const [mode, setMode] = useState<'demo' | 'research'>('demo');
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Search input state
  const [searchQuery, setSearchQuery] = useState('');

  // Loading & Error States
  const [loading, setLoading] = useState(false);

  // Upload modal state
  const [showResearchUpload, setShowResearchUpload] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'ready' | 'error'>('idle');
  const [uploadedCount, setUploadedCount] = useState<number>(0);
  const [uploadErrorMessage, setUploadErrorMessage] = useState<string | undefined>(undefined);

  // Active Retrieval Session State
  const [currentQuestion, setCurrentQuestion] = useState<QuestionData | undefined>(undefined);
  const [candidates, setCandidates] = useState<CandidateData[]>([]);
  const [progress, setProgress] = useState<ProgressData | undefined>(undefined);
  const [selectionMetadata, setSelectionMetadata] = useState<SelectionMetadata | undefined>(undefined);
  const [foundSummary, setFoundSummary] = useState<FoundSummary | undefined>(undefined);
  const [selectedImageId, setSelectedImageId] = useState<string | undefined>(undefined);

  // Narrowing history trace (e.g., [29, 12, 7])
  const [narrowingHistory, setNarrowingHistory] = useState<number[]>([]);
  const [confirmedClues, setConfirmedClues] = useState<string[]>([]);
  const [referenceBanner, setReferenceBanner] = useState<string | null>(null);

  // Debug Trace Toggle
  const [showDebug, setShowDebug] = useState<boolean>(false);

  // Initialize session on mount
  useEffect(() => {
    async function initSession() {
      try {
        const res = await createSession('demo');
        if (res.success && res.data) {
          setSessionId(res.data.sessionId);
        }
      } catch (e) {
        console.warn('Session init warning:', e);
      }
    }
    initSession();
  }, []);

  const resetAll = () => {
    setIsGuideActive(false);
    setPanelStep('memory_input');
    setSearchQuery('');
    setLoading(false);
    setUploadStatus('idle');
    setUploadedCount(0);
    setCurrentQuestion(undefined);
    setCandidates([]);
    setProgress(undefined);
    setSelectionMetadata(undefined);
    setFoundSummary(undefined);
    setSelectedImageId(undefined);
    setNarrowingHistory([]);
    setConfirmedClues([]);
    setReferenceBanner(null);
  };

  const handleActivateMemoryGuide = (initialQuery?: string) => {
    setIsGuideActive(true);
    if (initialQuery) {
      setSearchQuery(initialQuery);
      handleSubmitQuery(initialQuery);
    }
  };

  // Upload Research Photos
  const handleUploadPhotos = async (files: File[]) => {
    setUploadErrorMessage(undefined);
    let currSessionId = sessionId;
    if (!currSessionId || mode === 'demo') {
      const sessRes = await createSession('research');
      if (sessRes.data) {
        currSessionId = sessRes.data.sessionId;
        setSessionId(currSessionId);
        setMode('research');
      } else if (sessRes.error) {
        setUploadErrorMessage(sessRes.error.message);
        setUploadStatus('error');
        return;
      }
    }
    if (!currSessionId) {
      setUploadErrorMessage("Could not initialize research session. Please check connection.");
      setUploadStatus('error');
      return;
    }

    setLoading(true);
    setUploadStatus('uploading');
    try {
      const res = await uploadPhotos(currSessionId, files);
      if (res.success && res.data) {
        setUploadedCount(res.data.imageCount || files.length);
        setUploadStatus('ready');
        setMode('research');
      } else if (res.error) {
        setUploadErrorMessage(res.error.message);
        setUploadStatus('error');
      }
    } catch (err: any) {
      setUploadErrorMessage(err.message || "Failed to upload photos.");
      setUploadStatus('error');
    } finally {
      setLoading(false);
    }
  };

  // Submit Initial Vague Memory Query
  const handleSubmitQuery = async (query: string) => {
    let currSessionId = sessionId;
    if (!currSessionId) {
      const sessRes = await createSession(mode);
      if (sessRes.data) {
        currSessionId = sessRes.data.sessionId;
        setSessionId(currSessionId);
      }
    }
    if (!currSessionId) return;

    // Reset previous search state completely
    setConfirmedClues([]);
    setCandidates([]);
    setNarrowingHistory([]);
    setReferenceBanner(null);
    setFoundSummary(undefined);
    setSelectedImageId(undefined);

    // Derive initial clues strictly from current query terms
    const initialClues: string[] = [];
    const lowerQ = query.toLowerCase();
    if (lowerQ.includes('beach')) initialClues.push('Beach');
    if (lowerQ.includes('vacation')) initialClues.push('Vacation');
    if (lowerQ.includes('people')) initialClues.push('People');
    if (lowerQ.includes('birthday')) initialClues.push('Birthday');
    if (lowerQ.includes('festival')) initialClues.push('Festival');
    if (lowerQ.includes('traditional')) initialClues.push('Traditional');
    if (lowerQ.includes('park') || lowerQ.includes('picnic')) initialClues.push('Park');
    setConfirmedClues(initialClues);

    setLoading(true);
    try {
      const res = await submitQuery(currSessionId, query, mode);
      if (res.success && res.data) {
        const stepData = res.data;
        const startCount = mode === 'research' ? uploadedCount : 29;
        if (stepData.progress) {
          setProgress(stepData.progress);
          setNarrowingHistory([startCount, stepData.progress.activeCandidates]);
        } else {
          setNarrowingHistory([startCount, Math.min(12, startCount)]);
        }
        if (stepData.selectionMetadata) {
          setSelectionMetadata(stepData.selectionMetadata);
        }

        if (stepData.action === 'ask_question' && stepData.question) {
          setCurrentQuestion(stepData.question);
          setPanelStep('question');
        } else if (stepData.action === 'show_candidates' && stepData.candidates) {
          setCandidates(stepData.candidates);
          setPanelStep('recognition');
        }
      } else if (res.error) {
        alert(res.error.message);
      }
    } catch (err: any) {
      console.warn("Query handling error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Submit User Answer to Question
  const handleAnswerQuestion = async (answerText: string) => {
    if (!sessionId) return;
    setLoading(true);
    setReferenceBanner(null);

    // Track confirmed clue if positive answer
    if (answerText !== "I don't remember" && currentQuestion) {
      const dimName = currentQuestion.subattributeKey
        ? currentQuestion.subattributeKey.split(':')[1]
        : currentQuestion.dimensionTested;
      if (answerText === "Yes" || answerText.toLowerCase() === dimName.toLowerCase()) {
        setConfirmedClues((prev) => Array.from(new Set([...prev, `${dimName} (${answerText})`])));
      }
    }

    try {
      const res = await submitAnswer(sessionId, answerText, mode);
      if (res.success && res.data) {
        const stepData = res.data;

        if (stepData.progress) {
          setProgress(stepData.progress);
          setNarrowingHistory((prev) => [...prev, stepData.progress!.activeCandidates]);
        }
        if (stepData.selectionMetadata) {
          setSelectionMetadata(stepData.selectionMetadata);
        }

        if (stepData.action === 'ask_question' && stepData.question) {
          setCurrentQuestion(stepData.question);
          setPanelStep('question');
        } else if (stepData.action === 'show_candidates' && stepData.candidates) {
          setCandidates(stepData.candidates);
          setPanelStep('recognition');
        }
      } else if (res.error) {
        alert(res.error.message);
      }
    } catch (err: any) {
      console.warn("Answer error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Candidate Selection ("This is it" / "Looks close" / "None of these")
  const handleSelectFound = async (imageId: string) => {
    if (!sessionId) return;
    setLoading(true);
    setSelectedImageId(imageId);
    try {
      const res = await selectCandidate(sessionId, { selectionType: 'found', imageId }, mode);
      if (res.success && res.data) {
        if (res.data.summary) {
          setFoundSummary(res.data.summary);
        }
        setPanelStep('found');
      } else if (res.error) {
        alert(res.error.message);
      }
    } catch (err: any) {
      console.warn("Select found error:", err);
      setPanelStep('found');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectClose = async (imageId: string) => {
    if (!sessionId) return;
    setLoading(true);
    setReferenceBanner(`Using candidate '${imageId}' as visual reference to narrow search…`);
    try {
      const res = await selectCandidate(sessionId, { selectionType: 'close', imageId }, mode);
      if (res.success && res.data) {
        const stepData = res.data;
        if (stepData.progress) {
          setProgress(stepData.progress);
          setNarrowingHistory((prev) => [...prev, stepData.progress!.activeCandidates]);
        }
        if (stepData.selectionMetadata) {
          setSelectionMetadata(stepData.selectionMetadata);
        }

        if (stepData.action === 'ask_question' && stepData.question) {
          setCurrentQuestion(stepData.question);
          setPanelStep('question');
        } else if (stepData.action === 'show_candidates' && stepData.candidates) {
          setCandidates(stepData.candidates);
          setPanelStep('recognition');
        }
      } else if (res.error) {
        alert(res.error.message);
      }
    } catch (err: any) {
      console.warn("Select close error:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectNone = async () => {
    if (!sessionId) return;
    setLoading(true);
    const rejectedIds = candidates.map((c) => c.imageId);
    try {
      const res = await selectCandidate(sessionId, { selectionType: 'none', rejectedImageIds: rejectedIds }, mode);
      if (res.success && res.data) {
        const stepData = res.data;
        if (stepData.progress) {
          setProgress(stepData.progress);
          setNarrowingHistory((prev) => [...prev, stepData.progress!.activeCandidates]);
        }
        if (stepData.selectionMetadata) {
          setSelectionMetadata(stepData.selectionMetadata);
        }

        if (stepData.action === 'ask_question' && stepData.question) {
          setCurrentQuestion(stepData.question);
          setPanelStep('question');
        } else if (stepData.action === 'show_candidates' && stepData.candidates) {
          setCandidates(stepData.candidates);
          setPanelStep('recognition');
        }
      } else if (res.error) {
        alert(res.error.message);
      }
    } catch (err: any) {
      console.warn("Select none error:", err);
    } finally {
      setLoading(false);
    }
  };

  // Submit Feedback
  const handleSubmitFeedback = async (rating: number, confusingFeedback?: string) => {
    if (!sessionId) return;
    try {
      await submitFeedback(sessionId, { helpfulnessRating: rating, confusingFeedback });
    } catch (err) {
      console.error('Feedback error:', err);
    }
  };

  const activeCandidateIds = candidates.map(c => c.imageId);
  const narrowingPathStr = [...narrowingHistory, 'Found'].join(' → ');

  return (
    <div className="gphotos-app">
      {/* Top Navbar */}
      <Navbar
        onActivateMemoryGuide={handleActivateMemoryGuide}
        onOpenResearchUpload={() => setShowResearchUpload(true)}
        onReset={resetAll}
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        isGuideActive={isGuideActive}
      />

      {/* Main Body */}
      <div className="gphotos-main-body">
        {/* Left Navigation Sidebar */}
        <Sidebar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
          onActivateMemoryGuide={() => handleActivateMemoryGuide()}
        />

        {/* Center Photo Library Grid */}
        <PhotoLibraryGrid
          activeCandidateIds={activeCandidateIds}
          isGuideActive={isGuideActive && panelStep !== 'memory_input'}
          mode={mode}
          uploadedCount={uploadedCount}
        />

        {/* Right Memory Guide AI Panel */}
        {isGuideActive && (
          <MemoryGuidePanel
            step={panelStep}
            onClose={() => setIsGuideActive(false)}
            onSubmitQuery={handleSubmitQuery}
            currentQuestion={currentQuestion}
            progress={progress}
            narrowingHistory={narrowingHistory}
            confirmedClues={confirmedClues}
            onAnswerQuestion={handleAnswerQuestion}
            candidates={candidates}
            onSelectFound={handleSelectFound}
            onSelectClose={handleSelectClose}
            onSelectNone={handleSelectNone}
            foundSummary={foundSummary}
            selectedImageId={selectedImageId}
            narrowingPathStr={narrowingPathStr}
            onSubmitFeedback={handleSubmitFeedback}
            onRestart={resetAll}
            loading={loading}
            referenceBanner={referenceBanner}
            selectionMetadata={selectionMetadata}
            showDebug={showDebug}
            onToggleDebug={() => setShowDebug(!showDebug)}
            mode={mode}
            uploadedCount={uploadedCount}
            sessionId={sessionId}
          />
        )}
      </div>

      {/* Research Upload Modal */}
      {showResearchUpload && (
        <ResearchUploadView
          onUpload={handleUploadPhotos}
          onProceedToQuery={() => {
            setShowResearchUpload(false);
            handleActivateMemoryGuide();
          }}
          onClose={() => setShowResearchUpload(false)}
          loading={loading}
          uploadStatus={uploadStatus}
          imageCount={uploadedCount}
          errorMessage={uploadErrorMessage}
        />
      )}

      {/* Optional Debug Trace Modal/Drawer */}
      {showDebug && (
        <div style={{ position: 'fixed', bottom: 10, left: 10, zIndex: 300 }}>
          <ResearchDebugTrace
            metadata={selectionMetadata}
            progress={progress}
            round={progress?.round}
          />
        </div>
      )}
    </div>
  );
}
