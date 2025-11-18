#!/bin/bash
# Clean animation removal without breaking JavaScript syntax

# 1. Remove only the CSS keyframes, not the entire style blocks
sed -i '/@keyframes fadeInDown/,/}/d' index.html
sed -i '/@keyframes fadeInUp/,/}/d' index.html  
sed -i '/@keyframes expandWidth/,/}/d' index.html
sed -i '/@keyframes pulse/,/}/d' index.html

# 2. Remove animation style attributes carefully
sed -i 's/style={{animation: [^}]*}}/style={{}}/g' index.html

# 3. Remove the animate-pulse-slow class
sed -i 's/animate-pulse-slow//g' index.html

# 4. Keep the structure intact
echo "✅ Clean animation removal complete"
