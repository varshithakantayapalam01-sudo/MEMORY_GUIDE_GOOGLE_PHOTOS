'use client';

import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import LandingView from '@/components/LandingView';
import ResearchUploadView from '@/components/ResearchUploadView';
import MemoryInputView from '@/components/MemoryInputView';
import QuestionCard from '@/components/QuestionCard';
import RecognitionGrid from '@/components/RecognitionGrid';
import FoundOutcome from '@/components/FoundOutcome';
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

type AppStep = 'landing' | 'research_upload' | 'memory_input' | 'question' | 'recognition' | 'found';

export default function HomePage() {
  const [step, setStep] = useState<AppStep>('landing');
  const [mode, setMode] = useState<'demo' | 'research' | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Loading & Error States
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Upload state
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'ready' | 'error'>('idle');
  const [uploadedCount, setUploadedCount] = useState<number>(0);

  // Active Retrieval Session State
  const [currentQuestion, setCurrentQuestion] = useState<QuestionData | undefined>(undefined);
  const [candidates, setCandidates] = useState<CandidateData[]>([]);
  const [progress, setProgress] = useState<ProgressData | undefined>(undefined);
  const [selectionMetadata, setSelectionMetadata] = useState<SelectionMetadata | undefined>(undefined);
  const [foundSummary, setFoundSummary] = useState<FoundSummary | undefined>(undefined);

  // Narrowing history trace (e.g., [24, 12, 7])
  const [narrowingHistory, setNarrowingHistory] = useState<number[]>([]);
  const [confirmedClues, setConfirmedClues] = useState<string[]>([]);
  const [referenceBanner, setReferenceBanner] = useState<string | null>(null);

  // Research Debug Trace Toggle
  const [showDebug, setShowDebug] = useState<boolean>(
    process.env.NEXT_PUBLIC_SHOW_RESEARCH_DEBUG === 'true'
  );

  const resetAll = () => {
    setStep('landing');
    setMode(null);
    setSessionId(null);
    setLoading(false);
    setErrorMessage(null);
    setUploadStatus('idle');
    setUploadedCount(0);
    setCurrentQuestion(undefined);
    setCandidates([]);
    setProgress(undefined);
    setSelectionMetadata(undefined);
    setFoundSummary(undefined);
    setNarrowingHistory([]);
    setConfirmedClues([]);
    setReferenceBanner(null);
  };

  // 1. Create Demo Session
  const handleStartDemo = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const res = await createSession('demo');
      if (res.success && res.data) {
        setSessionId(res.data.sessionId);
        setMode('demo');
        setStep('memory_input');
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to create demo session.');
    } finally {
      setLoading(false);
    }
  };

  // 2. Create Research Session
  const handleStartResearch = async () => {
    setLoading(true);
    setErrorMessage(null);
    try {
      const res = await createSession('research');
      if (res.success && res.data) {
        setSessionId(res.data.sessionId);
        setMode('research');
        setStep('research_upload');
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to create research session.');
    } finally {
      setLoading(false);
    }
  };

  // 3. Upload Research Photos
  const handleUploadPhotos = async (files: File[]) => {
    if (!sessionId) return;
    setLoading(true);
    setUploadStatus('uploading');
    setErrorMessage(null);
    try {
      const res = await uploadPhotos(sessionId, files);
      if (res.success && res.data) {
        setUploadedCount(res.data.imageCount || files.length);
        setUploadStatus('ready');
      }
    } catch (err: any) {
      setUploadStatus('error');
      setErrorMessage(err.message || 'Failed to upload photos.');
    } finally {
      setLoading(false);
    }
  };

  // 4. Submit Initial Vague Memory Query
  const handleSubmitQuery = async (query: string) => {
    if (!sessionId) return;
    setLoading(true);
    setErrorMessage(null);
    try {
      const res = await submitQuery(sessionId, query);
      if (res.success && res.data) {
        const stepData = res.data;
        if (stepData.progress) {
          setProgress(stepData.progress);
          setNarrowingHistory([stepData.progress.activeCandidates + stepData.progress.reserveCandidates]);
        }
        if (stepData.selectionMetadata) {
          setSelectionMetadata(stepData.selectionMetadata);
        }

        if (stepData.action === 'ask_question' && stepData.question) {
          setCurrentQuestion(stepData.question);
          setStep('question');
        } else if (stepData.action === 'show_candidates' && stepData.candidates) {
          setCandidates(stepData.candidates);
          setStep('recognition');
        }
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Error executing query. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // 5. Submit User Answer to Question
  const handleAnswerQuestion = async (answerText: string) => {
    if (!sessionId) return;
    setLoading(true);
    setErrorMessage(null);
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
      const res = await submitAnswer(sessionId, answerText);
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
          setStep('question');
        } else if (stepData.action === 'show_candidates' && stepData.candidates) {
          setCandidates(stepData.candidates);
          setStep('recognition');
        }
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Error processing answer.');
    } finally {
      setLoading(false);
    }
  };

  // 6. Candidate Selection ("This is it" / "Looks close" / "None of these")
  const handleSelectFound = async (imageId: string) => {
    if (!sessionId) return;
    setLoading(true);
    setErrorMessage(null);
    try {
      const res = await selectCandidate(sessionId, { selectionType: 'found', imageId });
      if (res.success && res.data) {
        if (res.data.summary) {
          setFoundSummary(res.data.summary);
        }
        setStep('found');
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to select image.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectClose = async (imageId: string) => {
    if (!sessionId) return;
    setLoading(true);
    setErrorMessage(null);
    setReferenceBanner(`Using candidate '${imageId}' as visual reference to narrow search…`);
    try {
      const res = await selectCandidate(sessionId, { selectionType: 'close', imageId });
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
          setStep('question');
        } else if (stepData.action === 'show_candidates' && stepData.candidates) {
          setCandidates(stepData.candidates);
          setStep('recognition');
        }
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Error processing reference selection.');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectNone = async () => {
    if (!sessionId) return;
    setLoading(true);
    setErrorMessage(null);
    const rejectedIds = candidates.map((c) => c.imageId);
    try {
      const res = await selectCandidate(sessionId, { selectionType: 'none', rejectedImageIds: rejectedIds });
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
          setStep('question');
        } else if (stepData.action === 'show_candidates' && stepData.candidates) {
          setCandidates(stepData.candidates);
          setStep('recognition');
        }
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Error processing rejection.');
    } finally {
      setLoading(false);
    }
  };

  // 7. Submit Helpfulness Feedback
  const handleSubmitFeedback = async (rating: number, confusingFeedback?: string) => {
    if (!sessionId) return;
    setLoading(true);
    try {
      await submitFeedback(sessionId, { helpfulnessRating: rating, confusingFeedback });
    } catch (err) {
      console.error('Feedback error:', err);
    } finally {
      setLoading(false);
    }
  };

  const narrowingPathStr = [...narrowingHistory, 'Found'].join(' → ');

  return (
    <div className="app-wrapper">
      <Navbar
        mode={mode}
        onReset={resetAll}
        showDebug={showDebug}
        onToggleDebug={() => setShowDebug(!showDebug)}
      />

      {errorMessage && (
        <div
          style={{
            background: 'rgba(248, 113, 113, 0.12)',
            border: '1px solid var(--danger-color)',
            color: 'var(--danger-color)',
            padding: '1rem 1.25rem',
            borderRadius: '12px',
            marginBottom: '1.5rem',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <span>⚠️ {errorMessage}</span>
          <button
            className="btn-ghost"
            onClick={() => setErrorMessage(null)}
            style={{ color: 'var(--danger-color)' }}
          >
            Dismiss
          </button>
        </div>
      )}

      <main>
        {step === 'landing' && (
          <LandingView
            onStartDemo={handleStartDemo}
            onStartResearch={handleStartResearch}
            loading={loading}
          />
        )}

        {step === 'research_upload' && (
          <ResearchUploadView
            onUpload={handleUploadPhotos}
            onProceedToQuery={() => setStep('memory_input')}
            loading={loading}
            uploadStatus={uploadStatus}
            imageCount={uploadedCount}
            errorMessage={errorMessage || undefined}
          />
        )}

        {step === 'memory_input' && (
          <MemoryInputView
            onSubmitQuery={handleSubmitQuery}
            loading={loading}
          />
        )}

        {step === 'question' && currentQuestion && (
          <QuestionCard
            question={currentQuestion}
            progress={progress}
            narrowingHistory={narrowingHistory}
            confirmedClues={confirmedClues}
            onAnswer={handleAnswerQuestion}
            loading={loading}
            referenceBanner={referenceBanner}
          />
        )}

        {step === 'recognition' && (
          <RecognitionGrid
            candidates={candidates}
            onSelectFound={handleSelectFound}
            onSelectClose={handleSelectClose}
            onSelectNone={handleSelectNone}
            loading={loading}
          />
        )}

        {step === 'found' && (
          <FoundOutcome
            selectedImageId={candidates[0]?.imageId}
            summary={foundSummary}
            narrowingPathStr={narrowingPathStr}
            onSubmitFeedback={handleSubmitFeedback}
            onRestart={resetAll}
            loading={loading}
          />
        )}

        {/* Collapsible Research Debug Trace */}
        {showDebug && (
          <ResearchDebugTrace
            metadata={selectionMetadata}
            progress={progress}
            round={progress?.round}
          />
        )}
      </main>
    </div>
  );
}
