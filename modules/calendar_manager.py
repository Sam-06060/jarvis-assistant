import subprocess
from datetime import datetime, timedelta
from dateutil import parser
import re

class CalendarManager:
    """Manage macOS Calendar via AppleScript"""
    
    def __init__(self):
        pass
    
    def get_todays_events(self):
        """Get today's calendar events"""
        try:
            script = '''
            tell application "Calendar"
                set todayStart to current date
                set time of todayStart to 0
                set todayEnd to todayStart + (24 * 60 * 60)
                
                set eventsList to ""
                repeat with cal in calendars
                    set calEvents to (every event of cal whose start date ≥ todayStart and start date < todayEnd)
                    repeat with evt in calEvents
                        set eventInfo to (summary of evt) & "|" & (start date of evt as string) & "|" & (end date of evt as string)
                        set eventsList to eventsList & eventInfo & "||"
                    end repeat
                end repeat
                return eventsList
            end tell
            '''
            
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return self._parse_events(result.stdout.strip())
            return "No events scheduled for today."
            
        except Exception as e:
            return f"Could not access calendar: {str(e)}"
    
    def get_upcoming_events(self, days=7):
        """Get events for next N days"""
        try:
            script = f'''
            tell application "Calendar"
                set startDate to current date
                set time of startDate to 0
                set endDate to startDate + ({days} * 24 * 60 * 60)
                
                set eventsList to ""
                repeat with cal in calendars
                    set calEvents to (every event of cal whose start date ≥ startDate and start date < endDate)
                    repeat with evt in calEvents
                        set eventInfo to (summary of evt) & "|" & (start date of evt as string) & "|" & (end date of evt as string)
                        set eventsList to eventsList & eventInfo & "||"
                    end repeat
                end repeat
                return eventsList
            end tell
            '''
            
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                return self._parse_events(result.stdout.strip())
            return f"No events in the next {days} days."
            
        except Exception as e:
            return f"Could not access calendar: {str(e)}"
    
    def _parse_events(self, events_string):
        """Parse events from AppleScript output"""
        events = events_string.split("||")
        formatted_events = []
        
        for event in events:
            if event.strip():
                parts = event.split("|")
                if len(parts) >= 3:
                    title = parts[0]
                    start = parts[1]
                    formatted_events.append(f"• {title} at {start}")
        
        if formatted_events:
            return "\n".join(formatted_events)
        return "No events found."
    
    def add_event(self, title, date_string, duration_minutes=60):
        """Add event to calendar"""
        try:
            # Parse the date string
            event_date = parser.parse(date_string, fuzzy=True)
            end_date = event_date + timedelta(minutes=duration_minutes)
            
            # Format dates for AppleScript
            start_str = event_date.strftime("%m/%d/%Y %I:%M:%S %p")
            end_str = end_date.strftime("%m/%d/%Y %I:%M:%S %p")
            
            script = f'''
            tell application "Calendar"
                tell calendar "Calendar"
                    make new event with properties {{summary:"{title}", start date:date "{start_str}", end date:date "{end_str}"}}
                end tell
            end tell
            '''
            
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return f"Event '{title}' added on {event_date.strftime('%B %d at %I:%M %p')}"
            else:
                return f"Could not add event: {result.stderr}"
                
        except Exception as e:
            return f"Error adding event: {str(e)}"
    
    def parse_event_command(self, command):
        """Parse natural language event command"""
        # Examples: "add meeting tomorrow at 3pm"
        #           "schedule dentist appointment next monday 10am"
        
        command = command.lower()
        
        # Extract event title
        title_match = re.search(r'(?:add|schedule|create)\s+(.+?)\s+(?:tomorrow|today|on|at|next)', command)
        if title_match:
            title = title_match.group(1).strip()
        else:
            title = "New Event"
        
        # Extract date/time
        date_match = re.search(r'(tomorrow|today|next \w+|on \w+|\d+/\d+)\s*(?:at\s*)?(\d+(?::\d+)?\s*(?:am|pm)?)?', command)
        
        if date_match:
            date_part = date_match.group(1)
            time_part = date_match.group(2) or "12:00 PM"
            date_string = f"{date_part} {time_part}"
            
            return self.add_event(title, date_string)
        
        return "Could not understand the date/time. Try: 'schedule meeting tomorrow at 3pm'"