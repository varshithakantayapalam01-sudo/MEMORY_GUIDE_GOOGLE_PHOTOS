# Memory Guide — Demo Dataset Plan

---

## Design Principle

The demo photo library must create **deliberate ambiguity**. If a vague query like "birthday photo" or "old childhood photo" immediately narrows to one image, the adaptive questioning mechanism has nothing to prove.

The dataset must ensure that:
- Multiple images match any reasonable vague description.
- Attribute dimensions vary across matching images, creating opportunities for discriminative questions.
- The refinement loop is necessary, not cosmetic.

---

## Dataset Size

**Target: 55–65 images.**

Rationale:
- Large enough that a vague query returns 15–25 initial candidates.
- Small enough that the VLM can index all images affordably.
- Small enough for in-memory storage with no performance concerns.
- Large enough that ambiguity is real, not artificial.

---

## Ambiguity Clusters

Images are organized into **overlapping clusters** — groups of images that share key attributes but differ on others. A vague query will typically match an entire cluster. The system's job is to use discriminative questions to narrow within the cluster.

Each image belongs to **2–3 clusters**, creating cross-cluster ambiguity.

### Cluster Overview

| Cluster | Size | Shared Attributes | Varying Attributes |
|---------|------|-------------------|--------------------|
| A. Birthdays | 8 | cake, celebration, decorations | setting, age group, people count, clothing, indoor/outdoor |
| B. Family Gatherings | 7 | multiple people, family, home | occasion, clothing formality, food, time of day |
| C. Travel / Outdoors | 8 | outdoor, travel, scenic | location type, people count, activity, time of day |
| D. Children Photos | 7 | child present | setting, activity, occasion, clothing, companions |
| E. Festivals & Traditions | 6 | traditional clothing, decorations, celebration | specific festival, setting, people count, food |
| F. Food & Dining | 5 | food visible, eating/dining | setting type, formality, people count, cuisine |
| G. Pet Photos | 5 | animal present | animal type, setting, activity, people present |
| H. Group/Friends Photos | 5 | 3+ people, social | setting, occasion, activity, age group |
| I. Selfies & Portraits | 4 | 1 person, close framing | setting, clothing, mood, occasion |

**Total: ~55 images** (some images belong to multiple clusters).

---

## Cluster Details

### Cluster A: Birthdays (8 images)

These all match "birthday photo" or "photo with cake" — the system must ask the right questions to narrow.

| ID | Description | Setting | People | Age | Clothing | Distinguishing Feature |
|----|------------|---------|--------|-----|----------|----------------------|
| A1 | Child (girl, ~5) cutting cake indoors, pink frock, adult woman in blue sari beside her | indoor / home | 2 | child + adult | pink frock, blue sari | pink frock, 2 people, home |
| A2 | Child (girl, ~5) blowing candles indoors, yellow dress, 3 children around table | indoor / home | 4 | children | yellow dress | group of children, yellow |
| A3 | Child (boy, ~8) cutting cake outdoors in garden, blue t-shirt, parents behind | outdoor / garden | 3 | child + adults | blue t-shirt | boy, outdoor, garden |
| A4 | Teen girl cutting cake at restaurant, friends around, casual wear | indoor / restaurant | 5 | teens | casual / jeans | restaurant, teens, friends |
| A5 | Adult woman blowing candles at home, small cake, partner beside her, dim lighting | indoor / home | 2 | adults | casual / sweater | adults, dim/romantic, small cake |
| A6 | Child (girl, ~5) with cake outdoors in park, pink dress, balloons, solo | outdoor / park | 1 | child | pink dress | solo child, park, outdoors |
| A7 | Elderly person cutting cake at home, large family gathered | indoor / home | 6+ | elderly + mixed | formal / traditional | elderly, large group |
| A8 | Child (boy, ~3) with face covered in cake, messy, indoors, laughing | indoor / home | 1 | toddler | bib / messy | toddler, cake smash, messy |

**Why this works**: Querying "childhood birthday photo with cake" matches A1, A2, A3, A6, A8. The system must ask about indoor/outdoor (splits A1,A2,A8 vs A3,A6), then people count, then clothing color to converge.

**Key ambiguity pairs**:
- A1 vs A6: Same girl, same pink dress, both have cake — but indoor vs outdoor, 2 people vs 1.
- A2 vs A8: Both indoor child birthdays — but group vs solo, posed vs candid.
- A3 vs A6: Both outdoor child birthdays — but boy vs girl, garden vs park, group vs solo.

---

### Cluster B: Family Gatherings (7 images)

Match "family photo at home" or "group photo during celebration."

| ID | Description | Setting | People | Occasion | Clothing | Distinguishing Feature |
|----|------------|---------|--------|----------|----------|----------------------|
| B1 | Family of 4 posing at home during Diwali, traditional clothing, diyas visible | indoor / home | 4 | Diwali | traditional / sari, kurta | diyas, rangoli |
| B2 | Family of 4 posing at home during Christmas, sweaters, tree in background | indoor / home | 4 | Christmas | casual / sweaters | Christmas tree, sweaters |
| B3 | Family of 5 at dining table, home, casual dinner, no decorations | indoor / home | 5 | casual dinner | casual | plain dinner, no occasion |
| B4 | Family at home during Holi, colored faces, outdoor courtyard | outdoor / home courtyard | 5 | Holi | white (stained with color) | colored powder, messy |
| B5 | Three generations at home, formal photo, anniversary celebration | indoor / home | 7+ | anniversary | formal / sari, suit | formal, elderly couple centered |
| B6 | Family picnic in park, blanket on grass, food containers | outdoor / park | 4 | casual picnic | casual / sportswear | picnic blanket, park |
| B7 | Family at home for birthday (overlaps cluster A), decorations | indoor / home | 5 | birthday | mixed | overlaps with birthday cluster |

**Key ambiguity pairs**:
- B1 vs B2: Both family of 4 at home, both festive — but Diwali vs Christmas, traditional vs casual.
- B3 vs B5: Both family at home dining — but casual vs formal, small vs large group.
- B4 vs B6: Both outdoor family — but Holi (colorful/messy) vs picnic (relaxed).

---

### Cluster C: Travel / Outdoors (8 images)

Match "travel photo" or "outdoor photo" or "vacation picture."

| ID | Description | Setting | People | Location | Activity | Distinguishing Feature |
|----|------------|---------|--------|----------|----------|----------------------|
| C1 | Couple at beach, sunset, standing near water | outdoor / beach | 2 | beach / Goa | posing | sunset, couple, water |
| C2 | Family at beach, daytime, kids playing in sand | outdoor / beach | 4 | beach | playing | daytime, children, sand |
| C3 | Solo hiker on mountain trail, backpack, misty | outdoor / mountain | 1 | mountain | hiking | solo, misty, backpack |
| C4 | Group of friends at mountain viewpoint, sunny, posing | outdoor / mountain | 4 | mountain | posing | friends, sunny, viewpoint |
| C5 | Couple at historical monument, posing, daytime | outdoor / monument | 2 | city / monument | posing/sightseeing | monument, architecture |
| C6 | Solo person at lake, sitting on rocks, contemplative | outdoor / lake | 1 | lake / nature | sitting | solo, calm, lake |
| C7 | Family at waterfall, everyone getting splashed | outdoor / waterfall | 4 | waterfall | playing | waterfall, wet, splashing |
| C8 | Two friends at street market, colorful stalls, shopping | outdoor / street | 2 | city / market | shopping | market, colorful, street |

**Key ambiguity pairs**:
- C1 vs C2: Both beach — but sunset/couple vs daytime/family.
- C3 vs C4: Both mountain — but solo/misty vs group/sunny.
- C3 vs C6: Both solo outdoors in nature — but mountain/hiking vs lake/sitting.
- C5 vs C8: Both urban outdoor — but monument/posing vs market/shopping.

---

### Cluster D: Children Photos (7 images)

Match "old photo of me as a kid" or "childhood photo." Overlaps heavily with clusters A and B.

| ID | Description | Setting | Activity | Companions | Distinguishing Feature |
|----|------------|---------|----------|------------|----------------------|
| D1 | Child drawing at a desk, home, concentrated | indoor / home | studying/drawing | solo | art supplies, focused |
| D2 | Child in school uniform, posing at school gate | outdoor / school | posing | solo | school uniform, gate |
| D3 | Child playing with dog in garden | outdoor / garden | playing | dog | dog, garden |
| D4 | Child in traditional clothing at temple, holding flowers | outdoor / temple | praying/visiting | adult (parent) | temple, flowers, traditional |
| D5 | Two children on a swing in park | outdoor / park | playing | sibling | swing, park |
| D6 | Child sleeping on sofa, candid, blanket | indoor / home | sleeping | solo | candid, sleeping, cozy |
| D7 | Child at swimming pool, flotation ring, splashing | outdoor / pool | swimming | other children | pool, water, flotation ring |

*Note: A1, A2, A3, A6, A8 from the birthday cluster also match "childhood photo," creating 12 total candidates for that query.*

**Key ambiguity pairs**:
- D1 vs D6: Both indoor, solo child at home — but active/drawing vs passive/sleeping.
- D2 vs D4: Both outdoor with child — but school vs temple, uniform vs traditional.
- D3 vs D5: Both outdoor play — but solo+dog vs two children, garden vs park.

---

### Cluster E: Festivals & Traditions (6 images)

Match "festival photo" or "photo in traditional clothes." Overlaps with cluster B.

| ID | Description | Setting | Festival | People | Distinguishing Feature |
|----|------------|---------|----------|--------|----------------------|
| E1 | Woman lighting diyas at home entrance, evening, sari | outdoor / home entrance | Diwali | 1 | diyas, evening, solo |
| E2 | Group performing puja at home, flowers, incense | indoor / home | puja/prayer | 4 | incense, flowers, devotional |
| E3 | Children with sparklers at night, Diwali, laughing | outdoor / terrace | Diwali | 3 | sparklers, night, children |
| E4 | Family at Ganesh mandal, outdoor, crowded | outdoor / street | Ganesh Chaturthi | 5+ | idol, crowd, street |
| E5 | Women applying mehndi, sitting indoors, close-up of hands | indoor / home | wedding prep / Karva Chauth | 3 | mehndi, hands close-up |
| E6 | Man and child flying kite on terrace, sunny | outdoor / terrace | Makar Sankranti | 2 | kite, terrace, sunny |

**Key ambiguity pairs**:
- E1 vs E3: Both Diwali — but solo/diyas vs children/sparklers, entrance vs terrace.
- B1 vs E1 vs E3: All Diwali-related — different compositions and people.
- E2 vs E4: Both religious — but indoor/intimate vs outdoor/crowded.

---

### Cluster F: Food & Dining (5 images)

Match "photo at restaurant" or "food photo" or "dinner photo."

| ID | Description | Setting | People | Formality | Distinguishing Feature |
|----|------------|---------|--------|-----------|----------------------|
| F1 | Couple at fancy restaurant, candlelit, wine glasses | indoor / restaurant | 2 | formal | candlelight, wine, date night |
| F2 | Friends at street food stall, casual, standing, night | outdoor / street | 3 | casual | street food, standing, night |
| F3 | Family cooking together in kitchen, messy counter | indoor / home kitchen | 3 | casual | cooking, messy, kitchen |
| F4 | Group at cafe, laptops and coffee, daytime | indoor / cafe | 4 | casual | laptops, cafe, working |
| F5 | Birthday dinner at restaurant (overlaps A4) | indoor / restaurant | 5 | casual | overlaps with birthday |

**Key ambiguity pairs**:
- F1 vs F5: Both restaurant — but romantic/2 people vs group/birthday.
- F2 vs F4: Both casual eating — but outdoor/night vs indoor/daytime.

---

### Cluster G: Pet Photos (5 images)

Match "photo of my dog" or "photo with pet."

| ID | Description | Setting | Animal | People | Distinguishing Feature |
|----|------------|---------|--------|--------|----------------------|
| G1 | Dog (golden retriever) in park, fetching ball | outdoor / park | dog | 0 visible | park, active, ball |
| G2 | Dog (golden retriever) sleeping on couch at home | indoor / home | dog | 0 visible | sleeping, couch, indoor |
| G3 | Person training dog in hallway, dog sitting | indoor / hallway | dog | 1 | training, hallway |
| G4 | Cat sitting on windowsill, sunlight, indoor | indoor / home | cat | 0 visible | cat, windowsill, sunlight |
| G5 | Child with dog at beach, running | outdoor / beach | dog | 1 (child) | beach, running, child+dog |

*Note: D3 (child playing with dog in garden) also matches "pet photo."*

**Key ambiguity pairs**:
- G1 vs G2: Same dog breed — but park/active vs home/sleeping.
- G1 vs G5: Both outdoor with dog — but solo dog/park vs child+dog/beach.
- G3 vs D3: Both person with dog — but hallway/training vs garden/playing.

---

### Cluster H: Group/Friends Photos (5 images)

Match "group photo with friends" or "photo with college friends."

| ID | Description | Setting | People | Occasion | Distinguishing Feature |
|----|------------|---------|--------|----------|----------------------|
| H1 | Friends posing at college campus, casual | outdoor / campus | 5 | casual | campus, young adults |
| H2 | Friends at house party, dim lighting, drinks | indoor / home | 6 | party | dim, party, drinks |
| H3 | Colleagues at office event, semi-formal | indoor / office | 5 | work event | office, semi-formal |
| H4 | Friends at concert/event, loud, colorful lighting | indoor / venue | 4 | concert | concert, stage lights |
| H5 | Friends at graduation, robes, outdoor | outdoor / campus | 4 | graduation | robes, caps, formal |

**Key ambiguity pairs**:
- H1 vs H5: Both outdoor campus with friends — but casual vs graduation.
- H2 vs H4: Both indoor social — but house/dim vs venue/colorful.
- H3 vs H4: Both indoor group events — but office/formal vs concert/casual.

---

### Cluster I: Selfies & Portraits (4 images)

Match "selfie" or "photo of me at..."

| ID | Description | Setting | Clothing | Mood | Distinguishing Feature |
|----|------------|---------|----------|------|----------------------|
| I1 | Selfie at famous landmark, sunglasses, daytime | outdoor / monument | casual / sunglasses | happy | landmark, tourist |
| I2 | Selfie with friend at cafe, coffee cups visible | indoor / cafe | casual | happy | cafe, friend, coffee |
| I3 | Portrait in traditional outfit, studio-like background | indoor / studio | traditional / lehenga | posed/serious | traditional, formal portrait |
| I4 | Selfie at sunset, beach, golden light | outdoor / beach | casual / swimwear | happy/romantic | sunset, beach, golden |

---

## Cross-Cluster Ambiguity Map

This table shows which images create ambiguity when a user provides a common vague query.

| Vague Query | Matching Images | Clusters | Ambiguity Size |
|-------------|----------------|----------|----------------|
| "birthday photo" | A1–A8, B7, F5 | A, B, F | 10 |
| "childhood photo" | A1, A2, A3, A6, A8, D1–D7, E3, E6 | A, D, E | 12–14 |
| "photo at home" | A1, A2, A5, A7, A8, B1–B3, B5, D1, D6, E2, F3, G2, G3, G4 | A, B, D, E, F, G | 15+ |
| "family photo" | B1–B7, C2, C7, E2, E4 | B, C, E | 10+ |
| "photo with dog" | D3, G1, G2, G3, G5 | D, G | 5 |
| "travel photo" | C1–C8, I1, I4 | C, I | 10 |
| "outdoor photo" | A3, A6, B4, B6, C1–C8, D2–D5, D7, E1, E3, E4, E6, F2, G1, G5, H1, H5, I1, I4 | Many | 20+ |
| "photo with cake" | A1–A8, B7, F5 | A, B, F | 10 |
| "festival photo" | B1, B4, E1–E6 | B, E | 8 |
| "photo in pink dress" | A1, A6 | A | 2 (tight) |
| "restaurant photo" | A4, F1, F5 | A, F | 3 |
| "photo in traditional clothes" | B1, D4, E1, E2, E5, I3 | B, D, E, I | 6 |
| "photo with friends" | A4, C4, C8, F2, F4, H1–H5, I2 | A, C, F, H, I | 10+ |
| "beach photo" | C1, C2, G5, I4 | C, G, I | 4 |
| "school photo" | D2 | D | 1 (unique) |
| "group celebration" | A4, A7, B1–B5, B7, E4, H2, H5 | A, B, E, H | 10+ |

---

## Deliberate Confuser Pairs

These are image pairs specifically designed to be hard to distinguish without the right clarifying question.

| Pair | Shared Attributes | Distinguishing Dimension | Ideal Question |
|------|------------------|--------------------------|----------------|
| A1 vs A6 | child, pink dress, cake, birthday | setting (indoor vs outdoor), people count (2 vs 1) | "Was this indoors or outdoors?" |
| A2 vs A8 | indoor, child, birthday, cake, home | people count (4 vs 1), mood (posed vs candid/messy) | "Were other children in the photo?" |
| C1 vs C2 | beach, outdoor | time of day (sunset vs daytime), people (couple vs family with kids) | "Was this during the day or at sunset?" |
| C3 vs C4 | mountain, outdoor | people count (solo vs group) | "Were you alone or with others?" |
| G1 vs G2 | same dog breed | setting (outdoor/park vs indoor/home) | "Was the dog indoors or outdoors?" |
| B1 vs B2 | family of 4, home, festive | occasion (Diwali vs Christmas), clothing (traditional vs casual) | "Were people wearing traditional clothing?" |
| E1 vs E3 | Diwali, outdoor | people (solo vs children), objects (diyas vs sparklers) | "Were there children in this photo?" |
| D1 vs D6 | indoor, solo child, home | activity (drawing vs sleeping) | "What was the child doing?" |
| H1 vs H5 | outdoor, campus, friends | occasion (casual vs graduation), clothing (casual vs robes) | "Was this for a special event like graduation?" |
| F1 vs F5 | indoor, restaurant, dining | people count (2 vs 5), occasion (date vs birthday) | "Was this a dinner for two or a larger group?" |

---

## Test Scenarios

Each test scenario simulates a real user trying to find a specific target photo using a vague initial query. The "expected path" shows how the adaptive questioning should guide the user.

### Scenario 1: "Old childhood birthday photo"
- **Target**: A1 (girl, pink frock, cutting cake, indoor, 2 people)
- **Initial candidates**: A1, A2, A3, A6, A8 (+ possibly D-cluster images)
- **Expected question path**:
  1. "Was this indoors or outdoors?" → indoor (eliminates A3, A6)
  2. "Were you alone in the photo or was someone with you?" → someone with me (eliminates A8)
  3. Show A1 and A2 → user recognizes A1

### Scenario 2: "That beach photo from vacation"
- **Target**: C1 (couple at sunset)
- **Initial candidates**: C1, C2, G5, I4
- **Expected question path**:
  1. "Was this during the day or closer to sunset?" → sunset (eliminates C2, G5)
  2. Show C1 and I4 → user recognizes C1

### Scenario 3: "Family photo during a festival"
- **Target**: B1 (Diwali, family of 4, traditional clothing)
- **Initial candidates**: B1, B2, B4, E1, E2, E3, E4
- **Expected question path**:
  1. "Was everyone wearing traditional or festive clothing?" → yes, traditional (eliminates B2, B4, E3)
  2. "Was this indoors or outdoors?" → indoor (eliminates E1, E4)
  3. Show B1 and E2 → user recognizes B1

### Scenario 4: "Photo of my dog"
- **Target**: G3 (person training dog in hallway)
- **Initial candidates**: D3, G1, G2, G3, G5
- **Expected question path**:
  1. "Was this indoors or outdoors?" → indoor (eliminates D3, G1, G5)
  2. Show G2 and G3 → user recognizes G3

### Scenario 5: "Group photo with college friends"
- **Target**: H5 (graduation)
- **Initial candidates**: H1, H2, H3, H4, H5, C4
- **Expected question path**:
  1. "Was this indoors or outdoors?" → outdoor (eliminates H2, H3, H4)
  2. "Was this for a special event or just a regular day?" → special event, graduation (eliminates H1, C4)
  3. Show H5 → user confirms

### Scenario 6: "Photo of me in traditional clothes" (harder — user is vague)
- **Target**: I3 (portrait in traditional outfit, studio)
- **Initial candidates**: B1, D4, E1, E2, E5, I3
- **Expected question path**:
  1. "Were there other people in this photo?" → no, just me (eliminates B1, E2, E5)
  2. "Was this outdoors or indoors?" → indoor (eliminates D4, E1)
  3. Show I3 → user confirms

---

## Image Sourcing Strategy

For the MVP demo, images can be sourced from:

1. **AI-generated images** (preferred for MVP). Use an image generation model to create photos matching each description. This avoids privacy/copyright issues and gives precise control over attributes.
2. **Royalty-free stock photos**. Source from Unsplash, Pexels, or Pixabay — select images that closely match each description.
3. **Team-provided personal photos** (with consent). If testers are willing to provide a small set of their own photos, this creates the most authentic test conditions.

### Recommendation for MVP

Use **AI-generated images** for the initial build and development. This guarantees the attribute profiles are accurate (we control exactly what's in each image) and avoids sourcing delays.

When doing user testing, optionally allow testers to **upload their own photos** alongside the demo set, or replace the demo set entirely. This tests whether the system works with real photos where VLM extraction may be less clean.

---

## Dataset Validation Checklist

Before considering the dataset complete, verify:

- [ ] At least 5 vague queries each produce 8+ initial candidates.
- [ ] Every cluster has at least one confuser pair requiring 2+ questions to resolve.
- [ ] No single image is the only match for more than one common query pattern.
- [ ] The `setting` dimension splits candidates roughly evenly across the full library (~50/50 indoor/outdoor).
- [ ] The `people_count` dimension varies meaningfully (mix of solo, pairs, groups).
- [ ] At least 3 images share the same `occasion` value (e.g., multiple birthdays, multiple festivals).
- [ ] At least 2 images share clothing color + setting, forcing deeper discrimination.
- [ ] All 6 test scenarios can be walked through and produce the expected narrowing.
- [ ] No scenario is solvable in 0 questions (initial query alone is never sufficient).

---

*This dataset plan is designed to stress-test the adaptive questioning mechanism. Images should be sourced/generated before implementation begins. Attribute profiles can be authored manually alongside the images or generated via VLM and then validated.*
