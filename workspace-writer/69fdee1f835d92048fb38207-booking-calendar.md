# Demo Booking Calendar Integration

## Calendly/Booking Setup for Email 3: "Still thinking about flaky tests? Here's the fix"

### Integration Details

**Email Subject:** Still thinking about flaky tests? Here's the fix  
**Trigger:** Day 7 of Developer Community Nurture sequence  
**CTA:** Book a 15-minute personalized demo

---

### Booking Calendar Configuration

**Calendar Name:** Smoke Test Co Demo Request

**Meeting Template:** 15-Minute Demo Preview

---

### Pre-Configured Meeting Agenda Template

#### Agenda Overview
*Welcome! This 15-minute demo will show how engineering teams like yours reduce testing time by 60% and eliminate flaky tests forever.*

#### Section 1: False-Positive Reduction (5 minutes)
- **What we'll show:** Live demonstration of intelligent false-positive detection in action
- **Key benefit:** Eliminate 95% of flaky tests with real-time pattern recognition
- **Success metric:** From 50+ false positives per week to under 5 with our intelligent detection
- **Demo:** Show before/after comparison of test runs with and without our detection

#### Section 2: Quick Setup (5 minutes)
- **What we'll show:** One-click integration with your existing CI/CD pipeline
- **Key benefit:** Start testing in 10 minutes, not 10 weeks
- **Success metric:** GitHub/GitLab/Jenkins integration complete in under 15 minutes
- **Demo:** Walk through the integration wizard with your actual repository

#### Section 3: Transparent Pricing (5 minutes)
- **What we'll show:** Clear pricing tiers with no hidden costs
- **Key benefit:** Choose the plan that fits your team—upgrade or downgrade anytime
- **Success metric:** No surprise costs or enterprise complexity
- **Demo:** Show pricing calculator and team tier options

---

### 3 Prep Tips for Attendees

#### Tip #1: Come with Your Biggest Test Challenge
Think about the test that's been flakiest or most frustrating in your pipeline. Bring the test file or a description so we can show you exactly how our detection eliminates that specific problem.

#### Tip #2: Know Your CI/CD Stack
If you use GitHub Actions, GitLab CI, Jenkins, or another tool, be ready to mention it. We'll show how to integrate with your specific setup in under 15 minutes.

#### Tip #3: Share Your Team Size
Let us know how many engineers are involved in your testing workflow. This helps us recommend the right plan and show relevant features that scale with your team.

---

### Post-Booking Email Automation

**Trigger:** Booking confirmed  
**Delay:** Immediate  
**Subject:** Demo slot confirmed: Here's the link + prep tips  
**Content:** Calendar invite with agenda template and prep tips embedded

**Trigger:** 24 hours before demo  
**Subject:** Reminder: Your Smoke Test Co demo is tomorrow  
**Content:** Calendar reminder with link to agenda and prep tips

**Trigger:** After demo attendance  
**Subject:** Thanks for the demo—here's what's next  
**Content:** Summary of discussed features, next steps, and option to start free trial

---

### Analytics Tracking

- **Booking rate:** Track demo request form completions → calendar bookings
- **Show-up rate:** Track confirmed attendees vs. no-shows
- **Conversion rate:** Track demo attendees → free trial signups
- **Satisfaction score:** Post-demo survey (NPS-style)

---

### Integration Notes

- Calendly integration with demo request form (form:demo-request-form)
- Automatic calendar invite generation with agenda template
- CRM integration for lead scoring (demo_booked flag set to true)
- Email sequence automation for pre/post-demo communications
- Slack notification to sales team when high-scoring lead books demo