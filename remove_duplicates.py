#!/usr/bin/env python3

def remove_duplicates():
    # Read the original file
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by the duplicate marker
    parts = content.split('# Route to setup database tables if they don\'t exist')
    
    # If we have more than 2 parts, it means we have duplicates
    if len(parts) > 2:
        # Keep only the first occurrence
        fixed_content = parts[0] + '# Route to setup database tables if they don\'t exist' + parts[1]
        # Add back the rest without duplicating the marker
        for i in range(2, len(parts)):
            # Check if this part starts with the route decorator
            if '@app.route("/setup_database")' in parts[i][:100]:
                # Skip this duplicate
                continue
            else:
                # Add this part
                fixed_content += parts[i]
        
        # Write the fixed file
        with open('app_fixed.py', 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print("Fixed file created as app_fixed.py")
    else:
        print("No duplicates found")
        # Just copy the file
        with open('app_fixed.py', 'w', encoding='utf-8') as f:
            f.write(content)

if __name__ == "__main__":
    remove_duplicates()