import { StepResponseData, CandidateData } from './api';

export interface DemoPhoto {
  image_id: string;
  filename: string;
  image_url: string;
  cluster_id: string;
  manual_label: string;
  attributes: {
    event: 'birthday' | 'vacation' | 'outdoor' | 'celebration';
    location: 'indoors' | 'outdoor';
    cake?: boolean;
    balloons?: boolean;
    people: 'solo' | 'pair' | 'group' | 'family';
    clothing_color?: string[];
    traditional?: boolean;
    sparklers?: boolean;
    diyas_flowers?: boolean;
    dog?: boolean;
  };
}

export const DEMO_PHOTOS: DemoPhoto[] = [
  { image_id: "demo_001", filename: "birthday_01.jpg", image_url: "/images/demo-photos/birthday_01.jpg", cluster_id: "birthday", manual_label: "Childhood birthday celebration indoors with pink dress, cake, and balloons", attributes: { event: "birthday", location: "indoors", cake: true, balloons: true, people: "family", clothing_color: ["pink"] } },
  { image_id: "demo_002", filename: "birthday_02.jpg", image_url: "/images/demo-photos/birthday_02.jpg", cluster_id: "birthday", manual_label: "Birthday party indoors with yellow dress, chocolate cake, and yellow balloons", attributes: { event: "birthday", location: "indoors", cake: true, balloons: true, people: "group", clothing_color: ["yellow"] } },
  { image_id: "demo_003", filename: "birthday_03.jpg", image_url: "/images/demo-photos/birthday_03.jpg", cluster_id: "birthday", manual_label: "Outdoor birthday celebration on patio with blue shirt and cake", attributes: { event: "birthday", location: "outdoor", cake: true, balloons: false, people: "group", clothing_color: ["blue"] } },
  { image_id: "demo_004", filename: "birthday_04.jpg", image_url: "/images/demo-photos/birthday_04.jpg", cluster_id: "birthday", manual_label: "Solo adult in pink sweater holding a birthday cupcake indoors with balloons", attributes: { event: "birthday", location: "indoors", cake: true, balloons: true, people: "solo", clothing_color: ["pink"] } },
  { image_id: "demo_005", filename: "birthday_05.jpg", image_url: "/images/demo-photos/birthday_05.jpg", cluster_id: "birthday", manual_label: "Restaurant birthday dinner with black and gold attire, cake, and sparklers", attributes: { event: "birthday", location: "indoors", cake: true, sparklers: true, people: "group", clothing_color: ["black", "gold"] } },
  { image_id: "demo_006", filename: "birthday_06.jpg", image_url: "/images/demo-photos/birthday_06.jpg", cluster_id: "birthday", manual_label: "Outdoor park pavilion birthday party with pink t-shirt and colorful balloons", attributes: { event: "birthday", location: "outdoor", cake: true, balloons: true, people: "group", clothing_color: ["pink"] } },
  { image_id: "demo_007", filename: "birthday_07.jpg", image_url: "/images/demo-photos/birthday_07.jpg", cluster_id: "birthday", manual_label: "Child in blue outfit at indoor birthday party with yellow balloons and cake", attributes: { event: "birthday", location: "indoors", cake: true, balloons: true, people: "family", clothing_color: ["blue"] } },
  { image_id: "demo_008", filename: "birthday_08.jpg", image_url: "/images/demo-photos/birthday_08.jpg", cluster_id: "birthday", manual_label: "Outdoor garden birthday gathering in yellow and white clothing with cake and balloons", attributes: { event: "birthday", location: "outdoor", cake: true, balloons: true, people: "group", clothing_color: ["yellow", "white"] } },
  { image_id: "demo_009", filename: "beach_01.jpg", image_url: "/images/demo-photos/beach_01.jpg", cluster_id: "vacation", manual_label: "Family beach trip during golden hour sunset near ocean waves", attributes: { event: "vacation", location: "outdoor", people: "family" } },
  { image_id: "demo_010", filename: "beach_02.jpg", image_url: "/images/demo-photos/beach_02.jpg", cluster_id: "vacation", manual_label: "Solo person walking along sandy beach coast in blue swimwear and sun hat", attributes: { event: "vacation", location: "outdoor", people: "solo", clothing_color: ["blue"] } },
  { image_id: "demo_011", filename: "beach_03.jpg", image_url: "/images/demo-photos/beach_03.jpg", cluster_id: "vacation", manual_label: "Sitting under beach umbrella on sunny coast wearing white shirt and sunglasses", attributes: { event: "vacation", location: "outdoor", people: "solo", clothing_color: ["white"] } },
  { image_id: "demo_012", filename: "beach_04.jpg", image_url: "/images/demo-photos/beach_04.jpg", cluster_id: "vacation", manual_label: "Friends sitting on beach blanket wearing pink and white casual tops near ocean", attributes: { event: "vacation", location: "outdoor", people: "group", clothing_color: ["pink", "white"] } },
  { image_id: "demo_013", filename: "beach_05.jpg", image_url: "/images/demo-photos/beach_05.jpg", cluster_id: "vacation", manual_label: "Pair walking along rocky beach coastline with sun hats and blue ocean background", attributes: { event: "vacation", location: "outdoor", people: "pair" } },
  { image_id: "demo_014", filename: "beach_06.jpg", image_url: "/images/demo-photos/beach_06.jpg", cluster_id: "vacation", manual_label: "Group playing beach volleyball on sunny sandy coast near water", attributes: { event: "vacation", location: "outdoor", people: "group" } },
  { image_id: "demo_015", filename: "beach_07.jpg", image_url: "/images/demo-photos/beach_07.jpg", cluster_id: "vacation", manual_label: "Solo person in yellow sun dress standing near palm trees on beach trip", attributes: { event: "vacation", location: "outdoor", people: "solo", clothing_color: ["yellow"] } },
  { image_id: "demo_016", filename: "park_01.jpg", image_url: "/images/demo-photos/park_01.jpg", cluster_id: "outdoor", manual_label: "Picnic on red checkered blanket on green park grass with basket and food", attributes: { event: "outdoor", location: "outdoor", people: "group", clothing_color: ["red"] } },
  { image_id: "demo_017", filename: "park_02.jpg", image_url: "/images/demo-photos/park_02.jpg", cluster_id: "outdoor", manual_label: "Friends playing frisbee in sports clothing on open green park field", attributes: { event: "outdoor", location: "outdoor", people: "group" } },
  { image_id: "demo_018", filename: "park_03.jpg", image_url: "/images/demo-photos/park_03.jpg", cluster_id: "outdoor", manual_label: "Solo person in pink hoodie walking a Golden Retriever dog along park path", attributes: { event: "outdoor", location: "outdoor", people: "solo", dog: true, clothing_color: ["pink"] } },
  { image_id: "demo_019", filename: "park_04.jpg", image_url: "/images/demo-photos/park_04.jpg", cluster_id: "outdoor", manual_label: "Family outdoor picnic gathering on blanket under park oak tree at sunset", attributes: { event: "outdoor", location: "outdoor", people: "family" } },
  { image_id: "demo_020", filename: "park_05.jpg", image_url: "/images/demo-photos/park_05.jpg", cluster_id: "outdoor", manual_label: "Group playing soccer in blue athletic wear on open park grass field", attributes: { event: "outdoor", location: "outdoor", people: "group", clothing_color: ["blue"] } },
  { image_id: "demo_021", filename: "park_06.jpg", image_url: "/images/demo-photos/park_06.jpg", cluster_id: "outdoor", manual_label: "Person in yellow jacket sitting on wooden bench surrounded by green park trees", attributes: { event: "outdoor", location: "outdoor", people: "solo", clothing_color: ["yellow"] } },
  { image_id: "demo_022", filename: "park_07.jpg", image_url: "/images/demo-photos/park_07.jpg", cluster_id: "outdoor", manual_label: "Group gathering on park grass with picnic blanket and a dog eating snacks", attributes: { event: "outdoor", location: "outdoor", people: "group", dog: true } },
  { image_id: "demo_023", filename: "festival_01.jpg", image_url: "/images/demo-photos/festival_01.jpg", cluster_id: "celebration", manual_label: "Diwali festival celebration indoors with illuminated diyas and traditional sweets", attributes: { event: "celebration", location: "indoors", traditional: true, diyas_flowers: true, people: "family" } },
  { image_id: "demo_024", filename: "wedding_01.jpg", image_url: "/images/demo-photos/wedding_01.jpg", cluster_id: "celebration", manual_label: "Traditional wedding ceremony in outdoor garden with floral arch and bridal gown", attributes: { event: "celebration", location: "outdoor", traditional: true, people: "group" } },
  { image_id: "demo_025", filename: "festival_02.jpg", image_url: "/images/demo-photos/festival_02.jpg", cluster_id: "celebration", manual_label: "Outdoor festival celebration lighting sparklers and diyas in pink and yellow ethnic kurti", attributes: { event: "celebration", location: "outdoor", traditional: true, sparklers: true, clothing_color: ["pink", "yellow"], people: "group" } },
  { image_id: "demo_026", filename: "festival_03.jpg", image_url: "/images/demo-photos/festival_03.jpg", cluster_id: "celebration", manual_label: "Formal indoor celebration with formal suits, sarees, and floral decorations", attributes: { event: "celebration", location: "indoors", traditional: true, people: "group" } },
  { image_id: "demo_027", filename: "festival_04.jpg", image_url: "/images/demo-photos/festival_04.jpg", cluster_id: "celebration", manual_label: "Festival sweets preparation indoors with yellow traditional dress and marigold flowers", attributes: { event: "celebration", location: "indoors", traditional: true, diyas_flowers: true, clothing_color: ["yellow"], people: "group" } },
  { image_id: "demo_028", filename: "wedding_02.jpg", image_url: "/images/demo-photos/wedding_02.jpg", cluster_id: "celebration", manual_label: "Formal outdoor wedding party in garden with flower beds and formal attire", attributes: { event: "celebration", location: "outdoor", traditional: true, people: "group" } },
  { image_id: "demo_029", filename: "festival_05.jpg", image_url: "/images/demo-photos/festival_05.jpg", cluster_id: "celebration", manual_label: "Family decorating entrance with marigold flowers and diyas for festival celebration", attributes: { event: "celebration", location: "outdoor", traditional: true, diyas_flowers: true, people: "family" } },
];

export interface FallbackSessionState {
  sessionId: string;
  query: string;
  candidateIds: string[];
  rejectedIds: string[];
  round: number;
  questionsAsked: string[];
  history: number[];
}

const activeSessions: Record<string, FallbackSessionState> = {};

export function createFallbackSession(mode: 'demo' | 'research'): string {
  const sessionId = 'fallback_sess_' + Math.random().toString(36).substring(2, 9);
  activeSessions[sessionId] = {
    sessionId,
    query: '',
    candidateIds: DEMO_PHOTOS.map(p => p.image_id),
    rejectedIds: [],
    round: 0,
    questionsAsked: [],
    history: [29],
  };
  return sessionId;
}

export function handleFallbackQuery(sessionId: string, query: string): StepResponseData {
  const session = activeSessions[sessionId] || {
    sessionId,
    query,
    candidateIds: DEMO_PHOTOS.map(p => p.image_id),
    rejectedIds: [],
    round: 0,
    questionsAsked: [],
    history: [29],
  };
  session.query = query;
  activeSessions[sessionId] = session;

  const lower = query.toLowerCase();

  // Determine initial candidate pool based on query terms
  let matching: DemoPhoto[] = [];
  if (lower.includes('birthday') || lower.includes('cake') || lower.includes('balloon')) {
    matching = DEMO_PHOTOS.filter(p => p.attributes.event === 'birthday');
  } else if (lower.includes('beach') || lower.includes('vacation') || lower.includes('ocean') || lower.includes('wave')) {
    matching = DEMO_PHOTOS.filter(p => p.attributes.event === 'vacation');
  } else if (lower.includes('festival') || lower.includes('traditional') || lower.includes('diwali') || lower.includes('wedding')) {
    matching = DEMO_PHOTOS.filter(p => p.attributes.event === 'celebration');
  } else if (lower.includes('park') || lower.includes('picnic') || lower.includes('frisbee') || lower.includes('dog')) {
    matching = DEMO_PHOTOS.filter(p => p.attributes.event === 'outdoor');
  } else {
    // default subset of 12
    matching = DEMO_PHOTOS.slice(0, 12);
  }

  session.candidateIds = matching.map(p => p.image_id);
  session.round = 1;
  const activeCount = matching.length;
  const reserveCount = 29 - activeCount;
  session.history = [29, activeCount];

  // Pick best discriminative question for candidate pool
  let questionText = "Was a cake visible in the photo?";
  let options = ["Yes", "No", "I don't remember"];
  let dimTested = "cake_visible";
  let subKey = "environment:cake";

  if (matching.every(p => p.attributes.event === 'birthday')) {
    questionText = "Was this birthday celebration indoors or somewhere outside?";
    options = ["Indoors", "Outside", "I don't remember"];
    dimTested = "environment";
    subKey = "environment:location";
  } else if (matching.every(p => p.attributes.event === 'vacation')) {
    questionText = "Were you with a group of people, or was it a solo/pair photo?";
    options = ["Group", "Solo or pair", "I don't remember"];
    dimTested = "social";
    subKey = "people_count:group";
  } else if (matching.every(p => p.attributes.event === 'celebration')) {
    questionText = "Were sparklers or diyas lit in the photo?";
    options = ["Yes", "No", "I don't remember"];
    dimTested = "props";
    subKey = "props:sparklers_diyas";
  }

  session.questionsAsked.push(questionText);

  return {
    action: 'ask_question',
    question: {
      questionId: 'q_' + session.round,
      round: session.round,
      text: questionText,
      options,
      dimensionTested: dimTested,
      subattributeKey: subKey,
    },
    progress: {
      activeCandidates: activeCount,
      reserveCandidates: reserveCount,
      round: session.round,
    },
    selectionMetadata: {
      dimension: dimTested,
      subattributeKey: subKey,
      discriminationScore: 0.88,
      memorabilityWeight: 0.72,
      finalScore: 0.63,
    },
  };
}

export function handleFallbackAnswer(sessionId: string, answerText: string): StepResponseData {
  const session = activeSessions[sessionId];
  if (!session) {
    return handleFallbackQuery(sessionId, "memory");
  }

  session.round += 1;
  let candidates = DEMO_PHOTOS.filter(p => session.candidateIds.includes(p.image_id) && !session.rejectedIds.includes(p.image_id));

  // Filter candidates based on answer
  const ansLower = answerText.toLowerCase();
  if (ansLower.includes('indoors')) {
    const filtered = candidates.filter(p => p.attributes.location === 'indoors');
    if (filtered.length > 0) candidates = filtered;
  } else if (ansLower.includes('outside') || ansLower.includes('outdoor')) {
    const filtered = candidates.filter(p => p.attributes.location === 'outdoor');
    if (filtered.length > 0) candidates = filtered;
  } else if (ansLower.includes('group')) {
    const filtered = candidates.filter(p => p.attributes.people === 'group' || p.attributes.people === 'family');
    if (filtered.length > 0) candidates = filtered;
  } else if (ansLower.includes('solo')) {
    const filtered = candidates.filter(p => p.attributes.people === 'solo' || p.attributes.people === 'pair');
    if (filtered.length > 0) candidates = filtered;
  } else if (ansLower.includes('yes')) {
    const filtered = candidates.filter(p => p.attributes.cake || p.attributes.sparklers || p.attributes.diyas_flowers || p.attributes.balloons);
    if (filtered.length > 0) candidates = filtered;
  }

  session.candidateIds = candidates.map(p => p.image_id);
  const activeCount = Math.max(3, candidates.length);
  session.history.push(activeCount);

  // If candidate pool is 3 to 6 photos, move to recognition phase!
  if (candidates.length <= 6 || session.round >= 3) {
    const cData: CandidateData[] = candidates.slice(0, 6).map((p, idx) => ({
      imageId: p.image_id,
      rank: idx + 1,
      score: Number((0.95 - idx * 0.05).toFixed(2)),
      semanticScore: 0.90,
      structuredScore: 0.88,
      imageUrl: p.image_url,
    }));

    return {
      action: 'show_candidates',
      candidates: cData,
      progress: {
        activeCandidates: cData.length,
        reserveCandidates: 29 - cData.length,
        round: session.round,
      },
      selectionMetadata: {
        dimension: "recognition_phase",
        discriminationScore: 0.92,
        memorabilityWeight: 0.80,
        finalScore: 0.74,
      }
    };
  }

  // Next question
  let nextQuestion = "Do you remember if anyone was wearing pink or yellow?";
  let options = ["Pink or yellow", "Other colors", "I don't remember"];
  if (ansLower.includes('indoors')) {
    nextQuestion = "Were balloons visible in the background?";
    options = ["Balloons present", "No balloons", "I don't remember"];
  }

  session.questionsAsked.push(nextQuestion);

  return {
    action: 'ask_question',
    question: {
      questionId: 'q_' + session.round,
      round: session.round,
      text: nextQuestion,
      options,
      dimensionTested: "clothing_and_decor",
      subattributeKey: "attire:color",
    },
    progress: {
      activeCandidates: activeCount,
      reserveCandidates: 29 - activeCount,
      round: session.round,
    },
    selectionMetadata: {
      dimension: "clothing_and_decor",
      subattributeKey: "attire:color",
      discriminationScore: 0.85,
      memorabilityWeight: 0.70,
      finalScore: 0.60,
    }
  };
}

export function handleFallbackSelect(
  sessionId: string,
  payload: { selectionType: 'found' | 'close' | 'none'; imageId?: string; rejectedImageIds?: string[] }
): StepResponseData {
  const session = activeSessions[sessionId] || {
    sessionId,
    query: "photo",
    candidateIds: ["demo_001", "demo_002", "demo_003", "demo_004"],
    rejectedIds: [],
    round: 2,
    questionsAsked: ["Was a cake visible?", "Was it indoors?"],
    history: [29, 12, 4],
  };

  if (payload.selectionType === 'found') {
    const targetId = payload.imageId || session.candidateIds[0] || "demo_001";
    const targetPhoto = DEMO_PHOTOS.find(p => p.image_id === targetId) || DEMO_PHOTOS[0];

    return {
      action: 'found',
      selectedImageId: targetId,
      candidates: [{
        imageId: targetPhoto.image_id,
        rank: 1,
        score: 0.98,
        semanticScore: 0.96,
        structuredScore: 0.94,
        imageUrl: targetPhoto.image_url,
      }],
      summary: {
        totalRounds: session.round,
        totalIdkCount: 0,
        questionsAsked: session.questionsAsked,
        candidateNarrowingPath: session.history.concat([1]).join(' → '),
      }
    };
  }

  if (payload.selectionType === 'close') {
    // Narrow further using target photo characteristics
    const refPhoto = DEMO_PHOTOS.find(p => p.image_id === payload.imageId);
    session.round += 1;
    const remaining = DEMO_PHOTOS.filter(p => p.cluster_id === (refPhoto?.cluster_id || 'birthday')).slice(0, 4);

    return {
      action: 'show_candidates',
      candidates: remaining.map((p, idx) => ({
        imageId: p.image_id,
        rank: idx + 1,
        score: 0.95 - idx * 0.04,
        semanticScore: 0.92,
        structuredScore: 0.90,
        imageUrl: p.image_url,
      })),
      progress: {
        activeCandidates: remaining.length,
        reserveCandidates: 29 - remaining.length,
        round: session.round,
      }
    };
  }

  // selectionType === 'none'
  if (payload.rejectedImageIds) {
    session.rejectedIds.push(...payload.rejectedImageIds);
  }
  session.round += 1;
  const remaining = DEMO_PHOTOS.filter(p => !session.rejectedIds.includes(p.image_id)).slice(0, 4);

  return {
    action: 'ask_question',
    question: {
      questionId: 'q_' + session.round,
      round: session.round,
      text: "Was this photo taken during the day or at night?",
      options: ["Daytime", "Night time", "I don't remember"],
      dimensionTested: "time_of_day",
      subattributeKey: "environment:time",
    },
    progress: {
      activeCandidates: remaining.length,
      reserveCandidates: 29 - remaining.length,
      round: session.round,
    }
  };
}
