# Frontend Changes - Timezone Display Feature

## Overview
Added a timezone selection feature that allows users to view message timestamps in either their local timezone or UTC. The preference is persisted in browser localStorage.

## Changes Made

### 1. HTML (index.html)
**Location**: Lines 22-29

Added a timezone toggle control in the sidebar:
```html
<!-- Timezone Toggle -->
<div class="timezone-toggle">
    <label for="timezoneSelect">Timezone:</label>
    <select id="timezoneSelect">
        <option value="local">Local Time</option>
        <option value="utc">UTC</option>
    </select>
</div>
```

- Positioned at the top of the sidebar, above the "NEW CHAT" button
- Dropdown with two options: "Local Time" and "UTC"
- Easy access for users to switch timezone preference

### 2. CSS (style.css)
**Location**: Lines 605-644

Added styling for the timezone toggle and message timestamps:

**Timezone Toggle Styles**:
- Flex container with border and background styling
- Label with uppercase styling matching sidebar design
- Dropdown styled with hover and focus states
- Consistent with existing UI color scheme

**Message Timestamp Styles** (Lines 221-228):
- `.message-timestamp` class for displaying time information
- Subtle styling with reduced opacity
- Positioned below message content

### 3. JavaScript (script.js)

#### Global State (Lines 1-9)
- Added `currentTimezone` variable to track current timezone preference ('local' or 'utc')
- Added `timezoneSelect` DOM element reference

#### Initialization (Lines 11-31)
- Retrieves timezone selector from DOM
- Restores user's timezone preference from localStorage on page load
- Updates the dropdown to reflect saved preference

#### Event Listeners (Lines 41-47)
- Added timezone selector change listener
- Saves preference to localStorage when changed
- Calls `updateAllMessageTimestamps()` to refresh all existing messages

#### New Functions

**formatTimestamp(date, timezone)** (Lines 156-181):
- Formats dates using `Intl.DateTimeFormat` for localization
- Supports both local and UTC timezones
- Returns formatted string with timezone indicator (e.g., "12/31/2025, 03:45:30 PM Local")
- Uses 12-hour format with AM/PM

**updateAllMessageTimestamps()** (Lines 227-237):
- Updates all message timestamps when timezone preference changes
- Queries all `.message` elements
- Recalculates timestamps using stored ISO strings and new timezone preference
- Updates DOM in real-time

#### Modified addMessage() Function (Lines 183-225)
- Added `messageDiv.dataset.timestamp` to store ISO timestamp
- Generates formatted timestamp using `formatTimestamp()`
- Inserts timestamp below message content
- Preserves all existing functionality (markdown, sources, etc.)

## Features

1. **Timezone Toggle**: Users can switch between Local Time and UTC using dropdown in sidebar
2. **Persistent Preference**: Selected timezone is saved in browser's localStorage
3. **Real-time Updates**: When timezone is changed, all displayed messages update immediately
4. **Current Time**: Each message shows the exact time it was sent
5. **Clear Indicators**: Timestamps clearly indicate which timezone is displayed

## User Experience

- **Default**: Shows local timezone on first visit
- **Persistence**: Remembers user's choice across browser sessions
- **Responsive**: Timestamps update instantly when timezone preference changes
- **Accessible**: Dropdown is keyboard navigable with proper focus styling

## Technical Details

- Uses browser's `Intl.DateTimeFormat` API for timezone formatting
- Stores original timestamp in ISO format for accurate recalculation
- No external dependencies required
- localStorage key: `preferredTimezone`

## Files Modified

1. `frontend/index.html` - Added timezone control markup
2. `frontend/style.css` - Added styling for timezone toggle and timestamps
3. `frontend/script.js` - Added timezone logic, state management, and timestamp formatting

## Testing Recommendations

1. Send a message and verify timestamp appears
2. Switch timezone dropdown and verify all messages update
3. Refresh page and verify timezone preference persists
4. Test with different browser local timezones if possible
5. Verify timestamps are accurate (compare with system time)
