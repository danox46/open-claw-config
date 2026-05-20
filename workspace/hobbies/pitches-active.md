# Hobby Pitches - Active Testing

Hobbies you're testing before committing to full tracking. Each pitch includes a status and next steps.

## Current Pitches

### 1. Mixology
- **Status:** Testing
- **Start Date:** May 10, 2026
- **Purpose:** Learning mixology basics, experimenting with classic and modern cocktails
- **Progress:** 0/3 next steps completed
- **Next Steps:** 
  - [ ] Complete beginner mixology course (target: 1-2 weeks)
  - [ ] Purchase basic bar equipment (shaker, jigger, muddler, basic glassware)
  - [ ] Try 5 different cocktail recipes (mix classic + modern)
- **Conversion Criteria Status:**
  - **Consistency:** Pending (need 2+ drinks/week for 2 weeks)
  - **Commitment:** Pending (equipment purchase decision)
  - **Time:** Pending (schedule 30-60 min sessions)
- **Notes:** Learning mixology basics, experimenting with classic and modern cocktails
- **Decision:** Wait 2-3 weeks after course completion before approving

### 2. Acting
- **Status:** Testing
- **Start Date:** May 10, 2026
- **Purpose:** Acting classes, exploring theater (stage and film)
- **Progress:** 0/3 next steps completed
- **Next Steps:**
  - [ ] Find local acting classes/workshops
  - [ ] Attend community theater as audience member
  - [ ] Consider improv classes
- **Conversion Criteria Status:**
  - **Consistency:** Pending (need 1 class/session/week for 2 weeks)
  - **Commitment:** Pending (class enrollment + potential audition)
  - **Time:** Pending (schedule 2-4 hour sessions)
- **Notes:** Acting classes, exploring theater (stage and film)
- **Decision:** Need to find classes first before approving - low barrier entry (just attend 1 class as test)

## Progress Summary

| Pitch | Days Active | Next Steps Done | Events Attended | Progress % |
|-------|-------------|-----------------|-----------------|------------|
| Mixology | 9 | 0/3 | 0 | 0% |
| Acting | 9 | 0/3 | 0 | 0% |

## Conversion Criteria

A hobby pitch converts to full tracking when:

### ✅ Mixology - Conversion Requirements:
- **Consistency:** Mix 2+ cocktails per week for 2 weeks
- **Commitment:** Purchase basic bar equipment ($50-100)
- **Time:** Schedule 30-60 min sessions 2x/week
- **Duration:** Maintain for 2+ weeks
- **Conversion Trigger:** After completing 5 recipes + equipment purchase

### ✅ Acting - Conversion Requirements:
- **Consistency:** Attend 1 class/session per week for 2 weeks
- **Commitment:** Enroll in class (tuition varies)
- **Time:** Schedule 2-4 hour sessions 1x/week
- **Duration:** Attend for 2+ weeks
- **Conversion Trigger:** After attending 2 classes + feeling engaged

## Database Schema

### hobby_pitches Collection
```json
{
  "hobbyName": "string",
  "status": "suggested|testing|approved|rejected",
  "startDate": "YYYY-MM-DD",
  "notes": "string",
  "nextSteps": ["string"],
  "conversionCriteria": {
    "consistency": "boolean",
    "commitment": "boolean",
    "time": "boolean"
  },
  "convertedDate": "YYYY-MM-DD",
  "convertedTo": "hobbyName (if converted)"
}
```

---

**Last Updated:** May 19, 2026 (2:56 PM)
**Maintained By:** Tensoon
**Review Date:** May 26, 2026 (1-week check-in)
