# Acme Corp Marketing Strategy - MVP

## Campaign
- **Name:** "Get Up and Running"
- **Objective:** Drive 500 qualified SMB signups in 90 days through targeted LinkedIn and email nurture campaigns.
- **Target Audience:** SMB owners (10-50 employees) in logistics, delivery, and field service operations who manage routes and inventory across multiple locations.
- **Positioning:** The only SaaS platform that gives enterprise-grade route optimization and inventory visibility without the enterprise price tag or complexity.
- **Key Messages:**
  1. "Cut operational costs by 25% in 90 days with AI-powered route optimization"
  2. "Real-time inventory tracking across all your locations, no enterprise setup required"
  3. "Join 500+ SMBs saving 10+ hours per week on logistics operations"
- **Primary Channel:** LinkedIn (40% of research time, highest trust signal for B2B SMB decisions)
- **Timeline:** 90 days, starting June 1, 2026

## Content Plan
1. **Type:** Blog Post
   - **Title:** "How SMBs Are Cutting Fuel Costs by 25% in 2026"
   - **Purpose:** Top-of-funnel awareness with specific ROI metrics
   - **Target Keywords:** ["SMB route optimization", "fuel cost reduction", "fleet management SMB"]
   - **Channel:** Company blog + LinkedIn distribution
   - **CallToAction:** "Calculate Your Savings"

2. **Type:** Blog Post
   - **Title:** "The Hidden Inventory Costs Killing Your Margins"
   - **Purpose:** Address fragmentation pain point, establish authority
   - **Target Keywords:** ["inventory management SMB", "warehouse optimization", "stock tracking"]
   - **Channel:** Company blog + email nurture
   - **CallToAction:** "Download Inventory Checklist"

3. **Type:** Case Study
   - **Title:** "CityDash: How a 30-Person Delivery Company Saved $47K/Year"
   - **Purpose:** Social proof with concrete ROI metrics
   - **Target Keywords:** ["delivery company case study", "SaaS ROI logistics"]
   - **Channel:** LinkedIn + sales emails
   - **CallToAction:** "See How We Can Help You"

4. **Type:** ROI Calculator (Interactive Tool)
   - **Title:** "Route Optimization Savings Calculator"
   - **Purpose:** Self-serve qualification with 90-day ROI projection
   - **Target Keywords:** ["fleet cost calculator", "SaaS ROI tool"]
   - **Channel:** Landing page + LinkedIn
   - **CallToAction:** "Get Your Custom Report"

5. **Type:** Webinar
   - **Title:** "SMB Route Optimization Masterclass: 10% Cost Cuts Without Hiring"
   - **Purpose:** Deep-dive nurture, demo with social proof
   - **Target Keywords:** ["logistics webinar", "route optimization training"]
   - **Channel:** LinkedIn + email sequence
   - **CallToAction:** "Reserve My Spot"

## Landing Pages
1. **Slug:** /smboptimization
   - **Headline:** "Cut Logistics Costs by 25% in 90 Days"
   - **Subheadline:** "AI-powered route optimization built specifically for growing SMBs. No enterprise complexity."
   - **Value Proposition:** "While other tools charge enterprise prices for enterprise features, we give you exactly what SMBs need: route optimization, inventory tracking, and delivery scheduling—all for the price of 2 software subscriptions."
   - **CTA:** "Start Free Trial"
   - **FormId:** form-main

2. **Slug:** /inventory-control
   - **Headline:** "Real-Time Inventory Across All Locations. Zero Setup."
   - **Subheadline:** "Stop losing money to stockouts and overstock. See inventory from your warehouse to your last-mile delivery."
   - **Value Proposition:** "Our platform connects all your locations in minutes—not weeks. No legacy system integration needed. Just scan, track, and optimize."
   - **CTA:** "See How It Works"
   - **FormId:** form-inventory

3. **Slug:** /calculator
   - **Headline:** "Calculate Your Potential Savings in 60 Seconds"
   - **Subheadline:** "Enter your current fleet size, routes, and fuel costs. Get a customized ROI projection."
   - **Value Proposition:** "Most SMBs leave 15-25% of potential savings on the table. Our calculator shows you exactly what you're missing—and how to capture it."
   - **CTA:** "Run Calculator"
   - **FormId:** form-calc

## Forms
1. **id:** form-main
   - **name:** "SMB Route Optimization Demo Request"
   - **purpose:** demo request
   - **fields:** ["email", "company_name", "employee_count", "current_fleet_size"]
   - **successAction:** trigger:demo-sequence

2. **id:** form-inventory
   - **name:** "Inventory Control Assessment"
   - **purpose:** content download
   - **fields:** ["email", "company_name", "number_locations"]
   - **successAction:** trigger:inventory-sequence

3. **id:** form-calc
   - **name:** "ROI Calculator Report"
   - **purpose:** content download
   - **fields:** ["email", "fleet_size", "avg_miles_per_day", "current_fuel_cost"]
   - **successAction:** redirect:/calculator-results

## Email Sequences
1. **name:** "Demo Nurturer"
   - **trigger:** form:form-main
   - **steps:**
     - { "delay": "immediate", "subject": "Quick question about your logistics stack", "purpose": "Engage and validate fit" }
     - { "delay": "2 days", "subject": "3 SMBs like you saved $47K/year—here's how", "purpose": "Social proof + pain validation" }
     - { "delay": "4 days", "subject": "The ROI calculator is ready for you", "purpose": "Self-serve qualification" }
     - { "delay": "7 days", "subject": "Webinar: Cut costs without hiring", "purpose": "Deep-dive education" }
     - { "delay": "10 days", "subject": "Last chance: 50% off for Q3 signups", "purpose": "Urgency + conversion" }

2. **name:** "Inventory Nurture"
   - **trigger:** form:form-inventory
   - **steps:**
     - { "delay": "immediate", "subject": "Your inventory checklist is attached", "purpose": "Deliver value immediately" }
     - { "delay": "3 days", "subject": "Common inventory mistakes (and how to fix them)", "purpose": "Education + authority" }
     - { "delay": "7 days", "subject": "Real inventory tracking: CityDash case study", "purpose": "Social proof" }
     - { "delay": "14 days", "subject": "Questions about inventory control? Chat with us", "purpose": "Support + conversion" }

3. **name:** "ROI Calculator Follow-up"
   - **trigger:** form:form-calc
   - **steps:**
     - { "delay": "immediate", "subject": "Your savings estimate: ${X} per year", "purpose": "Personalized ROI + urgency" }
     - { "delay": "2 days", "subject": "3 ways to capture that savings", "purpose": "Value reinforcement" }
     - { "delay": "5 days", "subject": "Free demo: See how it works with your data", "purpose": "Conversion" }

## Lead Rules
```json
{
  "scoringCriteria": [
    { "action": "Visited /smboptimization", "points": 10 },
    { "action": "Requested demo", "points": 20 },
    { "action": "Opened email", "points": 5 },
    { "action": "Clicked link in email", "points": 8 },
    { "action": "Downloaded checklist", "points": 12 },
    { "action": "Used ROI calculator", "points": 25 },
    { "action": "Registered for webinar", "points": 30 },
    { "action": "Booked demo", "points": 40 }
  ],
  "routingRules": [
    { "condition": "score >= 60 AND demo_booked == true", "action": "assign to AE" },
    { "condition": "score >= 40 AND employee_count > 20", "action": "trigger:mid-market-sequence" },
    { "condition": "score >= 25", "action": "trigger:nurture-sequence" }
  ]
}
```

## Sales Qualified Handoff
- **SQO Threshold:** "score >= 60 AND (demo_booked == true OR employee_count > 30)"
- **Handoff Process:**
  1. LeadOps triggers Slack alert in #sales-alerts with lead details
  2. AE receives notification with lead score, form data, and journey map
  3. AE reviews lead within 15 minutes (high-intent) or 2 hours (nurture)
  4. AE makes first call within 30 minutes for high-intent, 24 hours for nurture
  5. AE sends personalized Loom video within 1 hour showing how platform solves their specific use case
- **Notification Channel:** Slack #sales-alerts
- **Required Data:** ["email", "company_name", "employee_count", "use_case", "timeline", "budget_range"]
