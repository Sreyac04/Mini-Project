#!/usr/bin/env python3

def remove_duplicate_routes():
    # Read the original file
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find the line numbers of the duplicate setup_database routes
    setup_database_lines = []
    debug_db_lines = []
    
    for i, line in enumerate(lines):
        if line.strip() == '# Route to setup database tables if they don\'t exist':
            if i+1 < len(lines) and lines[i+1].strip() == '@app.route("/setup_database")':
                setup_database_lines.append(i)
        elif line.strip() == '# Debug route to check database content':
            if i+1 < len(lines) and lines[i+1].strip() == '@app.route("/debug_db")':
                debug_db_lines.append(i)
    
    # Remove the second occurrence of each duplicate
    lines_to_remove = set()
    
    # Remove second setup_database route (if it exists)
    if len(setup_database_lines) > 1:
        # Find the end of the second setup_database function
        start = setup_database_lines[1]
        end = start
        # Look for the end of the function by finding the next route or end of file
        while end < len(lines):
            end += 1
            if end >= len(lines):
                break
            # Stop at the next route decorator or a new function comment
            if lines[end].strip().startswith('@app.route(') or \
               (lines[end].strip().startswith('#') and 'route' in lines[end].lower()) or \
               (lines[end].strip().startswith('def ') and end > start + 20):  # Assume functions are longer than 20 lines
                break
        
        # Mark lines for removal (from start to end-1)
        for i in range(start, end-1):
            lines_to_remove.add(i)
        print(f"Marking lines {start} to {end-1} for removal (setup_database)")
    
    # Remove second debug_db route (if it exists)
    if len(debug_db_lines) > 1:
        # Find the end of the second debug_db function
        start = debug_db_lines[1]
        end = start
        # Look for the end of the function by finding the next route or end of file
        while end < len(lines):
            end += 1
            if end >= len(lines):
                break
            # Stop at the next route decorator or a new function comment
            if lines[end].strip().startswith('@app.route(') or \
               (lines[end].strip().startswith('#') and 'route' in lines[end].lower()) or \
               (lines[end].strip().startswith('def ') and end > start + 20):  # Assume functions are longer than 20 lines
                break
        
        # Mark lines for removal (from start to end-1)
        for i in range(start, end-1):
            lines_to_remove.add(i)
        print(f"Marking lines {start} to {end-1} for removal (debug_db)")
    
    # Create new lines list without duplicates
    new_lines = []
    for i, line in enumerate(lines):
        if i not in lines_to_remove:
            new_lines.append(line)
    
    # Write the fixed file
    with open('app_fixed.py', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"Found {len(setup_database_lines)} setup_database routes")
    print(f"Found {len(debug_db_lines)} debug_db routes")
    print(f"Removed {len(lines_to_remove)} duplicate lines")
    print("Fixed file written to app_fixed.py")

if __name__ == "__main__":
    remove_duplicate_routes()