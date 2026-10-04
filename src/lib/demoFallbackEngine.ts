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
  { image_id: "demo_001", filename: "birthday_01.jpg", image_url: "https://images.unsplash.com/photo-1530103862676-de8c9debad1d?w=600&auto=format&fit=crop&q=80", cluster_id: "birthday", manual_label: "Childhood birthday celebration indoors with pink dress, cake, and balloons", attributes: { event: "birthday", location: "indoors", cake: true, balloons: true, people: "family", clothing_color: ["pink"] } },
  { image_id: "demo_002", filename: "birthday_02.jpg", image_url: "https://images.unsplash.com/photo-1513151233558-d860c5398176?w=600&auto=format&fit=crop&q=80", cluster_id: "birthday", manual_label: "Birthday party indoors with yellow dress, chocolate cake, and yellow balloons", attributes: { event: "birthday", location: "indoors", cake: true, balloons: true, people: "group", clothing_color: ["yellow"] } },
  { image_id: "demo_003", filename: "birthday_03.jpg", image_url: "https://images.unsplash.com/photo-1464349095431-e9a21285b5f3?w=600&auto=format&fit=crop&q=80", cluster_id: "birthday", manual_label: "Outdoor birthday celebration on patio with blue shirt and cake", attributes: { event: "birthday", location: "outdoor", cake: true, balloons: false, people: "group", clothing_color: ["blue"] } },
  { image_id: "demo_004", filename: "birthday_04.jpg", image_url: "https://images.unsplash.com/photo-1558636508-e0db3814bd1d?w=600&auto=format&fit=crop&q=80", cluster_id: "birthday", manual_label: "Solo adult in pink sweater holding a birthday cupcake indoors with balloons", attributes: { event: "birthday", location: "indoors", cake: true, balloons: true, people: "solo", clothing_color: ["pink"] } },
  { image_id: "demo_005", filename: "birthday_05.jpg", image_url: "https://images.unsplash.com/photo-1514525253161-7a46d19cd819?w=600&auto=format&fit=crop&q=80", cluster_id: "birthday", manual_label: "Restaurant birthday dinner with black and gold attire, cake, and sparklers", attributes: { event: "birthday", location: "indoors", cake: true, sparklers: true, people: "group", clothing_color: ["black", "gold"] } },
  { image_id: "demo_006", filename: "birthday_06.jpg", image_url: "https://images.unsplash.com/photo-1527529482837-4698179dc6ce?w=600&auto=format&fit=crop&q=80", cluster_id: "birthday", manual_label: "Outdoor park pavilion birthday party with pink t-shirt and colorful balloons", attributes: { event: "birthday", location: "outdoor", cake: true, balloons: true, people: "group", clothing_color: ["pink"] } },
  { image_id: "demo_007", filename: "birthday_07.jpg", image_url: "https://images.unsplash.com/photo-1566737236500-c8ac43014a67?w=600&auto=format&fit=crop&q=80", cluster_id: "birthday", manual_label: "Child in blue outfit at indoor birthday party with yellow balloons and cake", attributes: { event: "birthday", location: "indoors", cake: true, balloons: true, people: "family", clothing_color: ["blue"] } },
  { image_id: "demo_008", filename: "birthday_08.jpg", image_url: "https://images.unsplash.com/photo-1513272565700-984444585f8c?w=600&auto=format&fit=crop&q=80", cluster_id: "birthday", manual_label: "Outdoor garden birthday gathering in yellow and white clothing with cake and balloons", attributes: { event: "birthday", location: "outdoor", cake: true, balloons: true, people: "group", clothing_color: ["yellow", "white"] } },
  { image_id: "demo_009", filename: "beach_01.jpg", image_url: "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600&auto=format&fit=crop&q=80", cluster_id: "vacation", manual_label: "Family beach trip during golden hour sunset near ocean waves", attributes: { event: "vacation", location: "outdoor", people: "family" } },
  { image_id: "demo_010", filename: "beach_02.jpg", image_url: "https://images.unsplash.com/photo-1519046904884-53103b34b206?w=600&auto=format&fit=crop&q=80", cluster_id: "vacation", manual_label: "Solo person walking along sandy beach coast in blue swimwear and sun hat", attributes: { event: "vacation", location: "outdoor", people: "solo", clothing_color: ["blue"] } },
  { image_id: "demo_011", filename: "beach_03.jpg", image_url: "https://images.unsplash.com/photo-1506929562872-bb421503ef21?w=600&auto=format&fit=crop&q=80", cluster_id: "vacation", manual_label: "Sitting under beach umbrella on sunny coast wearing white shirt and sunglasses", attributes: { event: "vacation", location: "outdoor", people: "solo", clothing_color: ["white"] } },
  { image_id: "demo_012", filename: "beach_04.jpg", image_url: "https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=600&auto=format&fit=crop&q=80", cluster_id: "vacation", manual_label: "Friends sitting on beach blanket wearing pink and white casual tops near ocean", attributes: { event: "vacation", location: "outdoor", people: "group", clothing_color: ["pink", "white"] } },
  { image_id: "demo_013", filename: "beach_05.jpg", image_url: "https://images.unsplash.com/photo-1471922694854-ff1b63b20054?w=600&auto=format&fit=crop&q=80", cluster_id: "vacation", manual_label: "Pair walking along rocky beach coastline with sun hats and blue ocean background", attributes: { event: "vacation", location: "outdoor", people: "pair" } },
  { image_id: "demo_014", filename: "beach_06.jpg", image_url: "https://images.unsplash.com/photo-1612872087720-bb876e2e67d1?w=600&auto=format&fit=crop&q=80", cluster_id: "vacation", manual_label: "Group playing beach volleyball on sunny sandy coast near water", attributes: { event: "vacation", location: "outdoor", people: "group" } },
  { image_id: "demo_015", filename: "beach_07.jpg", image_url: "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=600&auto=format&fit=crop&q=80", cluster_id: "vacation", manual_label: "Solo person in yellow sun dress standing near palm trees on beach trip", attributes: { event: "vacation", location: "outdoor", people: "solo", clothing_color: ["yellow"] } },
  { image_id: "demo_016", filename: "park_01.jpg", image_url: "https://images.unsplash.com/photo-1526772662000-3f88f10405ff?w=600&auto=format&fit=crop&q=80", cluster_id: "outdoor", manual_label: "Picnic on red checkered blanket on green park grass with basket and food", attributes: { event: "outdoor", location: "outdoor", people: "group", clothing_color: ["red"] } },
  { image_id: "demo_017", filename: "park_02.jpg", image_url: "https://images.unsplash.com/photo-1533105079780-92b9be482077?w=600&auto=format&fit=crop&q=80", cluster_id: "outdoor", manual_label: "Friends playing frisbee in sports clothing on open green park field", attributes: { event: "outdoor", location: "outdoor", people: "group" } },
  { image_id: "demo_018", filename: "park_03.jpg", image_url: "https://images.unsplash.com/photo-1543466835-00a7907e9de1?w=600&auto=format&fit=crop&q=80", cluster_id: "outdoor", manual_label: "Solo person in pink hoodie walking a Golden Retriever dog along park path", attributes: { event: "outdoor", location: "outdoor", people: "solo", dog: true, clothing_color: ["pink"] } },
  { image_id: "demo_019", filename: "park_04.jpg", image_url: "https://images.unsplash.com/photo-1470246973918-29a93221c455?w=600&auto=format&fit=crop&q=80", cluster_id: "outdoor", manual_label: "Family outdoor picnic gathering on blanket under park oak tree at sunset", attributes: { event: "outdoor", location: "outdoor", people: "family" } },
  { image_id: "demo_020", filename: "park_05.jpg", image_url: "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=600&auto=format&fit=crop&q=80", cluster_id: "outdoor", manual_label: "Group playing soccer in blue athletic wear on open park grass field", attributes: { event: "outdoor", location: "outdoor", people: "group", clothing_color: ["blue"] } },
  { image_id: "demo_021", filename: "park_06.jpg", image_url: "https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=600&auto=format&fit=crop&q=80", cluster_id: "outdoor", manual_label: "Person in yellow jacket sitting on wooden bench surrounded by green park trees", attributes: { event: "outdoor", location: "outdoor", people: "solo", clothing_color: ["yellow"] } },
  { image_id: "demo_022", filename: "park_07.jpg", image_url: "https://images.unsplash.com/photo-1517457373958-b7bdd4587205?w=600&auto=format&fit=crop&q=80", cluster_id: "outdoor", manual_label: "Group gathering on park grass with picnic blanket and a dog eating snacks", attributes: { event: "outdoor", location: "outdoor", people: "group", dog: true } },
  { image_id: "demo_023", filename: "festival_01.jpg", image_url: "https://images.unsplash.com/photo-1605826832916-d0ea9d6fe71e?w=600&auto=format&fit=crop&q=80", cluster_id: "celebration", manual_label: "Diwali festival celebration indoors with illuminated diyas and traditional sweets", attributes: { event: "celebration", location: "indoors", traditional: true, diyas_flowers: true, people: "family" } },
  { image_id: "demo_024", filename: "wedding_01.jpg", image_url: "https://images.unsplash.com/photo-1519741497674-611481863552?w=600&auto=format&fit=crop&q=80", cluster_id: "celebration", manual_label: "Traditional wedding ceremony in outdoor garden with floral arch and bridal gown", attributes: { event: "celebration", location: "outdoor", traditional: true, people: "group" } },
  { image_id: "demo_025", filename: "festival_02.jpg", image_url: "https://images.unsplash.com/photo-1540555700478-4be289fbecef?w=600&auto=format&fit=crop&q=80", cluster_id: "celebration", manual_label: "Outdoor festival celebration lighting sparklers and diyas in pink and yellow ethnic kurti", attributes: { event: "celebration", location: "outdoor", traditional: true, sparklers: true, clothing_color: ["pink", "yellow"], people: "group" } },
  { image_id: "demo_026", filename: "festival_03.jpg", image_url: "https://images.unsplash.com/photo-1511795409834-ef04bbd61622?w=600&auto=format&fit=crop&q=80", cluster_id: "celebration", manual_label: "Formal indoor celebration with formal suits, sarees, and floral decorations", attributes: { event: "celebration", location: "indoors", traditional: true, people: "group" } },
  { image_id: "demo_027", filename: "festival_04.jpg", image_url: "https://images.unsplash.com/photo-1567157577867-05ccb1388e66?w=600&auto=format&fit=crop&q=80", cluster_id: "celebration", manual_label: "Festival sweets preparation indoors with yellow traditional dress and marigold flowers", attributes: { event: "celebration", location: "indoors", traditional: true, diyas_flowers: true, clothing_color: ["yellow"], people: "group" } },
  { image_id: "demo_028", filename: "wedding_02.jpg", image_url: "https://images.unsplash.com/photo-1465495976277-4387d4b0b4c6?w=600&auto=format&fit=crop&q=80", cluster_id: "celebration", manual_label: "Formal outdoor wedding party in garden with flower beds and formal attire", attributes: { event: "celebration", location: "outdoor", traditional: true, people: "group" } },
  { image_id: "demo_029", filename: "festival_05.jpg", image_url: "https://images.unsplash.com/photo-1577998474517-7eeeed4e448a?w=600&auto=format&fit=crop&q=80", cluster_id: "celebration", manual_label: "Family decorating entrance with marigold flowers and diyas for festival celebration", attributes: { event: "celebration", location: "outdoor", traditional: true, diyas_flowers: true, people: "family" } },
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
  // ALWAYS initialize a completely clean session state for every query!
  const session: FallbackSessionState = {
    sessionId,
    query,
    candidateIds: DEMO_PHOTOS.map(p => p.image_id),
    rejectedIds: [],
    round: 0,
    questionsAsked: [],
    history: [29],
  };
  activeSessions[sessionId] = session;

  const lower = query.toLowerCase();

  // Determine initial candidate pool based strictly on query terms
  let matching: DemoPhoto[] = [];
  if (lower.includes('birthday') || lower.includes('cake') || lower.includes('balloon')) {
    matching = DEMO_PHOTOS.filter(p => p.attributes.event === 'birthday');
  } else if (lower.includes('beach') || lower.includes('vacation') || lower.includes('ocean') || lower.includes('wave') || lower.includes('sea')) {
    matching = DEMO_PHOTOS.filter(p => p.attributes.event === 'vacation');
  } else if (lower.includes('festival') || lower.includes('traditional') || lower.includes('diwali') || lower.includes('wedding') || lower.includes('saree')) {
    matching = DEMO_PHOTOS.filter(p => p.attributes.event === 'celebration');
  } else if (lower.includes('park') || lower.includes('picnic') || lower.includes('frisbee') || lower.includes('dog') || lower.includes('grass')) {
    matching = DEMO_PHOTOS.filter(p => p.attributes.event === 'outdoor');
  } else {
    // Default subset matching query length
    matching = DEMO_PHOTOS.slice(0, 12);
  }

  session.candidateIds = matching.map(p => p.image_id);
  session.round = 1;
  const activeCount = matching.length;
  const reserveCount = 29 - activeCount;
  session.history = [29, activeCount];

  // Pick best discriminative question for the candidate pool
  let questionText = "Was this taken indoors or outdoors?";
  let options = ["Indoors", "Outdoors", "I don't remember"];
  let dimTested = "environment";
  let subKey = "environment:location";

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
  } else if (matching.every(p => p.attributes.event === 'outdoor')) {
    questionText = "Was there a dog or pet in the photo?";
    options = ["Dog present", "No dog", "I don't remember"];
    dimTested = "animals";
    subKey = "pets:dog";
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
  } else if (ansLower.includes('yes') || ansLower.includes('dog')) {
    const filtered = candidates.filter(p => p.attributes.cake || p.attributes.sparklers || p.attributes.diyas_flowers || p.attributes.balloons || p.attributes.dog);
    if (filtered.length > 0) candidates = filtered;
  }

  session.candidateIds = candidates.map(p => p.image_id);
  const activeCount = Math.max(3, candidates.length);
  session.history.push(activeCount);

  // Move to recognition phase when narrowed to 3-6 photos
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
  let session = activeSessions[sessionId];
  if (!session) {
    session = {
      sessionId,
      query: "beach photo",
      candidateIds: ["demo_009", "demo_010", "demo_011", "demo_012"],
      rejectedIds: [],
      round: 2,
      questionsAsked: ["Were you with a group?", "Was it outdoors?"],
      history: [29, 7, 4],
    };
    activeSessions[sessionId] = session;
  }

  if (payload.selectionType === 'found') {
    const targetId = payload.imageId || session.candidateIds[0] || "demo_009";
    const targetPhoto = DEMO_PHOTOS.find(p => p.image_id === targetId) || DEMO_PHOTOS[8];

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
    const refPhoto = DEMO_PHOTOS.find(p => p.image_id === payload.imageId);
    session.round += 1;
    const remaining = DEMO_PHOTOS.filter(p => p.cluster_id === (refPhoto?.cluster_id || 'vacation')).slice(0, 4);

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
      text: "Was this photo taken during the day or at sunset?",
      options: ["Daytime", "Sunset", "I don't remember"],
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
