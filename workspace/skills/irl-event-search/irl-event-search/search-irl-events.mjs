#!/usr/bin/env node

/**
 * IRL Event Search Script
 * 
 * Searches for in-real-life hobby events and saves them to the database
 * with rejection_reason tracking.
 */

const { MongoClient } = require('mongodb');

// Configuration
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017';
const DATABASE_NAME = process.env.DATABASE_NAME || 'personal';

// Search parameters from cron
const params = {
  search_type: process.argv[2] || 'daily', // daily, weekly, custom
  date_range: {
    start: process.argv[3] || new Date().toISOString().split('T')[0],
    end: process.argv[4] || (() => {
      const days = process.argv[2] === 'daily' ? 7 : 30;
      const end = new Date();
      end.setDate(end.getDate() + days);
      return end.toISOString().split('T')[0];
    })()
  },
  hobbies: process.argv[5]?.split(',') || ['mixology', 'cooking', 'photography'],
  language: process.argv[6] || 'auto'
};

// Known Spanish regions
const spanishRegions = [
  'America/Bogota',
  'America/Mexico_City',
  'America/Santiago',
  'America/Buenos_Aires',
  'America/Lima',
  'Europe/Madrid'
];

// Get current timezone
function getCurrentTimezone() {
  return process.argv[7] || 'America/Bogota';
}

// Determine if we should use Spanish searches
function isSpanishRegion() {
  const timezone = getCurrentTimezone();
  return spanishRegions.includes(timezone);
}

// Get search queries based on language
function getSearchQueries(hobby) {
  const isSpanish = isSpanishRegion();
  
  if (isSpanish) {
    return [
      `${hobby} bogota ${params.date_range.start} ${params.date_range.end} fecha precio`,
      `taller de ${hobby} bogota`,
      `curso de ${hobby} bogota`,
      `${hobby} bogota eventos`,
      `escuela de ${hobby} bogota`
    ];
  } else {
    return [
      `${hobby} workshop bogota ${params.date_range.start}`,
      `${hobby} course bogota ${params.date_range.start}`,
      `${hobby} class bogota ${params.date_range.start}`,
      `${hobby} bogota 2026`
    ];
  }
}

// Deduplicate results
function deduplicateResults(results) {
  const seen = new Map();
  const unique = [];
  
  for (const result of results) {
    const key = `${result.event_name}-${result.event_date}-${result.price}`;
    
    if (!seen.has(key)) {
      seen.set(key, true);
      unique.push(result);
    }
  }
  
  return unique;
}

// Classify event category
function classifyCategory(event) {
  const name = event.event_name?.toLowerCase() || '';
  
  if (name.includes('workshop')) return 'workshop';
  if (name.includes('class')) return 'class';
  if (name.includes('expo') || name.includes('fair')) return 'expo';
  if (name.includes('festival')) return 'festival';
  return 'other';
}

// Classify event priority
function classifyPriority(event) {
  const eventDate = new Date(event.event_date);
  const now = new Date();
  const daysUntil = Math.ceil((eventDate - now) / (1000 * 60 * 60 * 24));
  
  if (daysUntil <= 3) return 'high';
  if (daysUntil <= 14) return 'medium';
  return 'low';
}

// Calculate days until event
function calculateDaysUntil(eventDate) {
  const date = new Date(eventDate);
  const now = new Date();
  return Math.ceil((date - now) / (1000 * 60 * 60 * 24));
}

// Main search function
async function searchEvents() {
  const client = new MongoClient(MONGODB_URI);
  
  try {
    await client.connect();
    const db = client.db(DATABASE_NAME);
    
    console.log('='.repeat(60));
    console.log('IRL Event Search');
    console.log('='.repeat(60));
    console.log(`Search Type: ${params.search_type}`);
    console.log(`Date Range: ${params.date_range.start} to ${params.date_range.end}`);
    console.log(`Hobbies: ${params.hobbies.join(', ')}`);
    console.log(`Language: ${params.language} (${isSpanishRegion() ? 'Spanish' : 'English'})`);
    console.log('='.repeat(60));
    
    // Get active hobbies from database
    console.log('\nFetching active hobbies...');
    const hobbiesList = await db.collection('hobbies.global.hobbies_list').find({
      status: 'active',
      isTemplate: { $exists: false }
    }).toArray();

    const activeHobbyNames = hobbiesList.map(h => h.hobbyName);
    console.log('Active hobbies:', activeHobbyNames.join(', ') || '(none)');

    // Also include hobby pitches in testing phase
    const pitchesList = await db.collection('hobby_pitches').find({
      status: 'testing',
      isTemplate: { $exists: false }
    }).toArray();

    const testingHobbyNames = pitchesList.map(h => h.hobbyName);
    console.log('Testing pitches:', testingHobbyNames.join(', ') || '(none)');

    // Merge, deduplicate
    const hobbiesToSearch = [...new Set([...activeHobbyNames, ...testingHobbyNames])];
    
    let allEvents = [];
    
    // Search for each hobby
    for (const hobby of hobbiesToSearch) {
      console.log(`\nSearching for ${hobby} events...`);
      
      const queries = getSearchQueries(hobby);
      
      for (const query of queries) {
        console.log(`  Searching: ${query}`);
        
        try {
          const results = await db.collection('search_cache').findOne({
            query: query,
            date: params.date_range.start
          });
          
          if (results) {
            const events = results.events || [];
            allEvents.push(...events.map(e => ({
              ...e,
              source_platform: 'search_cache'
            })));
          }
        } catch (error) {
          console.log(`    Error: ${error.message}`);
        }
      }
    }
    
    // Deduplicate events
    console.log('\nDeduplicating events...');
    const uniqueEvents = deduplicateResults(allEvents);
    console.log(`Found ${uniqueEvents.length} unique events`);
    
    // Categorize events
    console.log('\nCategorizing events...');
    const categorizedEvents = uniqueEvents.map(event => ({
      hobby: event.hobby || 'unknown',
      event_name: event.event_name || 'Untitled',
      event_date: event.event_date || new Date().toISOString().split('T')[0],
      event_time: event.event_time || '',
      price: event.price || 0,
      currency: event.currency || 'COP',
      location: event.location || '',
      address: event.address || '',
      website: event.website || '',
      instructor: event.instructor || '',
      capacity: event.capacity || 0,
      registration_link: event.registration_link || '',
      materials_included: event.materials_included || false,
      source_platform: event.source_platform || 'unknown',
      research_date: new Date().toISOString().split('T')[0],
      category: classifyCategory(event),
      priority: classifyPriority(event),
      status: 'pending',
      rejection_reason: null,
      ttl_days: 14,
      expires_at: new Date(new Date(event.event_date).getTime() + 14 * 24 * 60 * 60 * 1000)
    }));
    
    // Check for previously pitched events
    console.log('\nChecking for previously pitched events...');
    const pitchedEvents = await db.collection('hobby_events').find({
      hobby: { $in: hobbiesToSearch },
      status: 'pending',
      event_date: {
        $gte: new Date(params.date_range.start),
        $lte: new Date(params.date_range.end)
      }
    }).toArray();
    
    const pitchedNames = new Set(pitchedEvents.map(e => e.event_name.toLowerCase()));
    
    // Mark duplicates
    for (const event of categorizedEvents) {
      const existing = pitchedEvents.find(e => 
        e.event_name?.toLowerCase() === event.event_name?.toLowerCase() &&
        e.event_date === event.event_date
      );
      
      if (existing) {
        event.status = 'duplicate';
        event.rejection_reason = 'Already pitched on ' + existing.research_date;
      }
    }
    
    // Save new events to database
    console.log('\nSaving events to database...');
    const insertedCount = 0;
    
    for (const event of categorizedEvents) {
      const exists = await db.collection('hobby_events').findOne({
        hobby: event.hobby,
        event_name: event.event_name,
        event_date: event.event_date
      });
      
      if (!exists) {
        await db.collection('hobby_events').insertOne(event);
        insertedCount++;
      }
    }
    
    console.log(`Inserted ${insertedCount} new events`);
    
    // Generate report
    console.log('\nGenerating report...');
    const report = {
      search_type: params.search_type,
      date_range: params.date_range,
      search_date: new Date().toISOString().split('T')[0],
      total_events_found: uniqueEvents.length,
      new_events: insertedCount,
      duplicate_events: uniqueEvents.filter(e => e.status === 'duplicate').length,
      events_by_hobby: {},
      events_by_status: {},
      events_by_category: {},
      recommendations: []
    };
    
    for (const event of categorizedEvents) {
      if (!report.events_by_hobby[event.hobby]) {
        report.events_by_hobby[event.hobby] = 0;
      }
      report.events_by_hobby[event.hobby]++;
      
      if (!report.events_by_status[event.status]) {
        report.events_by_status[event.status] = 0;
      }
      report.events_by_status[event.status]++;
      
      if (!report.events_by_category[event.category]) {
        report.events_by_category[event.category] = 0;
      }
      report.events_by_category[event.category]++;
    }
    
    console.log(JSON.stringify(report, null, 2));
    
    // Generate notification message
    console.log('\nGenerating notification...');
    const notification = `IRL Event Search Results\n\n` +
      `- Search Type: ${params.search_type}\n` +
      `- Date Range: ${params.date_range.start} to ${params.date_range.end}\n` +
      `- Total Events Found: ${uniqueEvents.length}\n` +
      `- New Events: ${insertedCount}\n` +
      `- Duplicates: ${uniqueEvents.filter(e => e.status === 'duplicate').length}\n\n` +
      'Top Opportunities:\n';
    
    const topEvents = categorizedEvents
      .filter(e => e.status === 'pending')
      .sort((a, b) => a.event_date.localeCompare(b.event_date))
      .slice(0, 5);
    
    for (const event of topEvents) {
      notification += `- ${event.event_name} (${event.event_date}): ${event.price} ${event.currency}\n`;
    }
    
    console.log(notification);
    
    console.log('\nIRL Event Search completed!');
    console.log('Results saved to: ' + DATABASE_NAME + '.hobby_events');
    
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  } finally {
    await client.close();
  }
}

// Run the search
searchEvents();
